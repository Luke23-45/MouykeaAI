from langchain.prompts import PromptTemplate
import uuid
import re
import sys
import os
import ast
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.fileUtils import read_json_file, write_json_file
from utils.parseJson import parse_json_object
from utils.sendEmail import send_email


set_medication_reminder_prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant designed to set medication reminders for users based on their medical information.
  "{llm_context} and {usercontext}" are only for contextual information. Only provide the context.
User's Medical Information:
{medicalInfo}

User's Instruction:
"{user_input}"

Your task is to process the user's instruction to set a medication reminder.

First, identify the name of the medication the user wants to be reminded about from their instruction. Then, check if this medication is listed in the "medications" section of the provided medical information.
if the user is mentioning about a disease and there could be corresponding medication in the medicalInfo please check this also as well.
Conditions and Responses:

1. Medication Not Found: If the medication name from the user's instruction is NOT found in the user's medical information, respond with the following JSON:
{{
  "repeated_medication":"boolearn value if the user has already taken medicine more than they supposed to or did not taken as prescribed by doctor.",
  "reminder_set": false,
  "message": "Write what type of medical is not in their info. Write the gentle reponse."
}}

2. Medication Found: If the medication name IS found in the user's medical information, extract the reminder time from the user's instruction. Then, return a JSON object containing the following information about the medication:
{{
  "repeated_medication":"boolearn value if the user has already taken medicine more than they supposed to or did not taken as prescribed by doctor.",
  "reminder_set": true,
  "medication_name": "...",
  "dosage": "...",
  "frequency": "...",
  "times": [...]
}}

Populate the "medication_name", "dosage", "frequency", and "times" fields with the corresponding information from the user's medical information. If the user's instruction does not clearly specify a reminder time, you can prompt for it or use a default time if appropriate (for this prompt, assume the time is provided).

Analyze the user's instruction and the medical information, and respond with the appropriate JSON object.
"""
)


check_medication_schedule_prompt = PromptTemplate.from_template("""
You are a helpful AI assistant tasked with providing the user with their medication schedule.
  "{llm_context} and {usercontext}" are only for contextual information. Only provide the context.
User's Medication Schedule:
{medicalremainder}

User's Request:
{user_input}

Instructions:
Analyze the user's request and the provided medication schedule.

Conditions and Responses:

1. No Scheduled Medications:
If the "User's Medication Schedule" is empty or contains no entries, respond with the following JSON:
{{
  "schedule_available": false,
  "message": "You do not have any scheduled medications."
}}

2. Scheduled Medications Found:
If the "User's Medication Schedule" contains entries, summarize the schedule in a structured JSON format. Include the medication name and the time(s) it should be taken. The response should be:
{{
  "schedule_available": true,
  "medications_due": [
    {{
      "medication_name": "Medication A",
      "times": ["8:00 AM", "8:00 PM"]
    }}
    // more medications if applicable
  ]
}}

- Populate the "medication_name" and "times" fields based on the information in the "User's Medication Schedule."
- If the user's request is time-specific (e.g., "What medications do I take now?"), filter the schedule accordingly.
- Otherwise, provide the full schedule.

Respond only with the appropriate JSON object.
""")


get_medication_info_prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant designed to provide information about a user's prescribed medications.
      "{llm_context} and {usercontext}" are only for contextual information. Only provide the context.
User's Request:
{user_input}
User's Medication Information:
{medicationInfo}



Your task is to retrieve detailed information about a specific medication mentioned in the user's request from their medication information.

1. Identify the name of the medication the user is asking about.
2. Search for this medication in the "medications" list provided in the JSON above.

Response Format:

while checking please be perform the strict checking.
* If the medication is found: Return a JSON object containing the medication name, dosage, frequency, and instructions.
{{
  "medication_found": true,
  "medication_name": "...",
  "dosage": "...",
  "frequency": "...",
  "instructions": "..."
}}

* If the medication is NOT found: Return a JSON object indicating that the medication is not in the user's list.
{{
  "medication_found": false,
  "message": "This medication is not found in your current medication list."
}}

Analyze the user's request and the medication information, and respond with the appropriate JSON object."""
)

