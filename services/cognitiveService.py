import os
import sys
from langchain.prompts import PromptTemplate
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.parseJson import parse_json_object
from utils.fileUtils import read_json_file, write_json_file



set_cognitive_activity_reminder_prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant designed to set reminders for cognitive activities.
      "{llm_context} and {usercontext}" are only for contextual information. Only provide the context.
User's Instruction:
"{user_input}"

Your task is to analyze the user's instruction and extract the cognitive activity they want to be reminded about and the time for the reminder.

Response Format:

1. Reminder Set Successfully: If you can clearly identify both the cognitive activity and the reminder time from the user's instruction, return a JSON object in the following format:
{{
  "reminder_set": true,
  "activity": "...",
  "reminder_time": "...",
  "message": "Reminder set for '{{activity}}' at {{reminder_time}}."
}}

2. Missing Activity: If the user's instruction does not clearly specify the cognitive activity they want to be reminded about, return a JSON object in the following format:
{{
  "reminder_set": false,
  "missing_information": "activity",
  "message": "Could you please specify which cognitive activity you would like to be reminded about?"
}}

3. Missing Reminder Time: If the user specifies the activity but not the time, return a JSON object in the following format:
{{
  "reminder_set": false,
  "missing_information": "time",
  "message": "At what time would you like to be reminded to do '{{activity}}'?"
}}

Analyze the user's instruction and respond with the appropriate JSON object."""
)

check_cognitive_activity_reminders_prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant designed to check if a user has any existing reminders for cognitive activities.
  "{llm_context} and {usercontext}" are only for contextual information. Only provide the context.
User's Instruction:
"{user_input}"

Existing Cognitive Activity Reminders:
{cognitive_activity_reminders}

Your task is to analyze the user's instruction (which is likely a question about their reminders) and the list of their existing cognitive activity reminders.

Response Format:

1. Reminders Found: If the user has one or more cognitive activity reminders scheduled, return a JSON object summarizing these reminders. Include the activity name and the reminder time for each.
{{
  "reminders_exist": true,
  "reminders": [
    {{
      "activity": "...",
      "reminder_time": "...",
      "message":"Write the proper answer about what specifically the user is asking?"
    }}
  ]
}}

2. No Reminders Found: If the user does not have any cognitive activity reminders scheduled, return a JSON object indicating this.
{{
  "reminders_exist": false,
  "message": "You do not currently have any scheduled reminders for cognitive activities."
}}

Analyze the user's instruction and the existing reminders, and respond with the appropriate JSON object."""
)
def get_session_data():
  return read_json_file(r"./data/context_infor.json")
def set_cognitive_activity_reminder(user_input, llm):
  d = get_session_data()
  usercontext = d[0]
  llm_context = d[1]
  chain = set_cognitive_activity_reminder_prompt | llm
  response = chain.invoke({"user_input": user_input,"usercontext":usercontext, "llm_context":llm_context})
  data = parse_json_object(response.content)
  reminder_data =  read_json_file(r"./data/cognitive.json")
  if(not data['reminder_set']):
    print(f"Missing information is {data['missing_information']} ----- {data['message']}")
    return
  reminder_data.append(data)
  write_json_file(r"./data/cognitive.json", reminder_data)
  print(data)
  return data
  
def check_cognitive_activity_reminders(user_input, llm):
  d = get_session_data()
  usercontext = d[0]
  llm_context = d[1]
  chain = check_cognitive_activity_reminders_prompt | llm
  cognitive_activity_reminders =  read_json_file(r"./data/cognitive.json")
  response = chain.invoke({"user_input": user_input,"cognitive_activity_reminders":cognitive_activity_reminders, "usercontext":usercontext, "llm_context":llm_context})
  data = parse_json_object(response.content)
  if(not data['reminders_exist']):
    print(data['message'])
    return
  print(data['reminders'])
  return data['reminders']
  