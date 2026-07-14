from langchain_core.tools import tool
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import re
from database import SessionLocal
import models

class SentimentEnum(str, Enum):
    Positive = "Positive"
    Neutral = "Neutral"
    Negative = "Negative"

class InteractionTypeEnum(str, Enum):
    Meeting = "Meeting"
    Video_Call = "Video Call"
    Email = "Email"
    Phone = "Phone"

class LogInteractionSchema(BaseModel):
    hcp_name: Optional[str] = Field(default=None, description="The name of the Healthcare Professional.")
    interaction_type: Optional[InteractionTypeEnum] = Field(default=None, description="The type of interaction. Map 'in person' to 'Meeting'.")
    date: Optional[str] = Field(default=None, description="The date of the interaction strictly in YYYY-MM-DD format.")
    time: Optional[str] = Field(default=None, description="The time of the interaction. Can be 12-hour or 24-hour format.")
    sentiment: Optional[SentimentEnum] = Field(default=None, description="The sentiment of the interaction.")
    topics_discussed: Optional[List[str]] = Field(default=None, description="List of topics discussed.")
    materials_shared: Optional[List[str]] = Field(default=None, description="List of materials shared.")
    key_outcomes: Optional[str] = Field(default=None, description="Description of agreements or results from the meeting.")
    follow_up_actions: Optional[str] = Field(default=None, description="Next steps, future meetings, or tasks to complete.")
    samples_distributed: Optional[List[str]] = Field(default=None, description="List of drug samples distributed to the HCP.")

    @field_validator("date")
    @classmethod
    def validate_date(cls, v):
        if not v:
            return v
        # Simple fallback parsing if LLM outputs MM/DD/YYYY
        if re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", v):
            try:
                dt = datetime.strptime(v, "%m/%d/%Y")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
        return v

    @field_validator("time")
    @classmethod
    def validate_time(cls, v):
        if not v:
            return v
        # Convert 12-hour format (e.g., "05:40 PM" or "5:40pm") to 24-hour HH:MM
        try:
            # Try parsing with various AM/PM formats
            v_upper = v.strip().upper()
            if "AM" in v_upper or "PM" in v_upper:
                # Add space if missing
                v_clean = re.sub(r'(?i)(\d)(AM|PM)', r'\1 \2', v_upper)
                dt = datetime.strptime(v_clean, "%I:%M %p")
                return dt.strftime("%H:%M")
        except ValueError:
            pass
        return v

@tool(args_schema=LogInteractionSchema)
def log_interaction(
    hcp_name: str = None, 
    interaction_type: InteractionTypeEnum = None,
    date: str = None, 
    time: str = None,
    sentiment: SentimentEnum = None, 
    topics_discussed: List[str] = None, 
    materials_shared: List[str] = None,
    key_outcomes: str = None,
    follow_up_actions: str = None,
    samples_distributed: List[str] = None
):
    """Processes the user's unstructured log text and maps the extracted data into the structured schema."""
    updates = {}
    if hcp_name is not None:
        updates["hcpName"] = hcp_name
    if interaction_type is not None:
        updates["interactionType"] = interaction_type
    if date is not None:
        updates["date"] = date
    if time is not None:
        updates["time"] = time
    if sentiment is not None:
        updates["sentiment"] = sentiment
    if topics_discussed:
        updates["topicsDiscussed"] = ", ".join(topics_discussed)
    if materials_shared:
        updates["materialsShared"] = ", ".join(materials_shared)
    if key_outcomes is not None:
        updates["keyOutcomes"] = key_outcomes
    if follow_up_actions is not None:
        updates["followUpActions"] = follow_up_actions
    if samples_distributed:
        updates["samplesDistributed"] = ", ".join(samples_distributed)
        
    return {"form_data": updates}

class EditInteractionSchema(BaseModel):
    hcp_name: Optional[str] = Field(None, description="The name of the Healthcare Professional.")
    interaction_type: Optional[InteractionTypeEnum] = Field(None, description="The type of interaction.")
    date: Optional[str] = Field(None, description="The date of the interaction strictly in YYYY-MM-DD format.")
    time: Optional[str] = Field(None, description="The time of the interaction. Can be 12-hour or 24-hour format.")
    sentiment: Optional[SentimentEnum] = Field(None, description="The sentiment of the interaction.")
    topics_discussed: Optional[List[str]] = Field(None, description="List of topics discussed.")
    materials_shared: Optional[List[str]] = Field(None, description="List of materials shared.")
    key_outcomes: Optional[str] = Field(None, description="Description of agreements or results from the meeting.")
    follow_up_actions: Optional[str] = Field(None, description="Next steps, future meetings, or tasks to complete.")
    samples_distributed: Optional[List[str]] = Field(None, description="List of drug samples distributed to the HCP.")

    @field_validator("date")
    @classmethod
    def validate_date(cls, v):
        if not v:
            return v
        if re.match(r"^\d{1,2}/\d{1,2}/\d{4}$", v):
            try:
                dt = datetime.strptime(v, "%m/%d/%Y")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
        return v

    @field_validator("time")
    @classmethod
    def validate_time(cls, v):
        if not v:
            return v
        try:
            v_upper = v.strip().upper()
            if "AM" in v_upper or "PM" in v_upper:
                v_clean = re.sub(r'(?i)(\d)(AM|PM)', r'\1 \2', v_upper)
                dt = datetime.strptime(v_clean, "%I:%M %p")
                return dt.strftime("%H:%M")
        except ValueError:
            pass
        return v