record_medication_prompt = PromptTemplate.from_template("""
You are a helpful AI assistant tasked with recording when a user takes their medication.
  "{llm_context} and {usercontext}" are only for contextual information. Only provide the context.
User's Input:
{user_input}

User's Medical Information:
{medical_info}

Medications Taken Today (So Far):
{medicine_take_for_a_day}

Instructions:

1. Analyze the user's input to identify:
   - The name of the medication they have taken.
   - The time when they took it.

2. The time must be **specific**:
   - Acceptable time formats include: parts of the day (e.g., "morning", "afternoon", "evening", "night") or absolute times like "8:00 AM", "3:30 PM", etc.
   - **Do NOT accept vague terms** like "today", "yesterday", or any day of the week as valid time inputs. If the time is vague or missing, consider it a missing value.

3. Check if the medication mentioned exists in the user's medical information.

Response Format:

1. **If the medication is found** in the medical information and the time is valid:
Return the following JSON:
{{
  "medication_logged": true,
  "medication_name": "...",
  "taken_at": "...",
  "medications_taken_today": [...]
}}

2. **If the medication is NOT found**, or if either the medication name or valid time is missing:
Return the following JSON:
{{
  "medication_logged": false,
  "message": "The medication was not found in your current list, or the time provided is not valid. Please make sure to include both the medication name and a specific time (e.g., morning, 8:00 AM)."
}}

Important:
- Do NOT make up medication names or times.
- Do NOT proceed if essential details are missing — return the appropriate failure response.
- Respond only with the correct JSON object.
""")



identify_concern_medicine_prompt = PromptTemplate.from_template("""
You are a helpful AI assistant tasked with identifying potential concerns related to a user's medication intake by comparing their prescribed medications with their medication log.

        "{llm_context} and {usercontext}" are only for contextual information. Only provide the context.                                                          

User's Prescribed Medication Information (JSON):
{medicationInfo}

User's Medication Log (JSON):
{log_medication}

Your Task:
Analyze the user's medication log and compare it against their prescribed medication information. Your goal is to identify any discrepancies or potential concerns.

Concern to Check:
- Medications logged in the medication log that are NOT found in the prescribed medication list. 
- Taken in different time than prescribed time of medicine.(Please refer to the medicationInfo time). Do not do the strict check. Check based on medical time validations.
- if the frequence exceeds.

Response Format:

1. If a concern is found (i.e., logged medication not in the prescribed list), return:
{{
  "concern_identified": true,
  "concern_type": "Irrelevant Medication Logged",
  "irrelevant_medications": ["Medication A", "Medication B"],
  "message": "The following medication(s) were logged but are not found in your prescribed medication list. Please verify."
}}

2. If there are no discrepancies:
{{
  "concern_identified": false,
  "message": "No concerns found regarding medications logged against your prescribed list."
}}

Important:
- Do not make up any medication names.
- Only include medication names that are present in the medication log and not in the prescribed list.
- Your response must be a valid JSON object in one of the two formats above.

Analyze the provided data carefully and respond with the correct JSON.
""")

get_prescription_details_prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant designed to provide prescription details to users based on their medical information.
      "{llm_context} and {usercontext}" are only for contextual information. Only provide the context.
User's Request:
"{user_input}"
    
User's Medical Information (JSON):
{medical_info}


Your task is to analyze the user's request and retrieve prescription information from the provided medical information.

Scenarios:

**1. Specific Medication Requested**
If the user asks about a specific medication (e.g., "Tell me about my Metformin prescription", "What are the details for Lisinopril?"), extract the medication name and return the following JSON:

{{
  "prescription_found": true,
  "medication_name": "...",
  "dosage": "...",
  "frequency": "...",
  "times": ["..."],
  "route": "...",
  "instructions": "...",
  "start_date": "...",
  "end_date": "...",
  "prescribing_doctor": "..."
}}

- Populate all fields using the matching medication entry in the user's medical info.
- If a field is missing, return an empty string (`""`) or `null`.

**2. All Prescriptions Requested**
If the user asks for all their current prescriptions (e.g., "Show me all my medications", "What prescriptions do I have?"), return:

{{
  "prescription_found": true,
  "prescriptions": [
    {{
      "medication_name": "...",
      "dosage": "...",
      "frequency": "...",
      "times": ["..."],
      "route": "...",
      "instructions": "...",
      "start_date": "...",
      "end_date": "...",
      "prescribing_doctor": "..."
    }}
    // more prescription objects if applicable
  ]
}}

**3. Medication Not Found**
If the user asks about a specific medication that is not in the list, return:

