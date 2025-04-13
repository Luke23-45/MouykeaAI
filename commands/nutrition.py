#commands/nutrition.py
from langchain.prompts import PromptTemplate
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.nutritionService import log_meal, check_dietary_compliance, get_food_recommendation,general_nutritions, get_past_meals


command_recognition_prompt = PromptTemplate.from_template(
"""
Please choose the most relevant subcommand from the following list that best reflects your current need or request. Carefully read the detailed description for each option to make the correct selection. Once you have decided, please provide only the name of the chosen subcommand as your response.
**Subcommand Options and Descriptions:**
1.  **log_meal:**
    * **Purpose:** This subcommand is used to record information about a meal you have consumed.
    * **Input:** It expects detailed information about the meal, including:
        * A list of all food items consumed. For each item, please specify the name, quantity (e.g., in grams, ounces, or number of pieces), and preparation method (e.g., raw, cooked, fried, baked).
        * The time the meal was consumed (including date and time).
        * The location where the meal was consumed (e.g., home, restaurant, work).
        * Any notes or observations about the meal, such as how you felt before or after eating, or any specific details about the ingredients or preparation.
    * **Output/Action:** This subcommand will store the provided meal information for future reference and analysis. This data can be used for tracking your dietary habits, identifying nutritional patterns, and potentially for other features like dietary compliance checks or health concern identification.

2.  **check_dietary_compliance:**
    * **Purpose:** This subcommand is designed to assess whether your recent or planned food intake aligns with specific dietary guidelines, restrictions, or goals.
    - can i eat this or it is alright if I eat.
    if the user wishes or have desire to eat something.
    * **Input:** It requires the following information:
        * The specific dietary criteria you want to check against (e.g., a particular diet like keto, paleo, vegan, low-sodium, low-sugar, or specific health recommendations from a doctor regarding calorie intake, macronutrient ratios, or avoidance of certain allergens). Please be as specific as possible about the rules or guidelines.
        * The period for which you want to check compliance (e.g., the last 24 hours, today's planned meals, a specific date range). If you have already logged meals using the `log_meal` subcommand, you can refer to that data. Otherwise, you may need to provide details about the food items consumed or planned for the specified period.
    * **Output/Action:** This subcommand will analyze the provided or previously logged dietary information against the specified criteria and provide a report indicating the level of compliance. This report may highlight areas where your intake aligns with or deviates from the guidelines.
    

5.  **get_food_recommendation:**
    * **Purpose:** This subcommand is designed to provide specific food recommendations based on your current needs, preferences, or goals.
    * **Input:** Please provide detailed information about:
        * Your current dietary goals (e.g., lose weight, gain muscle, eat healthier, manage a specific condition like diabetes).
        * Your food preferences and restrictions (e.g., foods you like, foods you dislike, allergies, intolerances, dietary restrictions like vegetarian or gluten-free).
        * Any specific nutritional requirements or targets you are aiming for (e.g., increase protein intake, reduce sugar intake).
        * The type of meal or snack you are looking for a recommendation for (e.g., breakfast, lunch, dinner, snack).
    * **Output/Action:** This subcommand will analyze your input and provide a specific food or meal recommendation that aligns with your stated goals, preferences, and restrictions. It may also include basic nutritional information about the recommendation.


6. get_past_meals:
* Purpose: This subcommand is designed to provide user the past food that he has eaten or taken.
seeking information about their past meals. or what meals that they have eaten.
* Purpose:: This clearly states the intention or goal of this particular subcommand.
This subcommand is designed to provide user...: This tells us that the primary function of get_past_meals is to give information to the user. 
...the past food that he has eaten or taken.: This specifies the type of information the subcommand will provide:
past food: This implies a history or record of meals that has been tracked by the system.
that he has eaten or taken: This covers both regular meals (breakfast, lunch, dinner) and potentially other forms of nutritional intake, like snacks, drinks, or even supplements. The phrasing "eaten or taken" is inclusive.

7.  **general:**
    * **Purpose:** This subcommand is for general queries or requests that don't fit into any of the more specific categories.
    * **Input:** Please provide a clear and concise description of your question or request.
    * **Output/Action:** The system will attempt to understand your general query and provide a relevant response or guidance. This might involve answering a question about nutrition, providing general information, or directing you to a more specific subcommand if appropriate.

Once you have carefully considered the descriptions above, please type the name of the subcommand you wish to use (e.g., `log_meal`, `check_dietary_compliance`, etc.).

User Instruction: "{user_instruction}"
"""
)

def handleNutritionCommand(user_input,llm):
  chain = command_recognition_prompt | llm
  response = chain.invoke({"user_instruction": user_input})
  subcommand = response.content
  if(subcommand == 'log_meal'):
    return log_meal(user_input,llm)
  elif(subcommand == 'check_dietary_compliance'):
    return check_dietary_compliance(user_input,llm)
  elif(subcommand == 'get_food_recommendation'):
    return get_food_recommendation(user_input,llm)
  elif(subcommand == 'general'):
    return general_nutritions(user_input, llm)
  elif(subcommand == 'get_past_meals'):
    return get_past_meals(user_input, llm)

  

  
