"""
Appointment Management Graph - Cancel/Modify Pattern

Educational demonstration of appointment management flow inspired by aibarber.
Shows a common enterprise pattern for handling appointment modifications and cancellations.

Flow:
START → detect_intent → extract_customer_data → lookup_appointments → process_request → respond_user → END

This pattern demonstrates:
- Intent detection (cancel vs modify)
- Customer identification 
- Database lookup patterns
- Business logic routing
- Response handling
"""

from langgraph.graph import StateGraph, START, END
from patterns.modify_appointment.state import AppointmentState
from patterns.modify_appointment.nodes import AppointmentNodes

def create_appointment_graph():
    """
    Creates the appointment management graph.
    
    Educational pattern following the same structure as booking and onboarding.
    Shows how to handle appointment modifications in a conversational AI system.
    """
    
    print("🏗️ Building appointment management graph...")
    
    # Initialize nodes
    nodes = AppointmentNodes()
    
    # Create the graph
    workflow = StateGraph(AppointmentState)
    
    # Add all nodes following the simple pattern
    workflow.add_node("detect_intent", nodes.detect_intent_node)
    workflow.add_node("extract_customer_data", nodes.extract_customer_data_node)
    workflow.add_node("lookup_appointments", nodes.lookup_appointments_node)
    workflow.add_node("process_request", nodes.process_request_node)
    workflow.add_node("check_availability", nodes.check_availability_node)
    workflow.add_node("confirm_modification", nodes.confirm_modification_node)
    workflow.add_node("respond_user", nodes.respond_user_node)
    
    # =========================================================================
    # ROUTING FUNCTIONS - Simple educational routing
    # =========================================================================
    
    def route_after_intent(state: AppointmentState) -> str:
        """
        Route after intent detection.
        
        Simple logic: if we detected a valid intent, proceed to extract customer data.
        """
        intent = state.get("intent")
        if intent and intent != "unknown":
            print(f"✅ Valid intent detected: {intent}")
            return "extract_customer_data"
        else:
            print("❓ Unknown intent, asking for clarification")
            return "respond_user"
    
    def route_after_extraction(state: AppointmentState) -> str:
        """
        Route after customer data extraction.
        
        Enhanced logic: Handle confirmation flow and customer identification.
        """
        current_step = state.get("current_step")
        modification_confirmed = state.get("modification_confirmed", False)
        customer_name = state.get("customer_name")
        
        # FIRST: Handle confirmation flow (highest priority)
        if current_step == "awaiting_confirmation" and modification_confirmed:
            print("✅ Confirmation detected → going to confirm_modification")
            return "confirm_modification"
        elif current_step == "awaiting_confirmation":
            print("📋 Still awaiting confirmation → respond to user")
            return "respond_user"
        
        # SECOND: Handle customer identification
        if customer_name:
            print(f"✅ Customer identified: {customer_name}")
            return "lookup_appointments"
        else:
            print("❓ No customer name, asking for it")
            return "respond_user"
    
    def route_after_lookup(state: AppointmentState) -> str:
        """
        Route after appointment lookup.
        
        Always process the request after lookup.
        """
        print("📋 Appointments looked up, processing request")
        return "process_request"
    
    def route_after_processing(state: AppointmentState) -> str:
        """
        Route after processing request.
        
        Check if we need to check availability, confirm modification, wait for selection, or respond to user.
        """
        current_step = state.get("current_step")
        if current_step == "checking_availability":
            print("🕐 Need to check availability")
            return "check_availability"
        # awaiting_confirmation is handled by check_availability, not here
        elif current_step == "awaiting_selection":
            print("⏳ Waiting for appointment selection")
            return "respond_user"
        elif current_step == "completed":
            print("✅ Request completed, responding to user")
            return "respond_user"
        else:
            print("⚙️ Request processed, responding to user")
            return "respond_user"
    
    def route_after_availability(state: AppointmentState) -> str:
        """
        Route after checking availability.
        
        Following booking pattern: if awaiting confirmation AND user confirmed → go to confirm_modification
        Otherwise → respond_user
        """
        current_step = state.get("current_step")
        modification_confirmed = state.get("modification_confirmed", False)
        
        if current_step == "awaiting_confirmation" and modification_confirmed:
            print("✅ User confirmed modification → finalizing")
            return "confirm_modification"
        else:
            print("📋 Availability checked, responding to user")
            return "respond_user"
    
    # =========================================================================
    # DEFINE THE GRAPH FLOW - Simple linear flow with conditional routing
    # =========================================================================
    
    # Main flow: START → detect_intent
    workflow.add_edge(START, "detect_intent")
    
    # Conditional routing after intent detection
    workflow.add_conditional_edges(
        "detect_intent",
        route_after_intent,
        {
            "extract_customer_data": "extract_customer_data",
            "respond_user": "respond_user"
        }
    )
    
    # Conditional routing after customer extraction
    workflow.add_conditional_edges(
        "extract_customer_data", 
        route_after_extraction,
        {
            "lookup_appointments": "lookup_appointments",
            "confirm_modification": "confirm_modification",
            "respond_user": "respond_user"
        }
    )
    
    # Simple routing after lookup
    workflow.add_conditional_edges(
        "lookup_appointments",
        route_after_lookup,
        {
            "process_request": "process_request"
        }
    )
    
    # Routing after processing - can go to check_availability or respond_user
    workflow.add_conditional_edges(
        "process_request",
        route_after_processing,
        {
            "check_availability": "check_availability",
            "respond_user": "respond_user"
        }
    )
    
    # Routing after availability check - can go to confirm_modification or respond_user
    workflow.add_conditional_edges(
        "check_availability",
        route_after_availability,
        {
            "confirm_modification": "confirm_modification",
            "respond_user": "respond_user"
        }
    )
    
    # After confirming modification, always respond to user
    workflow.add_edge("confirm_modification", "respond_user")
    
    # End after responding
    workflow.add_edge("respond_user", END)
    
    print("✅ Appointment management graph built successfully")
    return workflow.compile()

# =========================================================================
# CONFIGURATION FOR LANGGRAPH STUDIO
# =========================================================================

# This instance will be used by LangGraph Studio
app = create_appointment_graph()

# Helper function for local testing
def test_appointment_conversation():
    """
    Function to test the appointment management flow locally.
    """
    from langchain_core.messages import HumanMessage
    
    # Test cancellation flow
    initial_state = {
        "messages": [HumanMessage(content="Hi, I'm Juan Luis and I want to cancel my appointment")],
        "customer_name": None,
        "intent": None,
        "found_appointments": [],
        "selected_appointment": None,
        "modification_request": None,
        "current_step": None,
        "modification_completed": False,
        "modification_confirmed": False,
        "answer": None
    }
    
    print("🧪 Testing appointment management conversation...")
    result = app.invoke(initial_state)
    print("🎯 Final result:")
    print(f"Intent: {result.get('intent')}")
    print(f"Customer: {result.get('customer_name')}")
    print(f"Found appointments: {len(result.get('found_appointments', []))}")
    print(f"Completed: {result.get('modification_completed')}")
    
if __name__ == "__main__":
    test_appointment_conversation()