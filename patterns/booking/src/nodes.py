"""
Nodes for the booking conversational flow.

Each node represents a specific step in the conversation:
- detect_intent: Identifies that the user wants to make a booking
- extract_booking_data: Extracts service and date from the user's message
- check_availability: Checks that the date/time is available
- ask_for_information: Asks for missing data
- confirm_booking: Confirms the booking details
- respond_user: Sends the final response to the user
"""

from langchain_core.messages import AIMessage
from src.patterns.booking.state import BookingState

class BookingNodes:
    """Nodes for the booking conversational flow."""
    
    def detect_intent_node(self, state: BookingState) -> BookingState:
        """
        Detects the intent to book an appointment.
        
        In this simple demo, we assume that any conversation
        that reaches here is a booking intent.
        """
        print("🎯 Detecting intent: BOOKING")
        return {
            **state,
            "intent": "book"
        }
    
    def extract_booking_data_node(self, state: BookingState) -> BookingState:
        """
        Extracts service and date from the user's message.
        
        Uses simple patterns to identify:
        - Services: "haircut", "beard trim", "styling"
        - Dates: "today", "tomorrow", "the day after tomorrow"
        """
        if not state["messages"]:
            return {**state}
            
        # In Studio: content[0]["text"]
        last_message = state["messages"][-1].content[0]["text"].lower()
        print(f"💬 Analyzing message: '{last_message}'")
        
        # Get existing booking data
        booking_data = state.get("booking_data", {})
        
        # Simple service extraction
        if "haircut" in last_message:
            booking_data["service"] = "haircut"
            print("✂️ Service detected: haircut")
        elif "beard" in last_message:
            booking_data["service"] = "beard trim"
            print("🧔 Service detected: beard trim")
        elif "styling" in last_message:
            booking_data["service"] = "styling"
            print("💇 Service detected: styling")
            
        # Simple date extraction
        if "today" in last_message:
            booking_data["appointment_date"] = "today"
            print("📅 Date detected: today")
        elif "tomorrow" in last_message:
            booking_data["appointment_date"] = "tomorrow"
            print("📅 Date detected: tomorrow")
        elif "day after tomorrow" in last_message:
            booking_data["appointment_date"] = "day after tomorrow"
            print("📅 Date detected: day after tomorrow")
            
        # Simple time extraction
        import re
        time_pattern = r'\b([0-9]{1,2}):?([0-9]{2})?\b'
        time_match = re.search(time_pattern, last_message)
        if time_match:
            hour = time_match.group(1)
            minute = time_match.group(2) or "00"
            booking_data["appointment_time"] = f"{hour}:{minute}"
            print(f"🕐 Time detected: {booking_data['appointment_time']}")
        
        # Confirmation extraction - Only if we already have complete booking data
        booking_confirmed = state.get("booking_confirmed", False)
        has_service = bool(booking_data.get("service"))
        has_date = bool(booking_data.get("appointment_date"))
        has_time = bool(booking_data.get("appointment_time"))
        
        # Only confirm if we have all the data AND user says yes
        if has_service and has_date and has_time:
            confirmation_words = ["yes", "perfect", "ok", "confirm"]
            if any(word in last_message for word in confirmation_words):
                booking_confirmed = True
                print("✅ Final confirmation detected with complete data")
        
        return {
            **state,
            "booking_data": booking_data,
            "booking_confirmed": booking_confirmed
        }
    
    def check_availability_node(self, state: BookingState) -> BookingState:
        """
        Checks availability for the requested date/time.
        
        If no time is provided: returns available times for the day.
        If time is provided and available: asks for confirmation.
        If time is provided and NOT available: shows available times.
        """
        booking_data = state.get("booking_data", {})
        service = booking_data.get("service", "service")
        appointment_date = booking_data.get("appointment_date", "date")
        appointment_time = booking_data.get("appointment_time")
        
        # Mock available times
        available_times = ["9:00", "10:00", "11:00", "15:00", "16:00", "17:00"]
        
        if appointment_time:
            # Check specific time
            print(f"📋 Checking availability for {service} on {appointment_date} at {appointment_time}")
            
            if appointment_time in available_times:
                # Time available → Ask for confirmation
                print("✅ Time available → asking for confirmation")
                answer = f"Perfect, I'm confirming your appointment:\n• Service: {service}\n• Date: {appointment_date}\n• Time: {appointment_time}\n\nDo you confirm the booking?"
                
                return {
                    **state,
                    "answer": answer
                }
            else:
                # Time NOT available → Show alternatives
                print("❌ Time not available → showing alternatives")
                times_text = ", ".join(available_times)
                answer = f"Sorry, {appointment_time} is not available on {appointment_date}. We have these times: {times_text}. Which one do you prefer?"
                
                # Reset time so they can choose another one
                updated_booking_data = {**booking_data}
                updated_booking_data.pop("appointment_time", None)
                
                return {
                    **state,
                    "booking_data": updated_booking_data,
                    "answer": answer
                }
        else:
            # No time provided → Show available times
            print(f"📋 Checking available times for {appointment_date}")
            times_text = ", ".join(available_times)
            answer = f"We have these available times for {appointment_date}: {times_text}. Which one do you prefer?"
            print(f"🕐 Showing times: {times_text}")
            
            return {
                **state,
                "answer": answer
            }
    
    def ask_for_information_node(self, state: BookingState) -> BookingState:
        """
        Asks for missing information.
        
        Identifies which data is missing and asks the appropriate question.
        """
        booking_data = state.get("booking_data", {})
        
        if not booking_data.get("service"):
            answer = "Hi! What service do you need? We have haircut, beard trim, and styling."
            print("❓ Asking for service")
        elif not booking_data.get("appointment_date"):
            answer = f"Perfect, a {booking_data['service']}. When do you need it? (today, tomorrow, day after tomorrow)"
            print("❓ Asking for date")
        else:
            # If we get here, we have service + date but the routing failed
            answer = "Could you give me more details about your booking?"
            print("❓ Unexpected case - we have service + date but are in ask_for_information")
            
        return {
            **state,
            "answer": answer
        }
    
    def confirm_booking_node(self, state: BookingState) -> BookingState:
        """
        Handles the final confirmation when the user says "yes/perfect".
        
        Only generates the final success message.
        """
        booking_data = state.get("booking_data", {})
        service = booking_data.get("service", "service")
        appointment_date = booking_data.get("appointment_date", "date")
        appointment_time = booking_data.get("appointment_time", "time")
        
        answer = f"Excellent! Your {service} appointment for {appointment_date} at {appointment_time} is confirmed. See you soon! 🎉"
        print(f"🎉 Booking completed: {service} for {appointment_date} at {appointment_time}")
        
        return {
            **state,
            "answer": answer
        }
    
    def respond_user_node(self, state: BookingState) -> BookingState:
        """
        Converts the answer field to an AIMessage and adds it to messages.
        
        Centralized function for all bot responses.
        """
        # Use answer from state if it exists, otherwise use a default fallback
        answer = state.get("answer")
        
        if not answer:
            # Fallback based on state
            if state.get("booking_confirmed"):
                booking_data = state.get("booking_data", {})
                service = booking_data.get("service", "service")
                appointment_date = booking_data.get("appointment_date", "date")
                appointment_time = booking_data.get("appointment_time", "time")
                answer = f"Excellent! Your {service} appointment for {appointment_date} at {appointment_time} is confirmed. See you soon! 🎉"
                print("🎉 Booking completed successfully")
            else:
                answer = "How else can I help you today?"
                print("💭 Using fallback response")
        
        print(f"💬 Sending response: {answer[:50]}...")
            
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=answer)],
            "answer": None  # Clear answer after using it
        }
