import sys
import os
from langchain.prompts import PromptTemplate
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.parseJson import parse_json_object
from services.generalInfoService import get_weather_information, get_news_summary, answer_general_question


route_general_information_prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant tasked with routing user inquiries to the correct function for general information.

Available Functions:
- get_weather_information(user_id, user_input): Use this function when the user asks about the weather.
- get_news_summary(user_id, user_input): Use this function when the user asks for a summary of the latest news or generally asking about the news.
- answer_general_question(user_id, user_input): Use this function for all other general knowledge questions that are not specifically about weather or news.

User's Input:
"{user_input}"

Your task is to analyze the user's input and determine which of the above functions best handles the request. Your response must be a JSON object with a single key "function_to_call", whose value is exactly the name of the function to call.

If the input does not clearly match any of the defined categories, respond with:
{{
  "function_to_call": "unknown"
}}

Examples:

User Input: "What's the weather like today?"
Response:
{{
  "function_to_call": "get_weather_information"
}}

User Input: "Tell me the latest headlines."
Response:
{{
  "function_to_call": "get_news_summary"
}}

User Input: "What is the capital of France?"
Response:
{{
  "function_to_call": "answer_general_question"
}}


Analyze the user's input and provide the JSON response indicating the function to call."""
)

def handleGeneralCommand(user_input, llm):
  chain = route_general_information_prompt | llm
  response = chain.invoke({"user_input": user_input})
  data = parse_json_object(response.content)
  key = data['function_to_call']
  if(key == 'get_weather_information'):
    return get_weather_information(user_input, llm)
  elif(key == "get_news_summary"):
    return get_news_summary(user_input,llm)
  else:
    return answer_general_question(user_input,llm)
