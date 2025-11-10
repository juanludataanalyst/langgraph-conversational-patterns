"""
Nodes for the Detect Correction pattern.

Educational pattern following aibarber's structure:
- detect_correction: Detects user corrections with regex patterns
- detect_intent: Determines user intent (modified by corrections)  
- process_intent: Processes the specific intent (order, cancel, etc.)
- respond_user: Sends response to user

Uses food orders domain with regex-based detection (no LLM needed).
"""

import re
from langchain_core.messages import AIMessage
from patterns.detect_correction.state import DetectCorrectionState

class DetectCorrectionNodes:
    """
    Nodes for the Detect Correction conversational flow.
    
    Follows aibarber pattern: correction detection influences intent detection.
    """

    def __init__(self):
        """Initialize patterns for correction and intent detection."""
        
        # Correction patterns (English)
        self.correction_patterns = {
            "correction_dish": [
                r"\b(no,?\s*|wait,?\s*|actually,?\s*)(i\s+want|i\s+prefer|better)\s+(pizza|burger|taco|salad)",
                r"\b(actually|i\s+mean)\s+(a|an)?\s*(pizza|burger|taco|salad)",
                r"\b(change\s+to|i\s+prefer)\s+(a|an)?\s*(pizza|burger|taco|salad)",
                r"\b(no,?\s*better)\s+(a|an)?\s*(pizza|burger|taco|salad)"
            ],
            "correction_size": [
                r"\b(no,?\s*)(large|medium|small)",
                r"\b(better|actually)\s+(large|medium|small)",
                r"\b(make\s+it)\s+(large|medium|small)",
                r"\b(i\s+prefer)\s+(large|medium|small)"
            ],
            "rejection": [
                r"\b(no,?\s*thanks|no\s+thank\s+you|cancel\s+everything)",
                r"\b(never\s+mind|forget\s+it|i\s+changed\s+my\s+mind)",
                r"\b(not\s+interested|no\s+longer)"
            ]
        }
        
        # Intent patterns
        self.intent_patterns = {
            "order": [
                r"\b(i\s+want|i\s+need|i'd\s+like)\s+(.+)",
                r"\b(a|an)\s+(pizza|burger|taco|salad)",
                r"\b(pizza|burger|taco|salad|chicken|beef)",
                r"\b(order|ordering)"
            ],
            "finish": [
                r"\b(no,?\s*that's\s+all|that's\s+it|i'm\s+done)",
                r"\b(nothing\s+else|that's\s+everything)"
            ],
            "cancel": [
                r"\b(cancel|canceling)",
                r"\b(i\s+don't\s+want\s+the\s+order)",
                r"\b(remove\s+everything)"
            ],
            "modify": [
                r"\b(modify|change|update)",
                r"\b(update\s+the\s+order)",
                r"\b(remove|add)\s+(.+)"
            ],
            "faq": [
                r"\b(how\s+much|price|cost)",
                r"\b(delivery\s+time|when\s+will\s+it\s+arrive)",
                r"\b(ingredients|what's\s+in)"
            ]
        }

        # Food items for order processing
        self.dishes = {
            "pizza": ["pizza", "pizzas"],
            "burger": ["burger", "hamburger", "cheeseburger"],
            "taco": ["taco", "tacos"],
            "salad": ["salad", "salads"]
        }
        
        self.sizes = {
            "small": ["small", "little", "mini", "smaller"],
            "medium": ["medium", "regular", "normal"],
            "large": ["large", "big", "xl", "larger", "bigger"]
        }

    def detect_correction_node(self, state: DetectCorrectionState) -> DetectCorrectionState:
        """
        Detects if the user is correcting a previous statement or rejecting the flow.
        
        Following aibarber pattern: this runs FIRST and influences intent detection.
        Uses regex patterns for educational purposes (no LLM needed).
        """
        print("🔍 Detecting correction...")
        
        if not state["messages"]:
            return {**state}
        
        last_message = self._get_message_content(state["messages"][-1]).lower()
        print(f"📝 Analyzing message: '{last_message}'")
        
        correction_detected = None
        
        # Check for corrections in priority order
        for correction_type, patterns in self.correction_patterns.items():
            for pattern in patterns:
                if re.search(pattern, last_message, re.IGNORECASE):
                    correction_detected = correction_type
                    print(f"✅ {correction_type} detected with pattern: {pattern}")
                    break
            if correction_detected:
                break
        
        if not correction_detected:
            print("➡️ No correction detected")
        
        # If rejection detected, set the farewell message directly
        if correction_detected == "rejection":
            return {
                **state,
                "correction_detected": correction_detected,
                "answer": "No problem. Have a great day!"
            }
        
        return {
            **state,
            "correction_detected": correction_detected
        }

    def detect_intent_node(self, state: DetectCorrectionState) -> DetectCorrectionState:
        """
        Detects user intent, modified by any correction detected previously.

        Following aibarber pattern: correction_detected influences how intent is determined.
        NOTE: Rejection is handled in detect_correction_node and routed directly to respond_user.
        """
        print("🎯 Detecting intent...")

        correction_detected = state.get("correction_detected")

        if not state["messages"]:
            return {**state}
        
        last_message = self._get_message_content(state["messages"][-1]).lower()
        
        # If correction detected, prioritize order intent
        if correction_detected in ["correction_dish", "correction_size"]:
            print(f"🔄 Correction detected ({correction_detected}), prioritizing order intent")
            detected_intent = "order"
        else:
            # Normal intent detection with priority order
            # Check specific intents first (finish, modify, cancel, faq) before general "order"
            intent_priority = ["finish", "modify", "cancel", "faq", "order"]
            
            detected_intent = None
            for intent in intent_priority:
                patterns = self.intent_patterns[intent]
                for pattern in patterns:
                    if re.search(pattern, last_message, re.IGNORECASE):
                        detected_intent = intent
                        break
                if detected_intent:
                    break
            
            if not detected_intent:
                # Check if it's a simple size/dish response in conversation context
                current_order = state.get("current_order", {})
                
                # If we have an incomplete order and user gives size/dish, treat as order continuation
                if current_order and (
                    any(size_word in last_message for size_list in self.sizes.values() for size_word in size_list) or
                    any(dish_word in last_message for dish_list in self.dishes.values() for dish_word in dish_list)
                ):
                    print(f"🔄 Continuing order context with: {last_message}")
                    detected_intent = "order"
                else:
                    detected_intent = "unknown"
        
        print(f"✅ Intent detected: {detected_intent}")
        
        return {
            **state,
            "intent": detected_intent
        }

    def process_intent_node(self, state: DetectCorrectionState) -> DetectCorrectionState:
        """
        Processes the specific intent, applying any corrections detected.
        
        Following aibarber pattern: this is where business logic happens.
        """
        print("⚙️ Processing intent...")
        
        intent = state.get("intent")
        correction_detected = state.get("correction_detected")
        
        if intent == "reject":
            # Already handled in detect_intent
            return {**state}
        
        elif intent == "order":
            return self._process_order_intent(state)
        
        elif intent == "cancel":
            return self._process_cancel_intent(state)
        
        elif intent == "modify":
            return self._process_modify_intent(state)
        
        elif intent == "faq":
            return self._process_faq_intent(state)
        
        elif intent == "finish":
            return self._process_finish_intent(state)
        
        else:
            return {
                **state,
                "answer": "I didn't understand your request. You can order food, cancel orders, or ask questions."
            }

    def _process_order_intent(self, state: DetectCorrectionState) -> DetectCorrectionState:
        """Process order intent with correction handling."""
        print("🍕 Processing order...")
        
        last_message = self._get_message_content(state["messages"][-1]).lower()
        correction_detected = state.get("correction_detected")
        current_order = state.get("current_order", {})
        
        # Extract dish and size from message
        detected_dish = None
        detected_size = None
        
        for dish, keywords in self.dishes.items():
            for keyword in keywords:
                if keyword in last_message:
                    detected_dish = dish
                    break
            if detected_dish:
                break
        
        for size, keywords in self.sizes.items():
            for keyword in keywords:
                if keyword in last_message:
                    detected_size = size
                    break
            if detected_size:
                break
        
        # Apply corrections or updates
        if correction_detected == "correction_dish" and detected_dish:
            current_order["dish"] = detected_dish
            answer = f"Perfect, changed to {detected_dish}. What size would you prefer? (small, medium, large)"
            current_step = "awaiting_size"
        elif correction_detected == "correction_size" and detected_size:
            current_order["size"] = detected_size
            # Preserve existing dish information
            existing_dish = current_order.get("dish", "")
            if existing_dish:
                answer = f"Perfect, changed to {detected_size} size. Your order: {detected_size} {existing_dish}. Anything else?"
                current_step = "completed"
            else:
                answer = f"Perfect, changed to {detected_size} size."
                current_step = "awaiting_dish"
        else:
            # Normal order processing (no corrections)
            if detected_dish:
                current_order["dish"] = detected_dish
            if detected_size:
                current_order["size"] = detected_size
            
            if detected_dish and detected_size:
                answer = f"Perfect, {detected_size} {detected_dish}. Anything else?"
                current_step = "completed"
            elif detected_dish:
                answer = f"Great, {detected_dish}. What size would you prefer? (small, medium, large)"
                current_step = "awaiting_size"
            elif detected_size:
                # Check if we already have a dish in current order
                existing_dish = current_order.get("dish")
                if existing_dish:
                    answer = f"Perfect, {detected_size} {existing_dish}. Anything else?"
                    current_step = "completed"
                else:
                    answer = f"Size {detected_size} selected. What dish would you like?"
                    current_step = "awaiting_dish"
            else:
                answer = "What would you like to order? We have pizza, burgers, tacos, and salads."
                current_step = None
        
        return {
            **state,
            "current_order": current_order,
            "current_step": current_step,
            "answer": answer
        }

    def _process_cancel_intent(self, state: DetectCorrectionState) -> DetectCorrectionState:
        """Process cancel intent."""
        return {
            **state,
            "current_order": {},
            "current_step": None,
            "answer": "Order canceled. Can I help you with anything else?"
        }

    def _process_modify_intent(self, state: DetectCorrectionState) -> DetectCorrectionState:
        """Process modify intent."""
        current_order = state.get("current_order", {})
        if current_order:
            dish = current_order.get("dish", "your order")
            size = current_order.get("size", "")
            answer = f"Your current order: {size} {dish}. What would you like to change?"
            current_step = "awaiting_modification"
        else:
            answer = "You don't have an active order to modify."
            current_step = None
        
        return {
            **state,
            "current_step": current_step,
            "answer": answer
        }

    def _process_faq_intent(self, state: DetectCorrectionState) -> DetectCorrectionState:
        """Process FAQ intent with context preservation."""
        last_message = self._get_message_content(state["messages"][-1]).lower()
        
        # Generate FAQ response
        if "price" in last_message or "cost" in last_message:
            faq_answer = "Pizza: $15-25, Burger: $12-18, Tacos: $8-12, Salad: $10-15"
        elif "delivery" in last_message or "time" in last_message:
            faq_answer = "Delivery time is 30-45 minutes."
        elif "ingredients" in last_message:
            faq_answer = "Which dish would you like to know the ingredients for?"
        else:
            faq_answer = "I can help you with prices, delivery times, and ingredients."
        
        # Check if we have a pending order context
        current_step = state.get("current_step")
        current_order = state.get("current_order", {})
        
        if current_step == "awaiting_size" and current_order.get("dish"):
            dish = current_order["dish"]
            answer = f"{faq_answer} You were ordering a {dish} - what size would you prefer? (small, medium, large)"
        elif current_step == "awaiting_dish" and current_order.get("size"):
            size = current_order["size"]
            answer = f"{faq_answer} You selected {size} size - what dish would you like?"
        else:
            answer = faq_answer
        
        return {
            **state,
            "answer": answer
            # Preserve current_step and current_order
        }

    def _process_finish_intent(self, state: DetectCorrectionState) -> DetectCorrectionState:
        """Process finish/completion intent."""
        current_order = state.get("current_order", {})
        if current_order:
            dish = current_order.get("dish", "")
            size = current_order.get("size", "")
            if dish and size:
                answer = f"Perfect! Your order: {size} {dish}. Total will be calculated at checkout. Thank you!"
            elif dish:
                answer = f"Great! Your {dish} order is confirmed. Thank you!"
            else:
                answer = "Order confirmed. Thank you!"
        else:
            answer = "Thank you for visiting! Have a great day!"
        
        return {
            **state,
            "current_order": {},  # Clear order after completion
            "current_step": None,  # Reset step after completion
            "answer": answer
        }

    def respond_user_node(self, state: DetectCorrectionState) -> DetectCorrectionState:
        """
        Converts the answer field to an AIMessage and adds it to the message history.
        
        Following aibarber pattern: centralized response handling.
        """
        print("💬 Responding to user...")
        
        answer = state.get("answer")
        if not answer:
            print("⚠️ No answer to send.")
            return {**state}

        print(f"📤 Sending: {answer}")
        new_message = AIMessage(content=answer)
        
        return {
            **state,
            "messages": state["messages"] + [new_message],
            "answer": None  # Clear the answer after sending
        }

    def _get_message_content(self, message) -> str:
        """Safely extract message content."""
        if hasattr(message, 'content'):
            if isinstance(message.content, str):
                return message.content
            elif isinstance(message.content, list) and len(message.content) > 0:
                if isinstance(message.content[0], dict) and "text" in message.content[0]:
                    return message.content[0]["text"]
                elif isinstance(message.content[0], str):
                    return message.content[0]
        return ""