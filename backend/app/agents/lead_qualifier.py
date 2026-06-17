import re
import time
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from app.models.lead import LeadIntent, LeadStage


class LeadState(TypedDict):
    messages: list
    phone: str
    name: str
    intent: Optional[str]
    score: Optional[float]
    stage: Optional[str]
    property_type: Optional[str]
    budget_min: Optional[float]
    budget_max: Optional[float]
    preferred_location: Optional[str]
    timeline: Optional[str]
    steps_taken: int
    start_time: float
    error: Optional[str]


# Deterministic scoring rules - NOT LLM-based
SCORING_RULES = {
    "intent": {
        LeadIntent.BUY.value: 30,
        LeadIntent.SITE_VISIT.value: 25,
        LeadIntent.RENT.value: 20,
        LeadIntent.PRICING_INQUIRY.value: 15,
        LeadIntent.OTHER.value: 5,
        LeadIntent.SPAM.value: 0,
    },
    "budget_present": 20,
    "location_present": 15,
    "timeline_present": 15,
    "property_type_present": 10,
    "name_present": 10,
}


def classify_and_extract(state: LeadState) -> dict:
    """Node 1: Classify intent and extract entities using keyword matching."""
    try:
        last_msg = state["messages"][-1].content if state["messages"] else ""
        text_lower = last_msg.lower()
        intent = LeadIntent.OTHER.value

        if any(w in text_lower for w in ["buy", "purchase", "खरीदना"]):
            intent = LeadIntent.BUY.value
        elif any(w in text_lower for w in ["rent", "lease", "किराया"]):
            intent = LeadIntent.RENT.value
        elif any(w in text_lower for w in ["visit", "site", "देखना", "मिलना"]):
            intent = LeadIntent.SITE_VISIT.value
        elif any(w in text_lower for w in ["price", "cost", "rate", "कीमत"]):
            intent = LeadIntent.PRICING_INQUIRY.value
        elif any(w in text_lower for w in ["spam", "test", "hello", "hi"]):
            intent = LeadIntent.SPAM.value

        updates = {
            "intent": intent,
            "stage": LeadStage.NEW.value,
            "steps_taken": state.get("steps_taken", 0) + 1,
        }

        # Extract budget
        budget_match = re.search(r'(\d+)\s*(?:lakh|cr|crore|k|million)', text_lower)
        if budget_match:
            val = float(budget_match.group(1))
            if "lakh" in text_lower or "k" in text_lower:
                updates["budget_max"] = val * 100000
            elif "cr" in text_lower or "crore" in text_lower:
                updates["budget_max"] = val * 10000000

        # Extract Mumbai location
        mumbai_areas = ["bandra", "andheri", "worli", "colaba", "powai", "juhu",
                        "dadar", "parel", "lower parel", "bkc", "navi mumbai",
                        "thane", "virar", "vasai"]
        for area in mumbai_areas:
            if area in text_lower:
                updates["preferred_location"] = area.title()
                break

        return updates

    except Exception as e:
        return {"error": f"Classification failed: {str(e)}"}


def score_lead(state: LeadState) -> dict:
    """Node 2: Deterministic scoring based on extracted data."""
    try:
        score = 0.0
        intent_score = SCORING_RULES["intent"].get(state.get("intent"), 0)
        score += intent_score

        if state.get("budget_min") or state.get("budget_max"):
            score += SCORING_RULES["budget_present"]
        if state.get("preferred_location"):
            score += SCORING_RULES["location_present"]
        if state.get("timeline"):
            score += SCORING_RULES["timeline_present"]
        if state.get("property_type"):
            score += SCORING_RULES["property_type_present"]
        if state.get("name") and state["name"] != "User":
            score += SCORING_RULES["name_present"]

        score = min(score, 100.0)

        stage = state.get("stage", LeadStage.NEW.value)
        if score >= 70:
            stage = LeadStage.QUALIFIED.value
        elif score >= 40:
            stage = LeadStage.INTERESTED.value

        return {"score": score, "stage": stage}

    except Exception as e:
        return {"error": f"Scoring failed: {str(e)}"}


def generate_response(state: LeadState) -> dict:
    """Node 3: Generate contextual WhatsApp reply."""
    try:
        intent = state.get("intent", "other")
        name = state.get("name", "User")

        responses = {
            LeadIntent.BUY.value: f"Hi {name}! Thanks for your interest in buying. We have premium properties in Mumbai. What's your preferred location and budget?",
            LeadIntent.RENT.value: f"Hi {name}! We have rental options across Mumbai. Which area are you looking at?",
            LeadIntent.SITE_VISIT.value: f"Hi {name}! Happy to arrange a site visit. When would be convenient for you?",
            LeadIntent.PRICING_INQUIRY.value: f"Hi {name}! Pricing varies by location and configuration. Could you share your preferred area?",
            LeadIntent.SPAM.value: "Thanks for reaching out! How can we help you with Mumbai real estate?",
            LeadIntent.OTHER.value: f"Hi {name}! I'm your VYUHLEADS assistant. Are you looking to buy, rent, or schedule a site visit?",
        }

        reply = responses.get(intent, responses[LeadIntent.OTHER.value])
        return {"messages": state["messages"] + [AIMessage(content=reply)]}

    except Exception as e:
        return {"error": f"Response generation failed: {str(e)}"}


def should_continue(state: LeadState) -> str:
    """Conditional edge: stop on error or max steps."""
    if state.get("error"):
        return "end"
    if state.get("steps_taken", 0) >= 3:
        return "end"
    return "continue"


def build_lead_qualifier():
    """Build and compile the lead qualification graph."""
    workflow = StateGraph(LeadState)

    workflow.add_node("classify", classify_and_extract)
    workflow.add_node("score", score_lead)
    workflow.add_node("respond", generate_response)

    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "score")
    workflow.add_conditional_edges(
        "score",
        should_continue,
        {"continue": "respond", "end": END}
    )
    workflow.add_edge("respond", END)

    return workflow.compile()
