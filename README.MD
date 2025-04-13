## Elderly Care Voice Command AI Assistant - Documentation

This document outlines the functionalities and usage of the Elderly Care Voice Command AI Assistant, designed to help elderly individuals manage their daily tasks, access information, and stay connected.

**I. Core Functionalities:**

The AI Assistant is designed to understand and respond to voice and text commands, categorized into several key areas:

**1. Nutrition Management:**

* **Description:** This category handles tasks related to the user's dietary intake, nutritional information, and meal tracking.

    * **Subcommand: `log_meal`**
        * **Purpose:** To record the food and drinks the user has consumed.
        * **User Input Examples:**
            ```text
            "I have eaten some fruits and vegetables."
            "I had a bowl of oatmeal for breakfast at 7 AM."
            "I have eaten 1kg suger and rice."  # Concern Case
            "For lunch, I had a sandwich and a glass of water."
            "I drank a cup of tea."
            ```
        * **Expected Behavior:** The AI should acknowledge the logged meal and store the information. In the "Concern Case" example ("1kg suger and rice"), a more advanced system would ideally flag this as potentially unhealthy, perhaps prompt for confirmation, suggest consulting a healthcare professional, or even trigger a notification to a caregiver based on predefined rules.

    * **Subcommand: `check_dietary_compliance`**
        * **Purpose:** To allow the user to ask if a particular meal plan or food choice aligns with their dietary needs or restrictions (if known by the system).
        * **User Input Examples:**
            ```text
            "Breakfast: Scrambled eggs with spinach and avocado. Lunch: Grilled chicken salad with olive oil dressing. Dinner: Steak with roasted asparagus and butter. Can I eat it?"
            "Is it okay for me to have a piece of chocolate cake?"
            "I am thinking of having fish and chips for dinner. Is that a good choice?"
            ```
        * **Expected Behavior:** The AI should analyze the provided meal or food against the user's dietary profile (if available) and provide a response indicating compliance or suggesting alternatives if necessary. The AI would need prior knowledge of dietary restrictions (e.g., diabetes) to answer accurately.

    * **Subcommand: `recommend_food`**
        * **Purpose:** To provide the user with healthy food suggestions based on the time of day, their preferences (if known), or general health guidelines.
        * **User Input Examples:**
            ```text
            "Can you suggest a healthy breakfast for me?"
            "I'm feeling like a snack. What do you recommend?"
            "Give me some ideas for a light dinner."
            "Suggest some foods that are good for my heart."
            ```
        * **Expected Behavior:** The AI should provide relevant and healthy food suggestions based on the context of the user's request.

    * **Subcommand: `get_past_meals`**
        * **Purpose:** To retrieve and inform the user about their previous food intake over a specified period.
        * **User Input Examples:**
            ```text
            "Can you tell me what I have eaten over the past 4 days?"
            "What did I have for dinner last night?"
            "Show me my meals from the beginning of the week."
            "What were my snacks yesterday?"
            ```
        * **Expected Behavior:** The AI should access the logged meal history and provide the user with the requested information.

**2. Communication Assistance:**

* **Description:** This category enables the user to communicate with their contacts (family, caregivers, etc.) through voice or text commands.

    * **Subcommand: `send_message`**
        * **Purpose:** To send a message to a specified contact.
        * **User Input Examples:**
            ```text
            "Can you tell my daughter I will be late for dinner tonight?"
            "Send a message to John saying I'm feeling a bit unwell."
            "Text Sarah and tell her I had a good walk today."
            "Email my caregiver about my appointment."
            "Send a voice note to my neighbor." # (Requires voice note capability)
            "Inform my son that I've taken my medication."
            "Ask my daughter if she can visit tomorrow."
            "Notify the nurse that I need assistance." # (May trigger specific protocols)
            "Tell my friend I'm thinking of them."
            "Send a reminder to my grandson about my birthday."
            ```
        * **Examples Requiring Clarification:**
            ```text
            "Can you tell I will be late for dinner tonight?" # (Missing recipient)
            "Message my son that..." # (Incomplete message)
            "Call the doctor." # (Ambiguous which doctor, or if 'call' is supported vs. 'message')
            ```
        * **Expected Behavior:** The AI should identify the contact (e.g., daughter, John, Sarah, caregiver) and send the specified message using the configured communication method (e.g., SMS, email, in-app message). If the recipient or the message content is missing or unclear, the AI should prompt for clarification (e.g., "Who would you like to send this message to?", "What would you like to say to your son?").

