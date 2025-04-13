#servies/nutritionService.py
from langchain.prompts import PromptTemplate
import json
import uuid
import re
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.fileUtils import read_json_file, write_json_file
from utils.sendEmail import send_email

command_recognition_prompt = PromptTemplate.from_template(
    """
You are a helpful assistant designed to log meal information provided by the user. Please extract the following details from the user's input and format them clearly.

**Meal Details:**
* **Food Items:** Please list each food item consumed. For each item, include:
    * Name: <name_of_food_item>
    * Quantity: <quantity_of_food_item> (e.g., 100 grams, 2 slices)
    * Preparation Method: <preparation_method> (e.g., raw, cooked, fried)
* **Time Consumed:** <date_and_time_of_meal> (Please be as specific as possible)
* **Location:** <location_where_meal_was_consumed> (e.g., home, restaurant)
* **Notes:** <any_additional_notes_or_observations> (e.g., felt full afterwards)

Please make sure that format should be json object.

User Instruction: "{user_instruction}"

Please provide the extracted information in the format specified above. If any information is missing or unclear, write the default value for them.
"""
)

command_identify_health_concerns = PromptTemplate.from_template(
    """
    "You are a medical assistant AI tasked with identifying potential health concerns based on a patient's medical profile and their recent meal.\n\n"
    "Patient Medical Information:\n"
    "{patient_info}\n\n"
    "Recent Meal Information:\n"
    "{meal_info}\n\n"
    "Analyze the recent meal in the context of the patient's medical conditions, allergies, intolerances, and dietary restrictions. "
    "Consider any potential negative interactions or foods that might be problematic given the patient's health profile.\n\n"
    "Identify any potential health concerns related to this meal. If there are no immediate concerns, please state that. "
    "Be specific and explain your reasoning based on the provided information.\n\n"
    "Potential Health Concerns:"
    "make the reponse concise"
    "use the natural tone"
    "behave like a doctor and you are telling in person this information to the person"
    "specify whether it needs to send_dietary_alert or not as boolean"
    "return the reponse as a json object"
"""
)

check_dietary_compliance_prompt = PromptTemplate.from_template(
   """
    "You are a helpful AI assistant tasked with checking if a user's meal complies with their doctor's dietary recommendations.\n\n"
    "Patient Medical and Dietary Information:\n"
    "{patient_info}\n\n"
    "Specifically, pay attention to any dietary restrictions, recommended food types, and foods to avoid mentioned in the patient information.\n\n"
    "User's Meal:\n"
    "\"{user_input}\"\n\n"
    "Analyze the user's meal and compare it to the dietary information provided.\n\n"
    "Respond with a JSON object in the following format:\n"
    
  {{
  "compliance_status": "Compliant",
  "reason": "A brief explanation if non-compliant, otherwise can be null or an empty string."
}}
    "If you are unsure about any aspect of the compliance, please indicate that in the \"reason\" field."
  use the polite tone and repected.
    """
)

get_food_recommendation_prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant that provides food recommendations tailored to a person's medical conditions and dietary needs.

Patient Medical and Dietary Information:
{patient_info}

User's Request:
{user_input}

Instructions:
- Consider the patient's medical conditions, allergies, intolerances, dietary restrictions, and any relevant doctor's notes.
- Recommend a food or meal that aligns with their health needs based on the provided information and request.
- If the request is too vague, ask the user for more details.

Respond with a concise recommendation.
return the reponse in json format with field
{{
Food Recommendation:"recommended food based on the patient information"
}}
  use the polite  and respected tone.
"""
)

gentle_prompt_template_unknown = PromptTemplate.from_template(
    """You are a helpful and gentle AI assistant designed to understand and respond to user instructions.
    "{llm_context} and {usercontext}" are only for contextual information. Only provide the context.

User Instruction: "{user_input}"

Please try your best to understand the user's instruction and provide a helpful answer or fulfill the request if it is clear and within your capabilities.

If the user's instruction is unclear, ambiguous, or if you are unable to directly answer the question or fulfill the request, please respond with a gentle and encouraging message such as:

"I'm sorry, I didn't quite understand your request. Could you please try rephrasing it in a different way?"

or

"Could you please say that again? I want to make sure I understand you correctly."

or

"Hmm, I'm not entirely sure what you meant by that. Could you please try explaining it using different words?"

Your gentle response if you cannot directly answer or fulfill the request:
"""
)

get_past_meals_prompt_template = PromptTemplate.from_template(
    """You are a helpful AI assistant designed to process user requests for past meal information.
    "{llm_context} and {usercontext}" are only for contextual information. Only provide the context.  
User Input: "{user_input}"


