from typing import TypedDict, Optional, List, Dict, Any
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class ExistingAppointment(TypedDict, total=False):
    """Existing appointment information."""
    appointment_id: str                 # "APT-001", "APT-002", etc.
    service: str                        # "haircut", "beard trim", "styling"
    date: str                           # "2024-01-15"
    time: str                           # "10:00"
    customer_name: str                  # "Juan Luis"
    status: str                         # "confirmed", "cancelled", "modified"

class ModificationRequest(TypedDict, total=False):
    """Requested changes to appointment."""
    modification_type: str              # "cancel", "reschedule", "change_service"
    new_date: Optional[str]             # New date if changing
    new_time: Optional[str]             # New time if changing
    new_service: Optional[str]          # New service if changing
    reason: Optional[str]               # Reason for change

class AppointmentState(TypedDict):
    """State for appointment cancellation/modification flow.

    Inspired by aibarber pattern with clean step progression:
    identify_customer → lookup_appointments → process_modification → execute_action
    """
    messages: Annotated[List[BaseMessage], add_messages]  # Standard LangGraph messages

    # Customer identification (simplified - using name for demo)
    customer_name: Optional[str]                    # Customer identifier

    # Core intent and action
    intent: Optional[str]                           # "cancel", "modify", "reschedule"

    # Appointment lookup and selection
    found_appointments: List[ExistingAppointment]   # Found appointments
    selected_appointment: Optional[ExistingAppointment]  # Selected appointment

    # Modification data
    modification_request: Optional[ModificationRequest]  # Requested changes

    # Flow control (aibarber-style step tracking)
    current_step: Optional[str]                     # "identify", "lookup", "modify", "confirm"

    # Completion flags
    modification_completed: bool                    # Is the action completed?
    modification_confirmed: bool                    # Did user confirm the modification with "yes"?

    # Response handling
    answer: Optional[str]                           # Response text to be converted to AIMessage