{{
  "prescription_found": false,
  "message": "The medication 'medication_name' was not found in your current prescription list."
}}

Rules:
- Replace `medication_name` in the message with the actual name mentioned by the user.
- Only return the JSON. Do not include any explanations or text outside the JSON object.

Analyze the user's request and respond with the appropriate JSON.
"""
)

def get_session_data():
  return read_json_file(r"./data/context_infor.json")


def set_medication_reminder(user_input,llm):
  chain = set_medication_reminder_prompt | llm
  medical_info = read_json_file(r"./data/medicationInfo.json")
  d = get_session_data()
  usercontext = d[0]
  llm_context = d[1]
  response = chain.invoke({"user_input": user_input,"medicalInfo":medical_info,"usercontext":usercontext, "llm_context":llm_context})
  data = parse_json_object(response.content)
  id = str(uuid.uuid4())  
  if(not data['reminder_set']):
    print(data['message'])
    return
  data['id'] = id
  medical_rem = read_json_file(r"./data/medicalremainder.json")
  medical_rem.append(data)
  write_json_file(r"./data/medicalremainder.json",medical_rem)
  print("I have added it to remainder!")
  return f"I have added it to remainder!{data}" 


def check_medication_schedule(user_input,llm):
  chain = check_medication_schedule_prompt | llm
  medicalremainder = read_json_file(r"./data/medicationInfo.json")
  d = get_session_data()
  usercontext = d[0]
  llm_context = d[1]
  response = chain.invoke({"user_input": user_input,"medicalremainder":medicalremainder, "usercontext":usercontext, "llm_context":llm_context})
  data = parse_json_object(response.content)
  print(data)
  return data


def get_medication_info(user_input,llm):
  chain = get_medication_info_prompt | llm
  medicationInfo = read_json_file(r"./data/medicationInfo.json")
  d = get_session_data()
  usercontext = d[0]
  llm_context = d[1]
  response = chain.invoke({"user_input": user_input,"medicationInfo":medicationInfo,"usercontext":usercontext, "llm_context":llm_context})
  data = parse_json_object(response.content)
  if(not data['medication_found']):
    print(data['message'])
    return
  print(data)
  return data


def log_medication_taken(user_input,llm):
  chain = record_medication_prompt | llm
  medical_info = read_json_file(r"./data/medicationInfo.json")
  medicine_take_for_a_day = read_json_file(r"./data/log_medication.json")
  d = get_session_data()
  usercontext = d[0]
  llm_context = d[1]
  response = chain.invoke({"user_input": user_input,"medical_info":medical_info,"medicine_take_for_a_day":medicine_take_for_a_day,"usercontext":usercontext, "llm_context":llm_context})
  data = parse_json_object(response.content)
  if(not data['medication_logged']):
    print(data['message'])
    return
  id = str(uuid.uuid4())
  # data.id = id
  data["id"] = id
  if(medicine_take_for_a_day == ''):
    medicine_take_for_a_day = []
  medicine_take_for_a_day.append(data)
  write_json_file(r"./data/log_medication.json", data)
  return identify_concern_medicine(llm)




def identify_concern_medicine(llm):
  chain = identify_concern_medicine_prompt | llm
  medicationInfo = read_json_file(r"./data/medicationInfo.json")
  log_medication = read_json_file(r"./data/log_medication.json")
  d = get_session_data()
  usercontext = d[0]
  llm_context = d[1]
  response = chain.invoke({"medicationInfo":medicationInfo,"log_medication":log_medication,"usercontext":usercontext, "llm_context":llm_context})
  data = parse_json_object(response.content)
  if(data['concern_identified']):
    arr = ["krishnasubedi219@gmail.com"]
    send_email(arr,"Concern Medication taken" , data['message'])
    return "Informed Concern Medication taken to a doctor!"
  return "I have noted and stored your medication information!"

def get_prescription_details(user_input, llm):
  chain = get_prescription_details_prompt | llm
  medical_info = read_json_file(r"./data/medicationInfo.json")
  d = get_session_data()
  usercontext = d[0]
  llm_context = d[1]
  response = chain.invoke({"medical_info":medical_info,"user_input":user_input,"usercontext":usercontext, "llm_context":llm_context})
  data = parse_json_object(response.content)
  if(not data['prescription_found']):
    print(data['message'])
    return
  print(data)
  return data