Note: if user has not given any exact time. or just seeking for past meal then we consider 7 days. 

Your goal is to understand the user's request and determine the number of past meal entries to retrieve. Please follow these guidelines:

1. **Identify the time frame:** Determine if the user is asking for meals from a specific number of days, weeks, months, or a specific number of past meals.

2. **Handle weeks:** If the user specifies a time frame in weeks, consider each week to be 7 days.

3. **Default meals per day:** Assume that there are 2 main meals per day for the calculation.

4. **Calculate the total number of meal times:** Based on the parsed time frame (in days or as a direct number of meals), calculate the total number of past meal entries to retrieve.

   * **For days, weeks, or months:** Calculate the number of days and then multiply by 2 (meals per day).
   * **For a specific number of past meals:** Directly use that number.

5. **Output JSON structure:** Return the result as a JSON object with a single field named "times". The value of "times" should be the total number of past meal entries calculated in the previous step.

**Examples:**

* User Input: "Show me my meals from the last 3 days."
  Output: `{{"times": 6}}` (3 days * 2 meals/day = 6)

* User Input: "What did I eat in the past week?"
  Output: `{{"times": 14}}` (1 week * 7 days/week * 2 meals/day = 14)

* User Input: "Retrieve my past five meals."
  Output: `{{"times": 5}}`

* User Input: "Meals from the last month." (Assume a month is 30 days for this calculation)
  Output: `{{"times": 60}}` (30 days * 2 meals/day = 60)

Based on the User Input provided: "{user_input}"

Determine the value for the "times" field in the JSON output.

JSON Output:
"""
)

def get_session_data():
  return read_json_file(r"./data/context_infor.json")

def parse_json_object(input_str):
    pattern = r"```json\s*(.*?)\s*```"
    match = re.search(pattern, input_str, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        json_str = input_str
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError("Failed to parse JSON") from e

def log_meal(user_input,llm):
  chain = command_recognition_prompt | llm
  response = chain.invoke({"user_instruction": user_input})
  data = parse_json_object(response.content)
  id = str(uuid.uuid4())
  data["id"] = id
  old_data = read_json_file(r"./data/log_meal.json")
  old_data.append(data)
  write_json_file(r"./data/log_meal.json", old_data)
  print("I have noted and stored your meal information!")
  return identify_health_concerns(data,llm)
  
def identify_health_concerns(data,llm):
  chain = command_identify_health_concerns | llm
  patient_info = read_json_file(r"./data/identify_health_concerns.json")
  response = chain.invoke({"meal_info": data,"patient_info":patient_info})
  data_ = parse_json_object(response.content)
  print(data_['Potential Health Concerns'])
  if(data_['send_dietary_alert']):
    arr = ["krishnasubedi219@gmail.com"]
    send_email(arr,"Potential Health Concerns Report" , data_['Potential Health Concerns'])
    return "Potential Health Concerns Report"
  return data

def check_dietary_compliance(user_input,llm):
  chain = check_dietary_compliance_prompt | llm
  patient_info = read_json_file(r"./data/identify_health_concerns.json")
  response = chain.invoke({"user_input": user_input,"patient_info":patient_info})
  data_ = parse_json_object(response.content)
  print(data_)
  return data_

def get_food_recommendation(user_input,llm):
  chain = get_food_recommendation_prompt | llm
  patient_info = read_json_file(r"./data/identify_health_concerns.json")
  response = chain.invoke({"user_input": user_input,"patient_info":patient_info})
  data_ = parse_json_object(response.content)
  print(data_)
  return data_

def general_nutritions(user_input,llm):
  chain = gentle_prompt_template_unknown | llm
  d = get_session_data()
  usercontext = d[0]
  llm_context = d[1]
  response = chain.invoke({"user_input": user_input,"usercontext":usercontext, "llm_context":llm_context})
  print(response)
  return (response.content)

def extract_name_quantity(meals):
    result = []
    for meal in meals:
        food_items = meal.get("Meal Details", {}).get("Food Items", [])
        for item in food_items:
            result.append({
                "Name": item.get("Name"),
                "Quantity": item.get("Quantity")
            })
    return result
def get_past_meals(user_input,llm):
  chain = get_past_meals_prompt_template | llm
  d = get_session_data()
  usercontext = d[0]
  llm_context = d[1]
  response = chain.invoke({"user_input": user_input,"usercontext":usercontext, "llm_context":llm_context})
  data_ = int(parse_json_object(response.content)['times'])
  old_data = read_json_file(r"./data/log_meal.json")
  len_ = len(old_data)
  if(len_ > data_):
     return extract_name_quantity(old_data)
  return extract_name_quantity(old_data[-data_:])
  