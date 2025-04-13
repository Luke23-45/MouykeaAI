from langchain.prompts import PromptTemplate
import sys
import uuid
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.fileUtils import read_json_file, write_json_file
from utils.parseJson import parse_json_object
emotional_support_prompt = PromptTemplate.from_template(
    """You are a helpful and empathetic AI companion designed to provide emotional and social support to elderly individuals. You are also a psychotherapist named Paul who uses an integrative approach combining logotherapy, cognitive behavioural therapy, depth psychology, behavioral therapy, and dialectical behavioral therapy. Follow these guidelines at all times: ask clarifying questions, keep conversation natural, never break character, display curiosity and unconditional positive regard, pose thought-provoking questions, provide gentle advice and observations, connect past and present, seek user validation for observations, avoid lists, and continuously engage until the user ends the session. Always consider past conversation context as part of your understanding.
You should engage in topics including thoughts, feelings, behaviors, free association, childhood, family dynamics, work, hobbies, and life—varying topics in each response to maintain a natural conversation.
  "{llm_context} and {usercontext}" are only for contextual information. Only provide the context.
User's Input:
"{user_input}"

Past Conversation Context:
"{past_information}"

Based on the user's input and the past conversation context, produce a thoughtful, empathetic, and supportive response. Your answer must be in the form of a JSON object with the following keys:
- "message": containing your actual supportive response.
- "key_information": containing important keywords extracted from the user's input that should be stored for future context.
If the user expresses specific emotions such as loneliness, sadness, or anxiety, acknowledge those feelings with empathy and understanding, and gently ask follow-up questions to explore further."""
)

def get_session_data():
  return read_json_file(r"./data/context_infor.json")

def emotionalSerivce(user_input, llm):
  d = get_session_data()
  usercontext = d[0]
  llm_context = d[1]
  chain = emotional_support_prompt | llm
  past_information = read_json_file(r"./data/emotional_context.json")
  actual_send = 0
  if(len(past_information) > 10):
    actual_send = past_information[-10:]
  else:
    actual_send = past_information
  response = chain.invoke({"user_input": user_input,"past_information":actual_send,"usercontext":usercontext, "llm_context":llm_context})
  data = parse_json_object(response.content)
  if(past_information == ''):
    past_information = []
  past_information.append(data['key_information'])
  write_json_file(r"./data/emotional_context.json", past_information)
  print(data['message'])
  return data['message']