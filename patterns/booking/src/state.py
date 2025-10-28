from typing import TypedDict, Optional
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class BookingData(TypedDict, total=False):
    """Booking information structure."""
    service: Optional[str]           # Requested service (haircut, beard trim, styling)
    appointment_date: Optional[str]  # When they want the appointment (today, tomorrow, day after tomorrow)
    appointment_time: Optional[str]  # What time they want (9:00, 10:00, etc.)

class BookingState(TypedDict):
    """State for the booking conversation flow.
    
    Uses LangGraph's standard MessagesState pattern with additional booking data.
    """
    messages: Annotated[list[BaseMessage], add_messages]  # Standard LangGraph messages
    intent: Optional[str]        # Detected intent (book, modify, cancel, etc.)
    booking_data: BookingData    # Structured booking information
    booking_confirmed: bool      # Did user confirm the booking with "yes/perfect"?
    answer: Optional[str]        # Response text to be converted to AIMessage by respond_user
