from langchain.prompts import PromptTemplate
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.parseJson import parse_json_object

from services.medicationService import set_medication_reminder, check_medication_schedule,get_medication_info,log_medication_taken,get_prescription_details
from utils.fileUtils import read_json_file
medication_management_prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant specialized in medication management for elderly individuals. Your task is to analyze the user's instruction and determine which function from the list below should be called to fulfill their request.
  "{llm_context} and {usercontext}" are only for contextual information. Only provide the context.
**Available Functions in `medicationService.py`:**

* `set_medication_reminder(user_id, medication_name, reminder_time)`: Sets a reminder for the user to take a specific medication at a given time.
* `check_medication_schedule(user_id, current_time=None)`: Checks the user's medication schedule for the current time or a specified time.
* `get_medication_info(user_id, medication_name)`: Retrieves detailed information about a specific medication for the user, such as dosage, frequency, and instructions.
* `log_medication_taken(user_id, medication_name, taken_time=None)`: Records that the user has taken a specific medication.
* `proactive_medication_inquiry(user_id)`: Initiates a check with the user to ask if they have taken their scheduled medications.

* `handle_missed_medication(user_id, medication_name, scheduled_time)`: Handles the scenario where a user might have missed a scheduled medication, potentially by sending a reminder or notifying a caregiver.
* `organize_medication(user_id)`: Provides information on how the user's medications should be organized based on their schedule.

* `get_prescription_details(user_id, medication_name=None)`: Retrieves prescription details, potentially for a specific medication or a list of all prescriptions.

**User Instruction:** "{user_input}"

Analyze the user's instruction and determine the most appropriate function to call from the list above to handle the request.

Respond with a JSON object containing a single key, "function_to_call", and the value being the exact name of the function to call.

If the user's instruction does not clearly map to any of the available functions, respond with:

{{
  "function_to_call": "unknown"
}}"""
)

def get_session_data():
  return read_json_file(r"./data/context_infor.json")

def handleMedicationCommand(user_input,llm):
  d = get_session_data()
  usercontext = d[0]
  llm_context = d[1]
  chain = medication_management_prompt | llm
  response = chain.invoke({"user_input": user_input,"usercontext":usercontext, "llm_context":llm_context})
  subcommand =  parse_json_object(response.content)['function_to_call']
  if(subcommand == "unknown"):
    print("Sorry, I could not help with you that. Could you please provide me more information about it?")
    return
  if(subcommand == 'set_medication_reminder'):
    return set_medication_reminder(user_input,llm)
  elif(subcommand == 'check_medication_schedule'):
    return check_medication_schedule(user_input,llm)
  elif(subcommand == 'get_medication_info'):
    return get_medication_info(user_input, llm)
  elif(subcommand == 'log_medication_taken'):
    return log_medication_taken(user_input, llm)
  elif(subcommand == 'get_prescription_details'):
    return get_prescription_details(user_input, llm)
  