**3. Medication Management:**

* **Description:** This category helps the user manage their medications, including setting reminders and checking their schedule.

    * **Subcommand: `set_medication_reminder`**
        * **Purpose:** To create a reminder for taking a specific medication at a particular time.
        * **User Input Examples:**
            ```text
            "Remind me to take my Metformin at 8 PM."
            "Set a reminder for my blood pressure pill at 7:30 in the morning."
            "Remind me to take my Vitamin D after lunch."
            "Can you set a reminder for my eye drops at 6 PM daily?"
            ```
        * **Expected Behavior:** The AI should schedule a reminder for the specified medication and time.

    * **Subcommand: `check_medication_schedule`**
        * **Purpose:** To provide the user with a list of their scheduled medications and their respective times.
        * **User Input Examples:**
            ```text
            "Please provide me the medication schedule that I have asked to schedule. List the schedule medicine."
            "What medications am I supposed to take today?"
            "When do I need to take my next dose of Aspirin?"
            "Show me my medication reminders for the evening."
            ```
        * **Expected Behavior:** The AI should retrieve and present the user's medication schedule based on previously set reminders.

    * **Subcommand: `log_medication_taken`**
        * **Purpose:** To record when the user has taken a particular medication.
        * **User Input Examples:**
            ```text
            "Can you record that I have taken Profen at 8:00 PM."
            "I have just taken my morning pills."
            "Log that I took my Metformin now."
            "I took my eye drops a few minutes ago."
            ```
        * **Expected Behavior:** The AI should record the medication (if specified) and the time it was taken. It could potentially cross-reference with scheduled reminders.

    * **Subcommand: `get_medication_info`**
        * **Purpose:** To provide the user with information about a specific medication (e.g., dosage, purpose, side effects - this would require integration with a reliable medical information source).
        * **User Input Examples:**
            ```text
            "Please provide me the medication information about Profen."
            "Tell me more about what Metformin is for."
            "What are the possible side effects of my blood pressure medication?"
            "What is the usual dosage for Aspirin?"
            ```
        * **Expected Behavior:** The AI should retrieve and provide information about the requested medication from its knowledge base or integrated source. **Important Note:** The AI should always advise users to consult their doctor or pharmacist for definitive medical advice and information, especially regarding side effects, interactions, or dosage adjustments.

    * **Subcommand: `get_prescription_details`**
        * **Purpose:** To provide details about a user's prescription (requires system integration).
        * **User Input Examples:**
            ```text
            "Can you tell me about Metformin prescription!"
            "When is my prescription for Lisinopril due to be refilled?"
            "What is the dosage on my current prescription for my pain medication?"
            ```
        * **Expected Behavior:** If the system has access to the user's prescription data (with appropriate permissions and privacy safeguards), the AI should access these details and provide the requested information (e.g., refill dates, dosage).

**4. Emotional and Social Support:**

* **Description:** This category focuses on providing companionship and support for the user's emotional well-being.

    * **Subcommand: `handle_emotional_support`**
        * **Purpose:** To engage in conversation, offer comfort, or connect the user with social resources if they express feelings of loneliness or sadness.
        * **User Input Examples:**
            ```text
            "I feel lonely today. Can you chat with me?"
            "I'm feeling a bit down."
            "I'm having a difficult day."
            "Can you tell me a joke?"
            "Play some calming music."
            ```
        * **Expected Behavior:** The AI should respond with empathy, engage in simple, supportive conversation, offer comforting words, fulfill simple requests like telling a joke or playing music, or potentially suggest contacting a friend/family member or a support line if programmed to do so.

