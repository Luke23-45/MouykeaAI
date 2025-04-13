
import requests
from langchain.prompts import PromptTemplate
from utils.parseJson import parse_json_object
import xml.etree.ElementTree as ET
import urllib.parse
from utils.fileUtils import read_json_file


get_weather_information_prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant designed to provide weather information.

**User's Request:**
"{user_input}"

Your task is to understand the user's request and provide the current weather information for the specified location.
1.  **Identify Location:** Check if the user's request explicitly mentions a location.
2.  **Default Location:** If no location is specified in the user's request, assume the location is Kathmandu, Nepal.
3.  **Retrieve Weather:** Once the location is determined, provide the current weather conditions for that location. Include details such as:
    * Temperature (in Celsius)
    * Sky condition (e.g., sunny, cloudy, rainy)
    * Humidity
    * Wind speed (if available)
    * Any other relevant weather information.
Format your response as a concise weather report.
**Example Responses:**
* User Input: "What's the weather like?"
    Response: "The current weather in Kathmandu, Nepal is [Temperature] with [Sky condition]. Humidity is [Humidity] and wind speed is [Wind speed]."

* User Input: "Tell me the weather in Pokhara."
    Response: "The current weather in Pokhara is [Temperature] with [Sky condition]. Humidity is [Humidity] and wind speed is [Wind speed]."

Provide the weather information based on the user's request, defaulting to Kathmandu if no location is mentioned.

return the response in the proper json structure.
"""
)

route_news_prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant tasked with routing user news inquiries to the appropriate function.

Available Functions:

- `get_top_news_summary(user_id)`: Use this function when the user asks for the top news of today.
- `get_news_summary(user_id, topic)`: Use this function when the user asks for news about a specific topic or a summary of a particular news story.

User Input:
"{user_input}"

Analyze the user's input to determine which of the available functions is the most appropriate to handle the request.

Respond ONLY with a JSON object in one of the following formats:

Format 1: For Top News
{{"function_to_call": "get_top_news_summary"}}

Format 2: For Specific News or Topic
{{"function_to_call": "get_news_summary", "topic": "..." }}

In this format, the "topic" field should contain the specific topic or keywords the user is interested in (e.g., "politics", "earthquake in Nepal", "the latest on the economy").

Format 3: Unknown Request
{{"function_to_call": "unknown"}}

Examples:

User Input: "What's the top news today?"
Response:
{{"function_to_call": "get_top_news_summary"}}

User Input: "Tell me the news about the weather in Kathmandu."
Response:
{{"function_to_call": "get_news_summary", "topic": "weather in Kathmandu"}}

User Input: "Give me a summary of the latest on the Nepal stock market."
Response:
{{"function_to_call": "get_news_summary", "topic": "Nepal stock market"}}

User Input: "What are the current events?"
Response:
{{"function_to_call": "get_top_news_summary"}}

User Input: "Remind me to drink water."
Response:
{{"function_to_call": "unknown"}}

Analyze the user's input carefully and provide the JSON response indicating the function to call and the topic (if applicable). Do not include any explanation, only provide the JSON object.
"""
)


extract_general_question_topic_prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant tasked with analyzing a user's question and extracting the main subject or topic of the question.
  "{llm_context} and {usercontext}" are only for contextual information. Only provide the context.
User's Question:
"{user_input}"

Your goal is to identify the core subject or topic that the user is asking about in their question.

Response Format:

1. Topic Found: If you can clearly identify a subject or topic in the user's question, return a JSON object in the following format:
{{
  "topic_found": true,
  "topic": "...",
  "type_of_topic":"fact type(general infomation) or description type(need explanation). if it is a fact type then write fact and if it is type then write description type"
}}

The "topic" field should contain a concise description of the main subject of the user's question.

2. No Clear Topic Found: If the user's question is very general, a greeting, or does not have a clear subject that can be easily extracted, return a JSON object in the following format:
{{
  "topic_found": false
}}

Examples:

User Input: "What is the capital of France?"
Response:
{{ "topic_found": true, "topic": "capital of France" }}

User Input: "What time is it?"

User Input: "Hello"
Response:
{{ "topic_found": false }}

User Input: "Explain the theory of relativity."
Response:
{{ "topic_found": true, "topic": "theory of relativity" }}

