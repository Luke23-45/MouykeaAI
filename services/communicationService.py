from langchain.prompts import PromptTemplate
import sys
import os
import json
import re
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.fileUtils import read_json_file, write_json_file
from utils.sendEmail import send_email
send_email_prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant tasked with extracting information to send an email.
  "{llm_context} and {usercontext}" are only for contextual information. Only provide the context.
User's Instruction: "{user_input}"

Identify the recipient, subject (if provided), and body of the email from the user's instruction.

Respond with a JSON object in the following format:
if all infomation is provided then return the reponse in following format.
in the field "recipient" just will be just the name. Not the actual email address. Just write only the "recipient" name or how they address "recipient". Like if it mention "son" then the it will son. It is mention a full name like "Luke Green" then it will be "Luke Green".
if the user_input contains "daughter" or "son" then recipient will be respectively.
for the subject add based on the context(based on the body of an email).
{{
  "recipient": "...",
  "subject": "...",
  "body": "...",
  "valid_email":"if the body and recipient fields are available then set it to true otherwise false "
}}

if any information mention above is not provided then please gently urges them to include them. 
Write the gentle messages.
if any information is missing the return the following reponse only.
{{
  "message":"gently urges them to include the missing fields",
  "valid_email":"if the body or recipient field is missing any one of them then set it to false otherwise true "
}}
"""
)

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
def get_session_data():
  return read_json_file(r"./data/context_infor.json")


def handleCommunicationService(user_input,llm):
  print(user_input)
  d = get_session_data()
  usercontext = d[0]
  llm_context = d[1]
  chain = send_email_prompt | llm
  email_list = read_json_file(r"./data/emails.json")
  conversation_list = read_json_file(r"./data/conversation.json")
  response = chain.invoke({"user_input": user_input,"usercontext":usercontext, "llm_context":llm_context})
  data_ = parse_json_object(response.content)
  print(data_)
  if(not (data_['valid_email'])):
    return "Please specify the person or provide the message!"
  if f"{data_['recipient']}" not in email_list:
      print("I could not find that person in your contact list!")
      return "I could not find that person in your contact list!"
  else:
      receiver = email_list[f"{data_['recipient']}"]
      send_email([receiver],data_['subject'], data_['body'])
      id = str(uuid.uuid4())
      data_['id'] = id
      conversation_list.append(data_)
      write_json_file(r"./data/conversation.json",conversation_list)
      return data_

      