**5. Cognitive Support:**

* **Description:** This category assists with memory and cognitive tasks.

    * **Subcommand: `set_cognitive_activity_reminder`**
        * **Purpose:** To set reminders for cognitive activities or tasks.
        * **User Input Examples:**
            ```text
            "Help me remember to do my puzzles at 9:00 PM."
            "Remind me to read for 30 minutes at 10 AM."
            "Set a reminder to call my friend at 3 in the afternoon."
            "Help me remember to do my puzzles at 8:00 AM."
            ```
        * **Expected Behavior:** The AI should set a reminder for the specified activity and time.

    * **Subcommand: `check_cognitive_activity_reminders`**
        * **Purpose:** To allow the user to check their scheduled cognitive activity reminders.
        * **User Input Examples:**
            ```text
            "When did I set the puzzle activity to remind me?"
            "What cognitive activities do I have scheduled for today?"
            "Remind me what I planned to do this afternoon."
            ```
        * **Expected Behavior:** The AI should retrieve and list the user's scheduled cognitive activity reminders.

    * **Subcommand: `provide_cognitive_exercise`**
        * **Purpose:** To offer simple cognitive exercises or prompts to stimulate mental activity.
        * **User Input Examples:**
            ```text
            "Give me a simple memory exercise."
            "Can you ask me a riddle?"
            "Suggest a brain-training activity."
            ```
        * **Expected Behavior:** The AI should provide an appropriate cognitive exercise, riddle, or suggestion for a brain-training activity based on its capabilities.

**6. General Information:**

* **Description:** This category handles general knowledge queries that don't fall into the other specific categories.

    * **Subcommand: `get_weather`**
        * **Purpose:** To provide the user with current weather information.
        * **User Input Examples:**
            ```text
            "What's the weather like today?"
            "Will it rain tomorrow?"
            "What's the temperature outside?"
            ```
        * **Expected Behavior:** The AI should fetch and provide current and/or forecasted weather information for the user's presumed location (or ask for location if needed).

    * **Subcommand: `get_news`**
        * **Purpose:** To provide the user with top news stories.
        * **User Input Examples:**
            ```text
            "What are the top news story of today?"
            "Tell me the latest headlines."
            "What's happening in the world?"
            ```
        * **Expected Behavior:** The AI should fetch and present current news headlines from a configured news source.

    * **Subcommand: `get_news_details`**
        * **Purpose:** To provide more information about a specific news story mentioned or requested by the user.
        * **User Input Examples:**
            ```text
            "Tell me more about the news: President Xi's Southeast Asia visits set to inject new impetus into regional development"
            "Can you elaborate on the top story?"
            "Tell me more about the election results."
            ```
        * **Expected Behavior:** The AI should attempt to find and provide more details or a summary about the specified news topic or headline.

    * **Subcommand: `explain_concept`**
        * **Purpose:** To explain general concepts or answer factual questions.
        * **User Input Examples:**
            ```text
            "Explain what AI is in detail. What is it?"
            "What is the capital of Nepal?"
            "Tell me about the history of the internet."
            "How does photosynthesis work?"
            ```
        * **Expected Behavior:** The AI should access its knowledge base to provide a clear and accurate explanation or answer to the user's general knowledge question.

**II. Handling Invalid or Unclear Input:**

When the AI receives input that it cannot understand or classify into any of the defined command categories, or if the input is ambiguous, it should respond gently and prompt the user for clarification. Examples of such responses include:

```text
"I'm sorry, I didn't quite understand your request. Could you please try rephrasing it?"
"Could you please say that again in a different way?"
"Hmm, I'm not entirely sure what you meant by that. Could you please try explaining it using different words?"
"Who would you like to send that message to?"
"What medication would you like information about?"
```
**III. Conclusion:**

The Elderly Care Voice Command AI Assistant aims to provide a user-friendly and helpful interface for elderly individuals to manage their daily lives, stay informed, and feel more connected. By understanding and responding to a variety of voice and text commands, the AI can contribute to increased independence and well-being for its users.
