import sys
import os
from langchain.prompts import PromptTemplate
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.parseJson import parse_json_object
from services.cognitiveService import set_cognitive_activity_reminder,check_cognitive_activity_reminders



cognitive_support_prompt = PromptTemplate.from_template(
  """You are a helpful AI assistant designed to provide cognitive support to elderly individuals. Your task is to understand the user's request and determine the appropriate action or function to call.

**User's Instruction:**
"{user_input}"

Based on the user's instruction, determine which of the following categories of cognitive support they are requesting and respond accordingly.

**Possible Cognitive Support Actions:**


3.  **Cognitive Activity Reminders:** Ic
    * Example User Input: "Remind me to do my crossword puzzle at 3 PM." or "Set a reminder to read my book later."
    If the user asks to remember something or recall something they've forgotten.
    * Example User Input: "Please remember that my doctor's appointment is on Tuesday at 10 AM."
    * Potential Function to Call: `set_cognitive_activity_reminder`

check_cognitive_activity_reminders:
This function handles user inquiries about scheduled reminders for cognitive activities—such as puzzles, reading sessions, or appointments—that have previously been set or the activities before. It is specifically designed to respond when a user asks whether any cognitive tasks are scheduled or to retrieve details of what they asked to be reminded about.

Example User Inputs:

"What cognitive activities do I have reminders for?"

"Do I have any reminders for puzzles or reading today?"

"Which appointments have been scheduled for me?"


Potential Function to Call: check_cognitive_activity_reminders



Analyze the user's instruction and, if it clearly falls into one of the above categories, indicate the category and the potential function to call. If it's a general knowledge question, provide a brief answer directly. For memory-related requests, acknowledge the request. For exercise or activity reminders, confirm the reminder.

If the request is unclear or doesn't fit into these categories, you can ask for clarification.

**Response Guidelines:**

For memory requests: "Okay, I will remember that for you." or "Let me check my memory..."

For exercise requests: "Here is a mental exercise for you..." (and potentially provide it).

For activity reminders: "I will set a reminder for you."

For general knowledge: Provide the answer directly.

For unclear requests: "Could you please provide more details?"
please provide the response in the proper json structure.
"""
)

def handleCognitiveCommand(user_input, llm):
  chain = cognitive_support_prompt | llm
  response = chain.invoke({"user_input": user_input})
  data = parse_json_object(response.content)
  key = data['function_to_call']
  if(key == 'set_cognitive_activity_reminder'):
    return set_cognitive_activity_reminder(user_input,llm)
  if(key == "check_cognitive_activity_reminders"):
    return check_cognitive_activity_reminders(user_input, llm)


