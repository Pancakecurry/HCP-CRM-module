# AI-First CRM HCP Module

Welcome to the AI-First CRM Healthcare Professional (HCP) Module. This project introduces a paradigm shift in data entry: instead of manually filling out tedious forms after a meeting, pharmaceutical sales reps simply chat with an AI Assistant. The AI automatically parses the conversation, structures the data, checks compliance, and populates the CRM in real-time.

**The Golden Rule**: The left-hand form is strictly **read-only**. The user cannot type into it. All state mutations must be orchestrated by the AI Assistant on the right.

## Architecture & Tech Stack

This module employs a sophisticated modern architecture to deliver real-time AI capabilities:

- **Frontend**: React, Redux Toolkit, Tailwind CSS, Vite.
  - *Streaming Engine*: Uses native `fetch` with `ReadableStream` to consume Server-Sent Events (SSE).
  - *State Management*: Redux cleanly splits conversational streaming tokens from structural form patches.
- **Backend**: FastAPI, Python 3.10+, SQLAlchemy (SQLite default).
  - *LLM Engine*: LangGraph and LangChain Core.
  - *Models*: Powered by Groq Cloud. Primary model is `llama-3.3-70b-versatile` for lightning-fast tool extraction.

### How it works:
1. The user sends a chat message via the React UI.
2. The FastAPI backend receives the message and executes a cyclic LangGraph loop (`agent_node` -> `tool_execution_node`).
3. If the LLM determines it needs to update the form, it emits a structured JSON tool call.
4. LangGraph executes the custom Python tool, validating the data against a strict Pydantic v2 schema.
5. The backend streams two types of SSE events to the frontend:
   - `text_delta`: Renders the AI's prose token-by-token in the chat panel.
   - `ui_state_patch`: Emits a JSON slice of the updated form data immediately upon tool completion, triggering Redux to visibly update the locked form fields.

## The 5 Custom AI Tools

The agent is equipped with five specialized tools to accomplish its work:

1. **`log_interaction`**: Extracts standard form fields (Name, Date, Sentiment, Topics, Materials). Used to initialize or overwrite the UI state.
2. **`edit_interaction`**: A partial-patch variant. All fields are marked as optional so the LLM can fix a single field (like fixing a typo in the sentiment) without resetting the rest of the form.
3. **`search_hcp_directory`**: Queries the backend SQL database to find matching HCPs by name or specialty, gracefully returning text to the LLM if they are not found.
4. **`verify_materials`**: Mocks a medical compliance database. Cross-references marketing materials to ensure they are `verified` and not `flagged_unapproved`.
5. **`get_interaction_history`**: Queries the `InteractionLog` database to fetch the last 3 interactions for a specific HCP, providing the agent with conversation context.

---

## Local Setup Instructions

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- A valid [Groq API Key](https://console.groq.com/keys)

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/hcp-crm-module.git](https://github.com/yourusername/hcp-crm-module.git)
cd hcp-crm-module

### 2. Backend Setup

Open a terminal and navigate to the backend directory:
```bash
cd backend
```

Create a virtual environment and install the dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy pydantic langchain-core langchain-groq langgraph python-dotenv
```

Configure your environment variables:
Create a `.env` file inside the `backend/` directory:
```bash
touch .env
```
Add your Groq API key to `.env`:
```env
GROQ_API_KEY=gsk_your_api_key_here
```

Start the FastAPI streaming server:
```bash
uvicorn main:app --reload
```
*The backend will now be running on `http://localhost:8000`.*

### 3. Frontend Setup

Open a **new** terminal and navigate to the frontend directory:
```bash
cd frontend
```

Install the required Node dependencies:
```bash
npm install
```

Start the Vite development server:
```bash
npm run dev
```

### 4. Usage
Open the provided local URL (typically `http://localhost:5173`) in your web browser. 

Try testing the AI:
> *"I met with Dr. Smith today in person. We discussed the new clinical trial data. It went very well!"*

Watch as the AI streams its response and the locked form populates automatically!

