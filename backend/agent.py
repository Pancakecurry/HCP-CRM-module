import os
import json
from typing import TypedDict, Annotated, List, Dict, Any
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from tools import TOOLS_LIST, log_interaction, edit_interaction, search_hcp_directory, verify_materials, get_interaction_history

load_dotenv()

def update_dict(left: dict, right: dict) -> dict:
    if left is None:
        left = {}
    if right is None:
        return left
    return {**left, **right}

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    form_data: Annotated[dict, update_dict]
    validation_errors: Annotated[dict, update_dict]

primary_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    streaming=True,
    api_key=os.environ.get("GROQ_API_KEY", "mock_key")
)

fallback_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    streaming=True,
    api_key=os.environ.get("GROQ_API_KEY", "mock_key")
)

llm = primary_llm.with_fallbacks([fallback_llm])
llm_with_tools = llm.bind_tools(TOOLS_LIST)

from datetime import datetime

def get_system_prompt():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""You are an expert AI assistant for a Life Sciences CRM. 
Your job is to chat with pharmaceutical sales reps and help them log their interactions with Healthcare Professionals (HCPs).
You have access to tools to search the directory, verify materials compliance, and update the interaction form.
Extract information from their messages and use `log_interaction` or `edit_interaction` to populate the form.
You must ALWAYS execute the `log_interaction` tool when logging a new meeting. Do not just summarize the text to the user; you must push the data to the system using the tool.

CRITICAL: If the user provides new information, corrections, or missing fields (such as time, date, or materials) for a previously logged interaction, you MUST invoke the `edit_interaction` tool to update the system. NEVER verbally acknowledge an update without successfully executing the `edit_interaction` tool first.

If the user mentions next steps, scheduling another meeting, or sending a document later, map that to `follow_up_actions`. 
If they mention agreements or conclusions, map that to `key_outcomes`.
If the user mentions giving or leaving medication samples with the HCP, map that to `samples_distributed`.

Always be polite, concise, and confirm what you have extracted. If you need more information to complete a required field, ask for it.

CURRENT SERVER TIME: {current_time}
Relative temporal terms like "today", "yesterday", or "tomorrow" MUST be resolved to absolute dates based on the CURRENT SERVER TIME.
"""

from langchain_groq import ChatGroq

import os
from dotenv import load_dotenv
load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    raise Exception("GROQ_API_KEY not found in environment variables.")

# Using llama-3.3-70b-versatile for complex orchestration
primary_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

from tools import TOOLS_LIST

llm_with_tools = primary_llm.bind_tools(TOOLS_LIST)

def agent_node(state: AgentState):
    """The main reasoning engine. Invokes LLM with tools."""
    messages = state["messages"]
    
    # Prepend the dynamic system prompt
    sys_msg = SystemMessage(content=get_system_prompt())
    messages_with_sys = [sys_msg] + messages
    
    response = llm_with_tools.invoke(messages_with_sys)
    return {"messages": [response]}

def tool_execution_node(state: AgentState):
    """Executes the tool calls requested by the LLM and merges the results."""
    last_message = state["messages"][-1]
    
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return {}
        
    tool_messages = []
    form_data_updates = {}
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # Find the tool
        tool_instance = next((t for t in TOOLS_LIST if t.name == tool_name), None)
        if not tool_instance:
            tool_messages.append(ToolMessage(
                content=f"Error: Tool {tool_name} not found.",
                tool_call_id=tool_call["id"],
                name=tool_name
            ))
            continue
            
        try:
            # Execute tool
            result = tool_instance.invoke(tool_args)
            
            # If the tool returned form_data, extract it and merge
            if isinstance(result, dict) and "form_data" in result:
                form_data_updates.update(result["form_data"])
                tool_messages.append(ToolMessage(
                    content=f"Successfully updated form data with keys: {list(result['form_data'].keys())}",
                    tool_call_id=tool_call["id"],
                    name=tool_name
                ))
            else:
                tool_messages.append(ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                    name=tool_name
                ))
        except Exception as e:
            tool_messages.append(ToolMessage(
                content=f"Tool Execution Error: {str(e)}",
                tool_call_id=tool_call["id"],
                name=tool_name
            ))
            
    # Return both the tool execution confirmations AND the state patch
    return {
        "messages": tool_messages,
        "form_data": form_data_updates
    }

def should_continue(state: AgentState):
    """Router to determine if we need to execute a tool or end the turn."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tool_execution_node"
    return END

# Build the Graph
builder = StateGraph(AgentState)

builder.add_node("agent_node", agent_node)
builder.add_node("tool_execution_node", tool_execution_node)

builder.set_entry_point("agent_node")
builder.add_conditional_edges(
    "agent_node",
    should_continue,
    {
        "tool_execution_node": "tool_execution_node",
        END: END
    }
)
builder.add_edge("tool_execution_node", "agent_node")

# Memory
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

if __name__ == "__main__":
    import asyncio
    import json
    
    async def run_test():
        print("Running Async Graph Setup Check...")
        config = {"configurable": {"thread_id": "test_seq_1"}}
        
        async for event in graph.astream_events({"messages": [("user", "hi")]}, config=config, version="v2"):
            pass
        print("Async Agent check passed.")
        
        print("\nRunning 2-Turn Feature Simulation...")
        config = {"configurable": {"thread_id": "test_seq_5"}}
        
        # Turn 1
        prompt1 = "Met Dr. Smith. Left 10 units of DrugX samples."
        print(f"Turn 1 User: {prompt1}")
        async for event in graph.astream_events({"messages": [("user", prompt1)]}, config=config, version="v2"):
            pass
            
        state = graph.get_state(config)
        form_data = state.values.get("form_data", {})
        
        print("\nTurn 1 Extracted Payload:")
        print(json.dumps(form_data, indent=2))
        
        assert form_data.get("hcpName") == "Dr. Smith"
        assert form_data.get("samplesDistributed") is not None
        
        # Turn 2
        prompt2 = "Wait, I also left 5 units of DrugY."
        print(f"\nTurn 2 User: {prompt2}")
        
        tool_triggered = False
        async for event in graph.astream_events({"messages": [("user", prompt2)]}, config=config, version="v2"):
            if event["event"] == "on_chain_end" and event.get("name") == "tool_execution_node":
                tool_triggered = True
                print("Tool Execution Triggered on Turn 2!")
                
        state = graph.get_state(config)
        form_data2 = state.values.get("form_data", {})
        
        print("\nTurn 2 Final State Extracted Payload:")
        print(json.dumps(form_data2, indent=2))
        
        assert "DrugY" in form_data2.get("samplesDistributed")
        assert tool_triggered == True, "edit_interaction tool was not invoked!"
        
        print("\nAll assertions passed! Multi-Turn Sequence Simulation Completed.")
        
    asyncio.run(run_test())
