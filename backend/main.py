from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
from database import SessionLocal, engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI-First CRM HCP Module")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev only. Update in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI-First CRM API"}

@app.post("/hcps/", response_model=schemas.HCP)
def create_hcp(hcp: schemas.HCPCreate, db: Session = Depends(get_db)):
    db_hcp = models.HCP(**hcp.model_dump())
    db.add(db_hcp)
    db.commit()
    db.refresh(db_hcp)
    return db_hcp

@app.get("/hcps/", response_model=List[schemas.HCP])
def read_hcps(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    hcps = db.query(models.HCP).offset(skip).limit(limit).all()
    return hcps

@app.post("/interactions/", response_model=schemas.InteractionLog)
def create_interaction(interaction: schemas.InteractionLogCreate, db: Session = Depends(get_db)):
    db_interaction = models.InteractionLog(**interaction.model_dump())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

import json
from fastapi.responses import StreamingResponse
from agent import graph

@app.post("/api/chat/stream")
async def chat_endpoint_stream(request: schemas.ChatRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    inputs = {"messages": [("user", request.message)]}
    
    async def event_generator():
        try:
            async for event in graph.astream_events(inputs, config=config, version="v2"):
                kind = event["event"]
                
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if hasattr(chunk, "content") and chunk.content and isinstance(chunk.content, str):
                        payload = {"type": "text_delta", "content": chunk.content}
                        yield f"data: {json.dumps(payload)}\n\n"
                        
                elif kind == "on_chain_end":
                    name = event.get("name")
                    if name == "tool_execution_node":
                        outputs = event["data"].get("output", {})
                        if "form_data" in outputs and outputs["form_data"]:
                            payload = {"type": "ui_state_patch", "form_data": outputs["form_data"]}
                            yield f"data: {json.dumps(payload)}\n\n"

            yield f"data: {json.dumps({'type': 'end'})}\n\n"
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Graph Streaming Error:\n{error_details}")
            payload = {
                'type': 'error', 
                'content': f"Encountered a system error: {str(e)}"
            }
            yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/chat")

def chat_endpoint(request: schemas.ChatRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    
    # Check if there is existing state
    current_state = graph.get_state(config)
    
    # If starting fresh and we want to pass form_data, we could, but let's just append the message
    inputs = {"messages": [("user", request.message)]}
    
    # Stream or invoke
    try:
        # We invoke to get the final state after the graph completes its cycle
        result = graph.invoke(inputs, config=config)
        
        # Extract the last message content from the assistant
        last_message = result["messages"][-1].content
        
        return {
            "message": last_message,
            "form_data": result.get("form_data", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

