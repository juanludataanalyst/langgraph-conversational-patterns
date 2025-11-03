"""
Nodes for appointment cancellation/modification flow.

Educational pattern following the same structure as booking and onboarding:
- detect_intent: Identifies cancel/modify intent
- extract_customer_data: Extracts customer name from message  
- lookup_appointments: Finds customer's existing appointments
- process_request: Handles the modification/cancellation request
- respond_user: Sends responses to user

This demonstrates a common enterprise pattern for appointment management.
"""

import re
from langchain_core.messages import AIMessage
from patterns.modify_appointment.state import AppointmentState, ExistingAppointment, ModificationRequest

class AppointmentNodes:
    """Nodes for appointment management conversational flow."""
    
    def __init__(self):
        # Mock appointment database for educational demo
        # In real systems, this would connect to your appointment database
        self.mock_appointments = [
            {
                "appointment_id": "APT-001",
                "service": "haircut", 
                "date": "tomorrow",
                "time": "10:00",
                "customer_name": "Juan Luis",
                "status": "confirmed"
            },
            {
                "appointment_id": "APT-002",
                "service": "beard trim",
                "date": "next Monday", 
                "time": "15:30",
                "customer_name": "Juan Luis",
                "status": "confirmed"
            }
        ]
    
    def detect_intent_node(self, state: AppointmentState) -> AppointmentState:
        """
        Detects the intent to cancel or modify an appointment.
        
        Simple pattern matching for educational purposes.
        In production, you'd use more sophisticated NLU.
        """
        print("🎯 Detecting intent...")
        
        if not state["messages"]:
            return {**state}
        
        # If we already have a valid intent, preserve it
        current_intent = state.get("intent")
        if current_intent and current_intent != "unknown":
            print(f"✅ Preserving existing intent: {current_intent}")
            return {
                **state,
                "current_step": state.get("current_step")  # Preserve current step
            }
        
        last_message = state["messages"][-1].content[0]["text"]
        print(f"💬 Analyzing message: '{last_message}'")
        
        # Simple intent detection
        intent = None
        if any(word in last_message.lower() for word in ["cancel", "cancelar"]):
            intent = "cancel"
            print("🚫 Cancel intent detected")
        elif any(word in last_message.lower() for word in ["modify", "modificar", "change", "cambiar"]):
            intent = "modify" 
            print("✏️ Modify intent detected")
        elif any(word in last_message.lower() for word in ["reschedule", "reprogramar"]):
            intent = "reschedule"
            print("📅 Reschedule intent detected")
        else:
            intent = "unknown"
            print("❓ Unknown intent")
        
        # Set appropriate answer for unknown intent
        answer = None
        if intent == "unknown":
            answer = "I can help you cancel, modify, or reschedule your appointment. Please tell me what you'd like to do with your appointment."
        
        return {
            **state,
            "intent": intent,
            "answer": answer,
            "current_step": "identify" if intent != "unknown" else None
        }
    
    def extract_customer_data_node(self, state: AppointmentState) -> AppointmentState:
        """
        Extracts customer name from the message.
        
        Uses simple regex patterns for educational demonstration.
        Preserves existing customer name if already established.
        """
        print("👤 Extracting customer data...")
        
        if not state["messages"]:
            return {**state}
        
        # Get the message first (needed for confirmation detection)
        last_message = state["messages"][-1].content[0]["text"]
        
        # Get current step early (needed for confirmation check)
        current_step = state.get("current_step")
        modification_confirmed = state.get("modification_confirmed", False)
        
        # FIRST: Check for confirmation if we're awaiting it (highest priority)
        if current_step == "awaiting_confirmation":
            if not modification_confirmed:
                confirmation_words = ["yes", "sí", "si", "ok", "okay", "confirm", "confirmar", "perfecto", "perfect"]
                if any(word in last_message.lower() for word in confirmation_words):
                    modification_confirmed = True
                    print("✅ Modification confirmation detected")
            
            return {
                **state,
                "modification_confirmed": modification_confirmed,
                "current_step": "awaiting_confirmation"
            }
        
        # SECOND: Check if we already have a customer name
        existing_name = state.get("customer_name")
        if existing_name:
            print(f"✅ Customer name already known: {existing_name}")
            
            # Preserve current_step when customer is already known
            if current_step == "awaiting_selection":
                return {**state, "current_step": "awaiting_selection", "modification_confirmed": modification_confirmed}
            elif current_step == "awaiting_modification_details":
                return {**state, "current_step": "awaiting_modification_details", "modification_confirmed": modification_confirmed}
            elif current_step == "checking_availability":
                return {**state, "current_step": "checking_availability", "modification_confirmed": modification_confirmed}
            else:
                return {**state, "current_step": "lookup", "modification_confirmed": modification_confirmed}
        
        # Enhanced name extraction patterns - can find names anywhere in message
        name_patterns = [
            # Standard beginning patterns
            r"i'm (.+?)(?:\.|$|,)",
            r"i am (.+?)(?:\.|$|,)",
            r"my name is (.+?)(?:\.|$|,)",
            r"soy (.+?)(?:\.|$|,)",
            r"me llamo (.+?)(?:\.|$|,)",
            # End of message patterns - NEW!
            r"my name is (.+?)(?:\.|$)",
            r"i'm (.+?)(?:\.|$)",
            r"i am (.+?)(?:\.|$)",
            r"(?:call me|i'm|i am) (.+?)(?:\.|$)",
            # Mid-sentence patterns - NEW!
            r"(?:book|appointment|booking).+?(?:name is|i'm|i am) (.+?)(?:\.|$|,)",
            r"(?:modify|change|cancel).+?(?:name is|i'm|i am) (.+?)(?:\.|$|,)",
            # Flexible positioning patterns - NEW!
            r"(?:my name is|i'm|i am) ([a-zA-Z\s]+?)(?:\s+and|\s+,|\.|$)",
            r"(?:name is|i'm|i am) ([a-zA-Z\s]+?)(?:\s+want|\s+need|\s+would|\.|$|,)"
        ]
        
        extracted_name = None
        for pattern in name_patterns:
            match = re.search(pattern, last_message, re.IGNORECASE)
            if match:
                # Clean up the extracted name
                raw_name = match.group(1).strip()
                # Remove common words that might get captured
                clean_name = re.sub(r'\b(and|want|need|would|like|to|the|my|a|an)\b.*', '', raw_name, flags=re.IGNORECASE).strip()
                if clean_name and len(clean_name.split()) <= 3:  # Reasonable name length
                    extracted_name = clean_name.title()
                    break
        
        # Only check for confirmation if we're awaiting it
        if current_step == "awaiting_confirmation" and not modification_confirmed:
            confirmation_words = ["yes", "sí", "si", "ok", "okay", "confirm", "confirmar", "perfecto", "perfect"]
            if any(word in last_message.lower() for word in confirmation_words):
                modification_confirmed = True
                print("✅ Modification confirmation detected")
        
        if extracted_name:
            print(f"✅ Customer name extracted: {extracted_name}")
            return {
                **state,
                "customer_name": extracted_name,
                "modification_confirmed": modification_confirmed,
                "current_step": "lookup"
            }
        else:
            print("ℹ️ No customer name found in message")
            return {
                **state,
                "customer_name": None,
                "modification_confirmed": modification_confirmed,
                "answer": "I need your name to help you with your appointment. Please tell me your name.",
                "current_step": "identify"
            }
    
    def lookup_appointments_node(self, state: AppointmentState) -> AppointmentState:
        """
        Looks up customer appointments in the system.
        
        Simple mock lookup for educational demonstration.
        In production, this would query your appointment database.
        """
        print("📋 Looking up appointments...")
        
        customer_name = state.get("customer_name")
        
        if not customer_name:
            print("❌ No customer name to search with")
            return {
                **state,
                "answer": "I need your name to look up your appointments. Please tell me your name."
            }
        
        # Mock database lookup - find all appointments for customer
        all_appointments = []
        for apt in self.mock_appointments:
            if apt["customer_name"].lower() == customer_name.lower():
                all_appointments.append(ExistingAppointment(**apt))
        
        print(f"📅 Found {len(all_appointments)} total appointments for {customer_name}")
        
        # Apply message-based filters to narrow down results
        filtered_appointments = self._apply_message_filters(all_appointments, state)
        
        print(f"🔍 After filtering: {len(filtered_appointments)} relevant appointments")
        
        # Don't change current_step - preserve whatever was set by process_request
        current_step = state.get("current_step", "processing")
        
        # Keep the current step as-is - don't modify it here
        next_step = current_step
        
        return {
            **state,
            "found_appointments": filtered_appointments,
            "current_step": next_step
        }
    
    def _apply_message_filters(self, appointments: list, state: AppointmentState) -> list:
        """
        Apply message-based filters to narrow down appointment results.
        
        Educational example of smart filtering based on user message content.
        Maintains separation of concerns - only filters, doesn't change logic.
        """
        if not appointments or not state.get("messages"):
            return appointments
        
        # Get the original message (first message in conversation)
        original_message = state["messages"][0].content[0]["text"].lower()
        print(f"🔍 Applying filters based on: '{original_message[:50]}...'")
        
        filtered = appointments[:]  # Start with all appointments
        
        # Filter by service type mentioned in message
        service_filters = {
            "haircut": ["haircut", "hair cut", "cut"],
            "beard trim": ["beard", "trim", "beard trim"],
            "styling": ["styling", "style", "hair style"],
            "wash": ["wash", "shampoo", "clean"]
        }
        
        for service_name, keywords in service_filters.items():
            if any(keyword in original_message for keyword in keywords):
                service_matches = [apt for apt in filtered if apt["service"].lower() == service_name]
                if service_matches:
                    filtered = service_matches
                    print(f"🎯 Filtered by service: {service_name} ({len(filtered)} matches)")
                    break
        
        # Filter by date references (if mentioned)
        date_filters = {
            "tomorrow": ["tomorrow", "mañana"],
            "today": ["today", "hoy"],
            "monday": ["monday", "lunes"],
            "next monday": ["next monday", "próximo lunes"]
        }
        
        for date_value, keywords in date_filters.items():
            if any(keyword in original_message for keyword in keywords):
                date_matches = [apt for apt in filtered if date_value in apt["date"].lower()]
                if date_matches:
                    filtered = date_matches
                    print(f"📅 Filtered by date: {date_value} ({len(filtered)} matches)")
                    break
        
        # Filter by time references (basic)
        time_keywords = ["morning", "afternoon", "evening", "10:00", "15:30"]
        for time_keyword in time_keywords:
            if time_keyword in original_message:
                time_matches = [apt for apt in filtered if time_keyword in apt["time"] or time_keyword in apt["date"]]
                if time_matches:
                    filtered = time_matches
                    print(f"⏰ Filtered by time reference: {time_keyword} ({len(filtered)} matches)")
                    break
        
        return filtered
    
    def process_request_node(self, state: AppointmentState) -> AppointmentState:
        """
        Processes the appointment request (cancel/modify).
        
        Handles both initial processing and appointment selection.
        Uses current_step to track flow state.
        """
        print("⚙️ Processing request...")
        
        intent = state.get("intent")
        found_appointments = state.get("found_appointments", [])
        customer_name = state.get("customer_name")
        current_step = state.get("current_step")
        
        # DEBUG: Show state in response
        debug_info = f"[DEBUG: step={current_step}, appointments={len(found_appointments)}]"
        
        if not customer_name:
            return {
                **state,
                "answer": "I need your name to help you. Please tell me your name.",
                "current_step": "identify"
            }
        
        # Handle appointment selection if we're waiting for it
        if current_step == "awaiting_selection":
            return self._handle_appointment_selection(state)
        
        # Handle modification details if we're waiting for them
        if current_step == "awaiting_modification_details":
            return self._handle_modification_details(state)
        
        # Handle confirmation is now a separate node - remove from here
        
        # Initial processing
        if not found_appointments:
            action_word = "cancel" if intent == "cancel" else "modify"
            return {
                **state,
                "modification_completed": True,
                "answer": f"I couldn't find any appointments to {action_word} for {customer_name}. Would you like to book a new appointment?",
                "current_step": "completed"
            }
        
        if len(found_appointments) == 1:
            # Single appointment found
            apt = found_appointments[0]
            
            if intent == "cancel":
                answer = f"✅ Your {apt['service']} appointment on {apt['date']} at {apt['time']} has been cancelled."
                return {
                    **state,
                    "selected_appointment": apt,
                    "modification_completed": True,
                    "answer": answer,
                    "current_step": "completed"
                }
            else:
                # Check if modification details were provided in the original message
                original_message = state["messages"][0].content[0]["text"] if state.get("messages") else ""
                modification_request = self._extract_modification_from_text(original_message.lower())
                
                if modification_request:
                    # Direct modification - go to availability check
                    print("⚡ Direct modification detected in original message")
                    return {
                        **state,
                        "selected_appointment": apt,
                        "modification_request": ModificationRequest(**modification_request),
                        "modification_completed": False,  # Don't complete yet - check availability first
                        "answer": None,  # Clear answer, let check_availability handle response
                        "current_step": "checking_availability"
                    }
                else:
                    # No modification details provided - ask for them
                    answer = f"✅ Your {apt['service']} appointment on {apt['date']} at {apt['time']} is ready to be modified. What changes would you like? (time, date, or service)"
                    return {
                        **state,
                        "selected_appointment": apt,
                        "modification_completed": False,
                        "answer": answer,
                        "current_step": "awaiting_modification_details"
                    }
        
        # Multiple appointments - show list for selection
        appointments_text = []
        for i, apt in enumerate(found_appointments, 1):
            appointments_text.append(f"{i}. {apt['service']} on {apt['date']} at {apt['time']}")
        
        appointments_list = "\n".join(appointments_text)
        action_word = "cancel" if intent == "cancel" else "modify"
        
        return {
            **state,
            "answer": f"You have {len(found_appointments)} appointments:\n\n{appointments_list}\n\nWhich one would you like to {action_word}? (respond with the number)",
            "current_step": "awaiting_selection"
        }
    
    def _handle_appointment_selection(self, state: AppointmentState) -> AppointmentState:
        """
        Handles user selection of appointment number.
        Now supports dynamic "number + modification" in one response.
        """
        print("🔢 Processing appointment selection...")
        
        if not state["messages"]:
            return {**state}
        
        last_message = state["messages"][-1].content[0]["text"].strip()
        found_appointments = state.get("found_appointments", [])
        intent = state.get("intent")
        
        # Check for any number in the message (flexible appointment selection)
        number_match = re.search(r"(\d+)", last_message)
        
        if number_match:
            # Extract selection number and treat rest as modification text
            selection_num = int(number_match.group(1))
            # Remove ONLY the first number (selection) from the message
            modification_text = re.sub(r"^(\d+)\s*", "", last_message).strip().lower()
            # Clean up common words but keep time numbers
            modification_text = re.sub(r"^(?:i want to |i |want to |change |modify |booking |appointment )", "", modification_text).strip()
            
            print(f"🎯 Dynamic selection detected: {selection_num} + '{modification_text}'")
            
            # Validate selection range
            if selection_num < 1 or selection_num > len(found_appointments):
                return {
                    **state,
                    "answer": f"Please select a number between 1 and {len(found_appointments)}.",
                    "current_step": "awaiting_selection"
                }
            
            # Get selected appointment
            selected_apt = found_appointments[selection_num - 1]
            
            # For cancel intent, process immediately
            if intent == "cancel":
                answer = f"✅ Your {selected_apt['service']} appointment on {selected_apt['date']} at {selected_apt['time']} has been cancelled."
                return {
                    **state,
                    "selected_appointment": selected_apt,
                    "modification_completed": True,
                    "answer": answer,
                    "current_step": "completed"
                }
            
            # For modify intent, process the modification directly if there's modification text
            if modification_text:
                return self._process_dynamic_modification(state, selected_apt, modification_text)
            else:
                # Just selection, ask for modification details
                answer = f"✅ Your {selected_apt['service']} appointment on {selected_apt['date']} at {selected_apt['time']} is ready to be modified. What changes would you like? (time, date, or service)"
                return {
                    **state,
                    "selected_appointment": selected_apt,
                    "modification_completed": False,
                    "answer": answer,
                    "current_step": "awaiting_modification_details"
                }
        
        # Fallback: if no number found, show error
        if not last_message.isdigit():
            return {
                **state,
                "answer": "Please respond with the number of the appointment you'd like to select, or the number followed by your changes (e.g., '2 change time to 3pm').",
                "current_step": "awaiting_selection"
            }
        
        selection_num = int(last_message)
        
        # Validate selection range
        if selection_num < 1 or selection_num > len(found_appointments):
            return {
                **state,
                "answer": f"Please select a number between 1 and {len(found_appointments)}.",
                "current_step": "awaiting_selection"
            }
        
        # Get selected appointment (convert to 0-based index)
        selected_apt = found_appointments[selection_num - 1]
        
        # Process the selected appointment
        if intent == "cancel":
            answer = f"✅ Your {selected_apt['service']} appointment on {selected_apt['date']} at {selected_apt['time']} has been cancelled."
            return {
                **state,
                "selected_appointment": selected_apt,
                "modification_completed": True,
                "answer": answer,
                "current_step": "completed"
            }
        else:
            answer = f"✅ Your {selected_apt['service']} appointment on {selected_apt['date']} at {selected_apt['time']} is ready to be modified. What changes would you like? (time, date, or service)"
            return {
                **state,
                "selected_appointment": selected_apt,
                "modification_completed": False,
                "answer": answer,
                "current_step": "awaiting_modification_details"
            }
    
    def _process_dynamic_modification(self, state: AppointmentState, selected_apt: dict, modification_text: str) -> AppointmentState:
        """
        Process modification text for a selected appointment.
        Used for dynamic "number + modification" responses.
        """
        print(f"⚡ Processing dynamic modification: '{modification_text}'")
        
        # Use the same modification logic from _handle_modification_details
        modification_request = self._extract_modification_from_text(modification_text)
        
        if not modification_request:
            return {
                **state,
                "selected_appointment": selected_apt,
                "answer": f"I didn't understand the change '{modification_text}'. Please specify what you'd like to change: time (e.g., '3pm'), date (e.g., 'tomorrow'), or service (e.g., 'beard trim').",
                "current_step": "awaiting_modification_details"
            }
        
        # Don't build final message yet - let check_availability handle it
        # Just set up the modification request and go to availability check
        
        return {
            **state,
            "selected_appointment": selected_apt,
            "modification_request": ModificationRequest(**modification_request),
            "modification_completed": False,  # Don't complete yet - check availability first
            "answer": None,  # Clear answer, let check_availability handle response
            "current_step": "checking_availability"
        }
    
    def _extract_modification_from_text(self, text: str) -> dict:
        """
        Extract modification details from text. 
        Shared logic for both dynamic and step-by-step modifications.
        """
        modification_request = {}
        
        # Time changes: "change time to 3pm", "move to 15:30", "at 2pm", "to 11 hours"
        time_patterns = [
            r"(?:change|move|reschedule).*?(?:time|to)\s*(\d{1,2}(?::\d{2})?(?:\s*(?:am|pm|hours?))?)",
            r"(?:at|to)\s*(\d{1,2}(?::\d{2})?(?:\s*(?:am|pm|hours?))?)",
            r"(\d{1,2})\s*(?:hours?|hrs?|hour)",  # "11 hours", "3 hrs", "11 hour"
            r"(\d{1,2}(?::\d{2})?(?:\s*(?:am|pm))?)"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                raw_time = match.group(1).strip()
                # Clean up time format: "11 hours" -> "11:00", "3pm" -> "3pm"
                clean_time = re.sub(r'\s*hours?', ':00', raw_time)
                clean_time = re.sub(r'\s*hrs?', ':00', clean_time)
                clean_time = re.sub(r'\s*hour', ':00', clean_time)  # "11 hour" -> "11:00"
                modification_request["new_time"] = clean_time
                break
        
        # Date changes: "change date to tomorrow", "move to monday", "next week"
        date_patterns = [
            r"(?:change|move|reschedule).*?(?:date|to)\s*(tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next week)",
            r"(?:to|on)\s*(tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next week)",
            r"(tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|next week)"
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                modification_request["new_date"] = match.group(1)
                break
        
        # Service changes: "change to beard trim", "make it a styling"
        service_patterns = [
            r"(?:change|make).*?(?:to|it)\s*(haircut|beard trim|styling|wash)",
            r"(?:to|for)\s*(haircut|beard trim|styling|wash)",
            r"(haircut|beard trim|styling|wash)"
        ]
        
        for pattern in service_patterns:
            match = re.search(pattern, text)
            if match:
                modification_request["new_service"] = match.group(1)
                break
        
        return modification_request
    
    def check_availability_node(self, state: AppointmentState) -> AppointmentState:
        """
        Checks availability for the requested modification.
        
        Educational pattern: Always validate availability before confirming changes.
        Shows alternatives if requested time is not available.
        """
        print("🕐 Checking availability for modification...")
        
        selected_apt = state.get("selected_appointment")
        modification_request = state.get("modification_request")
        
        if not selected_apt or not modification_request:
            return {
                **state,
                "answer": "I need appointment and modification details to check availability.",
                "current_step": "processing"
            }
        
        # Extract requested changes
        new_time = modification_request.get("new_time")
        new_date = modification_request.get("new_date")
        new_service = modification_request.get("new_service")
        
        # Mock availability check (educational example)
        available_times = ["9:00", "11:00", "14:00", "16:00"]
        available = True
        
        # Enhanced availability logic to handle different change types
        if new_time:
            # Validate specific time requested
            check_time = new_time.replace(":00", "").replace("pm", "").replace("am", "")
            if check_time in ["13", "17", "18"]:  # Simulate unavailable times
                available = False
                # Time not available - show alternatives
                available_times_text = ", ".join(available_times)
                answer = f"❌ Sorry, {new_time} is not available. Here are available times: {available_times_text}. Which time would you prefer?"
                
                return {
                    **state,
                    "answer": answer,
                    "modification_request": None,  # Clear current request
                    "current_step": "awaiting_modification_details"
                }
        elif new_date and not new_time:
            # Date change without specific time - show available times for that date
            available_times_text = ", ".join(available_times)
            current_service = selected_apt.get("service", "appointment")
            answer = f"✅ I can change your {current_service} appointment to {new_date}. What time would you prefer? Available times: {available_times_text}"
            
            return {
                **state,
                "answer": answer,
                "current_step": "awaiting_modification_details"  # Keep asking for time
            }
        
        # If we reach here, time is available or it's a service/complete change
        changes = []
        if new_time:
            changes.append(f"time to {new_time}")
        if new_date:
            changes.append(f"date to {new_date}")
        if new_service:
            changes.append(f"service to {new_service}")
        
        changes_text = " and ".join(changes)
        current_service = selected_apt.get("service", "appointment")
        current_date = selected_apt.get("date", "current date")
        current_time = selected_apt.get("time", "current time")
        
        answer = f"✅ Great! I can change your {current_service} appointment {changes_text}. Your updated appointment would be on {new_date or current_date} at {new_time or current_time}. Shall I confirm this change? (yes/no)"
        
        return {
            **state,
            "answer": answer,
            "current_step": "awaiting_confirmation"
        }
    
    def confirm_modification_node(self, state: AppointmentState) -> AppointmentState:
        """
        Separate node to handle user confirmation of the modification.
        
        Following the same pattern as booking's confirm_booking_node.
        Clean separation of concerns.
        """
        print("✅ Processing modification confirmation...")
        
        if not state["messages"]:
            return {**state}
        
        last_message = state["messages"][-1].content[0]["text"].lower().strip()
        selected_apt = state.get("selected_appointment")
        modification_request = state.get("modification_request")
        
        # Check for confirmation keywords
        confirmation_words = ["yes", "sí", "si", "ok", "okay", "confirm", "confirmar", "perfecto", "perfect"]
        rejection_words = ["no", "cancel", "cancelar", "never mind"]
        
        if any(word in last_message for word in confirmation_words):
            # User confirmed - finalize the modification
            if not selected_apt or not modification_request:
                return {
                    **state,
                    "answer": "Sorry, I lost track of the modification details. Please start over.",
                    "current_step": "completed"
                }
            
            # Build final confirmation message
            changes = []
            if "new_time" in modification_request:
                changes.append(f"time to {modification_request['new_time']}")
            if "new_date" in modification_request:
                changes.append(f"date to {modification_request['new_date']}")
            if "new_service" in modification_request:
                changes.append(f"service to {modification_request['new_service']}")
            
            changes_text = " and ".join(changes)
            new_service = modification_request.get('new_service', selected_apt['service'])
            new_date = modification_request.get('new_date', selected_apt['date'])
            new_time = modification_request.get('new_time', selected_apt['time'])
            
            answer = f"🎉 Excellent! Your appointment has been successfully modified. Your {new_service} appointment is now confirmed for {new_date} at {new_time}. See you then!"
            
            return {
                **state,
                "modification_completed": True,
                "answer": answer,
                "current_step": "completed"
            }
        
        elif any(word in last_message for word in rejection_words):
            # User rejected - cancel the modification
            return {
                **state,
                "modification_request": None,
                "answer": "No problem! Your original appointment remains unchanged. Is there anything else I can help you with?",
                "current_step": "completed"
            }
        
        else:
            # Unclear response - ask again
            return {
                **state,
                "answer": "I didn't understand. Please say 'yes' to confirm the change or 'no' to keep your original appointment.",
                "current_step": "awaiting_confirmation"
            }
    
    def _handle_modification_details(self, state: AppointmentState) -> AppointmentState:
        """
        Handles user's modification details (time, date, service changes).
        
        Educational regex patterns for common modification requests.
        """
        print("✏️ Processing modification details...")
        
        if not state["messages"]:
            return {**state}
        
        last_message = state["messages"][-1].content[0]["text"].lower().strip()
        selected_apt = state.get("selected_appointment")
        
        if not selected_apt:
            return {
                **state,
                "answer": "I need to know which appointment you want to modify first.",
                "current_step": "processing"
            }
        
        # Use shared modification extraction logic
        modification_request = self._extract_modification_from_text(last_message)
        
        # Process the modification
        if not modification_request:
            return {
                **state,
                "answer": "I didn't understand the change you want to make. Please specify what you'd like to change: time (e.g., '3pm'), date (e.g., 'tomorrow'), or service (e.g., 'beard trim').",
                "current_step": "awaiting_modification_details"
            }
        
        # Don't complete immediately - go to availability check first
        return {
            **state,
            "modification_request": ModificationRequest(**modification_request),
            "modification_completed": False,  # Don't complete yet - check availability first
            "answer": None,  # Clear answer, let check_availability handle response
            "current_step": "checking_availability"
        }
    
    def respond_user_node(self, state: AppointmentState) -> AppointmentState:
        """
        Convert answer to AIMessage and send to user.
        
        Centralized response handling.
        """
        answer = state.get("answer")
        if not answer:
            print("⚠️ No answer to send to user")
            return {**state}
        
        print(f"💬 Sending response: {answer[:50]}...")
        
        # Convert answer to AIMessage
        new_message = AIMessage(content=answer)
        
        return {
            **state,
            "messages": state["messages"] + [new_message],
            "answer": None  # Clear after sending
        }