@tool(args_schema=EditInteractionSchema)
def edit_interaction(
    hcp_name: Optional[str] = None, 
    interaction_type: Optional[InteractionTypeEnum] = None,
    date: Optional[str] = None, 
    time: Optional[str] = None,
    sentiment: Optional[SentimentEnum] = None, 
    topics_discussed: Optional[List[str]] = None, 
    materials_shared: Optional[List[str]] = None,
    key_outcomes: Optional[str] = None,
    follow_up_actions: Optional[str] = None,
    samples_distributed: Optional[List[str]] = None
):
    """Applies a partial patch operation to the existing interaction form data state."""
    updates = {}
    if hcp_name is not None:
        updates["hcpName"] = hcp_name
    if interaction_type is not None:
        updates["interactionType"] = interaction_type
    if date is not None:
        updates["date"] = date
    if time is not None:
        updates["time"] = time
    if sentiment is not None:
        updates["sentiment"] = sentiment
    if topics_discussed:
        updates["topicsDiscussed"] = ", ".join(topics_discussed)
    if materials_shared:
        updates["materialsShared"] = ", ".join(materials_shared)
    if key_outcomes is not None:
        updates["keyOutcomes"] = key_outcomes
    if follow_up_actions is not None:
        updates["followUpActions"] = follow_up_actions
    if samples_distributed:
        updates["samplesDistributed"] = ", ".join(samples_distributed)
        
    return {"form_data": updates}

class SearchHCPDirectorySchema(BaseModel):
    search_query: str = Field(description="The name or specialty to search for in the HCP directory.")

@tool(args_schema=SearchHCPDirectorySchema)
def search_hcp_directory(search_query: str):
    """Queries the HCP directory to find matching Healthcare Professionals."""
    db = SessionLocal()
    try:
        results = db.query(models.HCP).filter(
            models.HCP.name.ilike(f"%{search_query}%") | models.HCP.specialty.ilike(f"%{search_query}%")
        ).all()
        
        if not results:
            return "No HCP found matching query. They may not be in our directory yet."
            
        return [
            {
                "id": hcp.id,
                "name": hcp.name,
                "specialty": hcp.specialty,
            } for hcp in results
        ]
    except Exception as e:
        return f"Database query failed: {str(e)}"
    finally:
        db.close()

class VerifyMaterialsSchema(BaseModel):
    materials_list: List[str] = Field(description="List of materials to verify compliance for.")

@tool(args_schema=VerifyMaterialsSchema)
def verify_materials(materials_list: List[str]):
    """Cross-references material names against an approved medical compliance database."""
    results = {}
    for mat in materials_list:
        if "unapproved" in mat.lower() or "draft" in mat.lower():
            results[mat] = "flagged_unapproved"
        else:
            results[mat] = "verified"
    return results

class GetInteractionHistorySchema(BaseModel):
    hcp_id: Optional[int] = Field(None, description="The ID of the HCP.")
    hcp_name: Optional[str] = Field(None, description="The name of the HCP.")

@tool(args_schema=GetInteractionHistorySchema)
def get_interaction_history(hcp_id: Optional[int] = None, hcp_name: Optional[str] = None):
    """Retrieves the last logged interactions for a specific HCP."""
    if not hcp_id and not hcp_name:
        return "Must provide either hcp_id or hcp_name."
        
    db = SessionLocal()
    try:
        query = db.query(models.InteractionLog)
        if hcp_id:
            query = query.filter(models.InteractionLog.hcp_id == hcp_id)
        elif hcp_name:
            query = query.join(models.HCP).filter(models.HCP.name.ilike(f"%{hcp_name}%"))
            
        results = query.order_by(models.InteractionLog.date.desc()).limit(3).all()
        
        if not results:
            return f"No prior interaction history found for this HCP."
            
        history = []
        for log in results:
            history.append(
                f"Date: {log.date}, Topics: {log.topics_discussed}, Sentiment: {log.sentiment}"
            )
        return "\n".join(history)
    except Exception as e:
        return f"Database query failed: {str(e)}"
    finally:
        db.close()

TOOLS_LIST = [log_interaction, edit_interaction, search_hcp_directory, verify_materials, get_interaction_history]

if __name__ == "__main__":
    print("Testing Tool Schemas...")
    # Schema Strictness Test
    try:
        # Pass missing parameters, expect Pydantic defaults instead of exception
        res = log_interaction.invoke({"hcp_name": "Dr. Smith"})
        print("Schema Strictness Check Passed:", res)
    except Exception as e:
        print("Schema Strictness Check Failed:", str(e))
        
    # Database Fallback Test
    try:
        res = search_hcp_directory.invoke({"search_query": "Dr. Unknown"})
        print("Database Fallback Check Passed:", res)
    except Exception as e:
        print("Database Fallback Check Failed:", str(e))