Analyze the user's question and respond with the appropriate JSON object indicating whether a topic was found and, if so, what the topic is."""
)

provide_topic_information_prompt = PromptTemplate.from_template(
    """You are a helpful AI assistant designed to provide information on various topics.

**User's Topic:**
"{topic}"

Based on the topic provided, generate a comprehensive and informative response. Include relevant details, key aspects, and any interesting facts related to "{topic}".

Your response should be well-structured and easy for an elderly person to understand. You can organize your response into logical paragraphs or bullet points if appropriate.

For example, if the topic is "game engines", you could discuss what they are, their purpose, some popular examples, and their importance in game development.

Please provide a detailed explanation of "{topic}".
return the response into the json data.

"""
)

provide_topic_information_prompt_for_fact = PromptTemplate.from_template(
    """You are a helpful AI assistant designed to provide fact-based information on various topics.

User's Topic:
"{topic}"

Return your response as a JSON object in the following format:
{{
  "information": "since it is a fact. only provide what it is asking. No explanation."
}}
"""
)

def get_session_data():
  return read_json_file(r"./data/context_infor.json")

def get_top_news_summary():
    try:
        # BBC News RSS feed
        url = "http://feeds.bbci.co.uk/news/rss.xml"
        response = requests.get(url)

        if response.status_code == 200:
            root = ET.fromstring(response.content)

            items = root.findall(".//item")
            
            # Get the top 5 headlines
            headlines = []
            for item in items[:8]:
                title = item.find("title").text
                headlines.append(f"- {title}")

            summary = "Top News Headlines:\n" + "\n".join(headlines)
            return summary
        else:
            return "Could not fetch news at the moment."
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return "Failed to connect to the news service."
    
def get_news_summary_from_topic( user_input):
    try:
        query = urllib.parse.quote(user_input)
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(url)

        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall(".//item")
            if not items:
                return f"No news found for '{user_input}'."
            headlines = []
            for item in items[:5]:
                title = item.find("title").text
                headlines.append(f"- {title}")

            summary = f"Top News about '{user_input}':\n" + "\n".join(headlines)
            return summary
        else:
            return "Could not fetch news at the moment."
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return "Failed to connect to the news service."

def get_weather_information( user_input):
    try:
        url = f"https://wttr.in/{user_input}?format=j1" 
        response = requests.get(url)

        if response.status_code == 200:
            return response.text.strip()
        else:
            return "Could not fetch weather information at the moment."
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather: {e}")
        return "Failed to connect to the weather service."
def get_weather_information(user_input,llm):
  chain =  get_weather_information_prompt | llm
  response = chain.invoke({"user_input": user_input})
  data = parse_json_object(response.content)
  print( data )
  return data


def get_news_summary(user_input,llm):
  chain =  route_news_prompt | llm
  response = chain.invoke({"user_input": user_input})
  data = parse_json_object(response.content)
  print( data['function_to_call'] )
  if(data['function_to_call'] == 'get_top_news_summary'):
      top_news = get_top_news_summary()
      print(top_news)
      return top_news
  if(data['function_to_call'] == 'get_news_summary'):
      summery_news = get_news_summary_from_topic(data['topic'])
      print(summery_news)
      return summery_news

def get_general_information(topic,llm):
  chain = provide_topic_information_prompt | llm
  response = chain.invoke({"topic": topic})
  data = parse_json_object(response.content)
  return data

def get_fact_information(topic,llm):
  print(topic)
  chain = provide_topic_information_prompt_for_fact | llm
  response = chain.invoke({"topic": topic})
  data = parse_json_object(response.content)
  return data
def answer_general_question(user_input,llm):
  d = get_session_data()
  usercontext = d[0]
  llm_context = d[1]
  chain =  extract_general_question_topic_prompt | llm
  response = chain.invoke({"user_input": user_input,"usercontext":usercontext, "llm_context":llm_context})
  data = parse_json_object(response.content)
  print(data)
  if(not data['topic_found']):
      print("topic could not be found!")
  print(data['topic'])
  if(data['type_of_topic'] == 'description type'):
    data_ = get_general_information(data['topic'],llm)
    print(data_)
    return data_
  if(data['type_of_topic'] == 'fact' or data['type_of_topic'] == 'fact type'):
      data_ = get_fact_information(data['topic'],llm)
      print(data_)
      return data_
  
