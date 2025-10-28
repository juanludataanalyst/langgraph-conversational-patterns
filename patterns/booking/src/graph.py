"""
Conversational graph for appointment bookings.

This graph models a typical booking conversation:
1. User expresses intent to book
2. Bot extracts information (service, date)
3. If information is missing → ask for it
4. If complete → check availability
5. Confirm the booking
6. Respond to the user

The flow is based on simple decisions about the conversation's state.
"""

from langgraph.graph import StateGraph, START, END
from src.patterns.booking.state import BookingState
from src.patterns.booking.nodes import BookingNodes

def create_booking_graph():
    """
    Creates the conversational booking graph.
    
    The graph follows a common pattern in booking conversations:
    - Incremental information gathering
    - Availability validation
    - Final confirmation
    """
    
    print("🏗️ Building booking graph...")
    
    # Initialize nodes
    nodes = BookingNodes()
    
    # Create the graph
    workflow = StateGraph(BookingState)
    
    # Add all nodes
    workflow.add_node("detect_intent", nodes.detect_intent_node)
    workflow.add_node("extract_booking_data", nodes.extract_booking_data_node)
    workflow.add_node("check_availability", nodes.check_availability_node)
    workflow.add_node("confirm_booking", nodes.confirm_booking_node)
    workflow.add_node("ask_for_information", nodes.ask_for_information_node)
    workflow.add_node("respond_user", nodes.respond_user_node)
    
    # =========================================================================
    # ROUTING FUNCTIONS - The heart of the conversational flow
    # =========================================================================
    
    def route_after_extraction(state: BookingState) -> str:
        """
        Decides the next step after extracting data.
        
        Logic:
        - If we have service + date → check availability (with or without time)
        - If service or date is missing → ask for it
        """
        booking_data = state.get("booking_data", {})
        has_service = bool(booking_data.get("service"))
        has_date = bool(booking_data.get("appointment_date"))
        has_time = bool(booking_data.get("appointment_time"))
        
        if has_service and has_date:
            print(f"📋 We have service + date → checking availability (time: {has_time})")
            return "check_availability"
        else:
            print(f"❓ Missing information (service: {has_service}, date: {has_date}) → asking")
            return "ask_for_information"
    
    def route_after_availability(state: BookingState) -> str:
        """
        Decides what to do after checking availability.
        
        Logic:
        - If we have time + user confirmed → finalize booking
        - Otherwise → respond to user (showing times or asking confirmation)
        """
        booking_data = state.get("booking_data", {})
        has_time = bool(booking_data.get("appointment_time"))
        user_confirmed = state.get("booking_confirmed", False)
        
        if has_time and user_confirmed:
            print("✅ Has time + user confirmed → finalizing booking")
            return "confirm_booking"
        else:
            print(f"📋 No final confirmation yet (time: {has_time}, confirmed: {user_confirmed}) → responding")
            return "respond_user"
    
    # =========================================================================
    # DEFINE THE GRAPH FLOW
    # =========================================================================
    
    # Main flow: START → detect_intent → extract_booking_data
    workflow.add_edge(START, "detect_intent")
    workflow.add_edge("detect_intent", "extract_booking_data")
    
    # Conditional routing after extracting data
    workflow.add_conditional_edges(
        "extract_booking_data",
        route_after_extraction,
        {
            "check_availability": "check_availability",
            "ask_for_information": "ask_for_information"
        }
    )
    
    # After checking availability, confirm or respond
    workflow.add_conditional_edges(
        "check_availability",
        route_after_availability,
        {
            "confirm_booking": "confirm_booking",
            "respond_user": "respond_user"
        }
    )
    
    # Both confirming and asking go to respond to the user
    workflow.add_edge("confirm_booking", "respond_user")
    workflow.add_edge("ask_for_information", "respond_user")
    
    # The flow ends after responding
    workflow.add_edge("respond_user", END)
    
    print("✅ Graph built successfully")
    return workflow.compile()

# =========================================================================
# CONFIGURATION FOR LANGGRAPH STUDIO
# =========================================================================

# This instance will be used by LangGraph Studio
app = create_booking_graph()

# Helper function for local testing
def test_booking_conversation():
    """
    Function to test the conversational flow locally.
    """
    from langchain_core.messages import HumanMessage
    
    # Initial state
    initial_state = {
        "messages": [HumanMessage(content="Hi, I want an appointment for a haircut tomorrow")],
        "intent": None,
        "booking_data": {},
        "booking_confirmed": False,
        "answer": None
    }
    
    print("🧪 Testing booking conversation...")
    result = app.invoke(initial_state)
    print("🎯 Final result:")
    print(f"Intent: {result.get('intent')}")
    booking_data = result.get('booking_data', {})
    print(f"Service: {booking_data.get('service')}")
    print(f"Date: {booking_data.get('appointment_date')}")
    print(f"Time: {booking_data.get('appointment_time')}")
    print(f"Confirmed: {result.get('booking_confirmed')}")
    
if __name__ == "__main__":
    test_booking_conversation()
