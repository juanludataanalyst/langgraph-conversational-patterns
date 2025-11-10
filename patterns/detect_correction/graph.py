"""
Conversational graph for the Detect Correction pattern.

Educational pattern following aibarber's structure:
START → detect_correction → detect_intent → process_intent → respond_user → END

This demonstrates the "Correction-First" pattern where correction detection
influences how intent is interpreted and processed.
"""

from langgraph.graph import StateGraph, START, END
from patterns.detect_correction.state import DetectCorrectionState
from patterns.detect_correction.nodes import DetectCorrectionNodes

def create_detect_correction_graph():
    """
    Creates the conversational graph for the Detect Correction pattern.

    Flow (optimized for rejection handling):
    - Normal flow: START → detect_correction → detect_intent → process_intent → respond_user → END
    - Rejection:   START → detect_correction → respond_user → END (early exit)

    Key pattern: Corrections are detected FIRST and influence intent detection.
    """
    print("🏗️ Building Detect Correction graph...")

    # Initialize nodes
    nodes = DetectCorrectionNodes()

    # Create the graph
    workflow = StateGraph(DetectCorrectionState)

    # Add nodes following aibarber structure
    workflow.add_node("detect_correction", nodes.detect_correction_node)
    workflow.add_node("detect_intent", nodes.detect_intent_node)
    workflow.add_node("process_intent", nodes.process_intent_node)
    workflow.add_node("respond_user", nodes.respond_user_node)

    # =========================================================================
    # ROUTING FUNCTIONS - Following aibarber's conditional routing pattern
    # =========================================================================

    def route_after_correction(state: DetectCorrectionState) -> str:
        """
        Route after correction detection.
        
        - If rejection detected → go directly to respond_user (no need for intent detection)
        - Otherwise → proceed to intent detection
        """
        correction_detected = state.get("correction_detected")
        print(f"🔀 Routing after correction detection: {correction_detected}")
        
        if correction_detected == "rejection":
            print("🚫 Rejection detected → direct to respond_user")
            return "respond_user"
        else:
            print("➡️ Normal/correction flow → detect_intent")
            return "detect_intent"

    # NOTE: Rejection is handled in detect_correction → respond_user (no route_after_intent needed)

    def route_after_processing(state: DetectCorrectionState) -> str:
        """
        Route after intent processing.
        
        Always respond to user after processing.
        """
        print("🔀 Routing after processing → respond_user")
        return "respond_user"

    # =========================================================================
    # DEFINE THE GRAPH FLOW - Following aibarber's structure
    # =========================================================================

    # 1. Start with correction detection (Correction-First pattern)
    workflow.add_edge(START, "detect_correction")

    # 2. After correction detection, route based on correction type
    workflow.add_conditional_edges(
        "detect_correction",
        route_after_correction,
        {
            "detect_intent": "detect_intent",
            "respond_user": "respond_user"  # For rejection cases
        }
    )

    # 3. After intent detection, always process the intent
    # (Rejection cases are already handled and routed to respond_user from detect_correction)
    workflow.add_edge("detect_intent", "process_intent")

    # 4. After processing intent, always respond
    workflow.add_conditional_edges(
        "process_intent",
        route_after_processing,
        {
            "respond_user": "respond_user"
        }
    )

    # 5. End after responding
    workflow.add_edge("respond_user", END)

    print("✅ Graph built successfully.")
    return workflow.compile()

# =========================================================================
# CONFIGURATION FOR LANGGRAPH STUDIO
# =========================================================================

# This instance will be used by LangGraph Studio
app = create_detect_correction_graph()

# =========================================================================
# LOCAL TESTING
# =========================================================================

def test_detect_correction_conversation():
    """
    Function to test the conversational flow locally.
    Tests correction detection in food ordering context.
    """
    from langchain_core.messages import HumanMessage

    print("\n🧪 Testing Detect Correction Pattern")
    print("=" * 50)

    # Test Case 1: Normal order (no correction)
    print("\n--- Test Case 1: Normal Order ---")
    state1 = {
        "messages": [HumanMessage(content="I want a large pizza")],
    }
    print(f"💬 User: '{state1['messages'][0].content}'")
    result1 = app.invoke(state1)
    print(f"🤖 Bot: '{result1['messages'][-1].content}'")
    print(f"📊 State: correction={result1.get('correction_detected')}, intent={result1.get('intent')}")

    # Test Case 2: Dish correction
    print("\n--- Test Case 2: Dish Correction ---")
    state2 = {
        "messages": [
            HumanMessage(content="I want a pizza"),
            HumanMessage(content="No, actually a burger"),
        ],
    }
    print(f"💬 User: '{state2['messages'][-1].content}'")
    result2 = app.invoke(state2)
    print(f"🤖 Bot: '{result2['messages'][-1].content}'")
    print(f"📊 State: correction={result2.get('correction_detected')}, intent={result2.get('intent')}")

    # Test Case 3: Size correction
    print("\n--- Test Case 3: Size Correction ---")
    state3 = {
        "messages": [
            HumanMessage(content="Medium pizza"),
            HumanMessage(content="Actually make it large"),
        ],
    }
    print(f"💬 User: '{state3['messages'][-1].content}'")
    result3 = app.invoke(state3)
    print(f"🤖 Bot: '{result3['messages'][-1].content}'")
    print(f"📊 State: correction={result3.get('correction_detected')}, intent={result3.get('intent')}")

    # Test Case 4: Complete rejection
    print("\n--- Test Case 4: Complete Rejection ---")
    state4 = {
        "messages": [
            HumanMessage(content="I want tacos"),
            HumanMessage(content="No thanks, never mind"),
        ],
    }
    print(f"💬 User: '{state4['messages'][-1].content}'")
    result4 = app.invoke(state4)
    print(f"🤖 Bot: '{result4['messages'][-1].content}'")
    print(f"📊 State: correction={result4.get('correction_detected')}, intent={result4.get('intent')}")

    # Test Case 5: FAQ intent
    print("\n--- Test Case 5: FAQ Intent ---")
    state5 = {
        "messages": [HumanMessage(content="How much does pizza cost?")],
    }
    print(f"💬 User: '{state5['messages'][0].content}'")
    result5 = app.invoke(state5)
    print(f"🤖 Bot: '{result5['messages'][-1].content}'")
    print(f"📊 State: correction={result5.get('correction_detected')}, intent={result5.get('intent')}")

if __name__ == "__main__":
    test_detect_correction_conversation()