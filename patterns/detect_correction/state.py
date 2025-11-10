"""
State definition for the Detect Correction pattern.

Educational pattern following aibarber's structure but with food orders domain.
Demonstrates correction detection with regex patterns (no LLM needed).
"""

from typing import TypedDict, Optional, List, Dict, Any
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class DetectCorrectionState(TypedDict):
    """
    State for the Detect Correction conversational pattern.

    Follows aibarber's structure: detect_correction → detect_intent → process_intent → respond_user
    Uses food orders as educational domain with regex-based detection.

    Attributes:
        messages: The list of messages in the conversation.
        correction_detected: Type of correction detected by detect_correction node.
        intent: User intent detected by detect_intent node.
        current_order: Current order data being built/modified.
        current_step: Current step in the conversation flow.
        answer: The response to be sent to the user.
    """
    messages: Annotated[List[BaseMessage], add_messages]

    # Correction detection (from detect_correction node)
    correction_detected: Optional[str]  # "correction_dish", "correction_size", "rejection", None

    # Intent detection (from detect_intent node)
    intent: Optional[str]  # "order", "cancel", "modify", "faq", "finish"

    # Order processing (from process_intent node)
    current_order: Optional[Dict[str, Any]]  # {"dish": "pizza", "size": "large", "extras": ["cheese"]}

    # Flow control (like aibarber/appointment_management)
    current_step: Optional[str]  # "awaiting_size", "awaiting_dish", "completed", None

    # Response handling (for respond_user node)
    answer: Optional[str]  # Response text to be converted to AIMessage
