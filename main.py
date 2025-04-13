# main.py
import os
import json
import io
import sys
import numpy as np
from pydub import AudioSegment
from gtts import gTTS
from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
from flask_cors import CORS
from functools import wraps
from utils.fileUtils import read_json_file, write_json_file
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'user_data_uploads')
ALLOWED_EXTENSIONS = {'json'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
try:
    from utils.api_key import get_api_key
    from utils.fileUtils import read_json_file
except ImportError as e:
    print(f"Error importing from utils: {e}")
    print("Ensure utils directory and its files (api_key.py, fileUtils.py) are accessible.")

try:
    import services.authService as auth_service
    print("Successfully imported authService.")
except ImportError:
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.abspath(os.path.join(current_dir, '..'))

    if os.path.exists(os.path.join(parent_dir, './services/authService.py')):
        sys.path.insert(0, parent_dir)

    services_dir = os.path.abspath(os.path.join(current_dir, '..', 'services'))
    if os.path.exists(os.path.join(services_dir, './services/authService.py')):
        # Add parent to import services
        sys.path.insert(0, os.path.abspath(os.path.join(current_dir, '..')))

    try:
        import services.authService as auth_service
        print("Successfully imported authService after path adjustment.")
    except ImportError as e:
        print(f"Error importing authService after path adjustments: {e}")
        print("Searched in:", sys.path)
        print("Ensure authService.py is accessible in the Python path.")
        sys.exit(1)
try:
    from commands.nutrition import handleNutritionCommand
    from commands.communication import handleCommunicationCommand
    from commands.medication import handleMedicationCommand
    from commands.emotional import handleEmotionalCommand
    from commands.cognitive import handleCognitiveCommand
    from commands.generalInfo import handleGeneralCommand
except ImportError as e:
    print(f"Error importing command handlers: {e}")
    print("Ensure the 'commands' directory and its handler files exist and are accessible.")
try:
    from langchain.prompts import PromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema.runnable import RunnablePassthrough, RunnableMap
except ImportError as e:
    print(f"Error importing Langchain components: {e}")
    print("Ensure langchain, langchain-google-genai are installed.")
    sys.exit(1)
try:
    from faster_whisper import WhisperModel
except ImportError as e:
    print(f"Error importing faster_whisper: {e}")
    print("Ensure faster-whisper is installed.")
try:
    os.environ["GOOGLE_API_KEY"] = get_api_key('API_KEY')
    print("GOOGLE_API_KEY loaded.")
except Exception as e:
    print(f"Error setting up environment variables: {e}")
    print("Ensure get_api_key works or set GOOGLE_API_KEY manually.")
    sys.exit(1)
try:
    auth_service.initialize_session()
    print("Authentication session initialized.")
except Exception as e:
    print(f"CRITICAL ERROR initializing authentication session: {e}")
    sys.exit(1)
whisper_model = None
try:
    whisper_model_name = "base.en"
    print(f"Loading Whisper model: {whisper_model_name}...")
    whisper_model = WhisperModel(
        whisper_model_name, device="cpu", compute_type="int8")
    print("Whisper model loaded successfully.")
except Exception as e:
    print(f"Error loading Whisper model '{whisper_model_name}': {e}")
    print("Audio processing will be unavailable.")
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
    )
    print("Google Generative AI LLM initialized.")
except Exception as e:
    print(f"Error initializing Google Generative AI LLM: {e}")
    sys.exit(1)
app = Flask(__name__)
CORS(app)
print("Flask app initialized with CORS enabled.")
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_user = auth_service.get_session_user()
        if not session_user or not isinstance(session_user, dict) or not session_user.keys():
            print("Access denied: No active session user found.")
            # Consistent error format
            return jsonify({'error': 'Authentication required. Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated_function
def process_audio_file(audio_bytes):
    if whisper_model is None:
        print("Whisper model not loaded. Cannot process audio.")
        return ""
    try:
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
        raw_audio_data = audio_segment.raw_data
        audio_np = np.frombuffer(
            raw_audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        segments, info = whisper_model.transcribe(audio_np, language='en')
        print(
            f"Detected language '{info.language}' with probability {info.language_probability}")

        transcription = "".join(segment.text for segment in segments).strip()
        print(f"Transcription successful: '{transcription}'")
        return transcription

    except Exception as e:
        print(f"Error processing audio file: {e}")
        return ""  # Return empty string on failure
def parse_command(json_string_with_backticks):
    print("Attempting to parse LLM response for command:",
          json_string_with_backticks)
    if not json_string_with_backticks or not isinstance(json_string_with_backticks, str):
        print("Error: Invalid input for parsing (expected non-empty string).")
        return None
    try:
        json_string = json_string_with_backticks.replace(
            "```json", "").replace("```", "").strip()
        json_start = json_string.find('{')
        json_end = json_string.rfind('}')
        if json_start != -1 and json_end != -1:
            json_string = json_string[json_start:json_end+1]
        else:
            print("Error: Could not find valid JSON object boundaries.")
            return None
        data = json.loads(json_string)
        command = data.get("command")
        if command:
            print(f"Successfully parsed command: {command}")
            return command
        else:
            print("Error: 'command' key not found in the parsed JSON object.")
            return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format during parsing: {e}")
        print(f"Problematic string content: '{json_string}'")
        return None
    except Exception as e:
        print(f"Error during command parsing: {e}")
        return None
def get_session_data():
    context_file_path = r"./data/context_infor.json"
    try:
        data = read_json_file(context_file_path)
        if isinstance(data, list) and len(data) >= 2:
            print("Successfully read session context data.")
            return data
        else:
            print(
                f"Warning: Context file '{context_file_path}' does not have the expected list structure. Returning default empty context.")
            return [{}, {}]
    except FileNotFoundError:
        print(
            f"Warning: Context file '{context_file_path}' not found. Returning default empty context.")
        return [{}, {}]
    except Exception as e:
        print(f"Error reading context file '{context_file_path}': {e}")
        return [{}, {}]
def generate_speech_audio_data(text):
    if not text:
        print("Warning: Empty text provided for speech synthesis.")
        return None
    try:
        print(f"Synthesizing speech for text: '{text[:50]}...'")
        tts = gTTS(text=text, lang='en', slow=False)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        sound = AudioSegment.from_file(mp3_fp, format="mp3")
        wav_fp = io.BytesIO()
        sound.export(wav_fp, format="wav")
        wav_fp.seek(0)
        print("Speech synthesis successful.")
        return wav_fp

    except Exception as e:
        print(f"Error generating speech audio data: {e}")
        return None
command_recognition_prompt = PromptTemplate.from_template(
    """
You are a helpful AI system designed to understand user instructions related to elderly care and route them to the appropriate module.

Below is a JSON object that describes all available command categories. Each category is an object with a "description" that defines its purpose and an "example" that illustrates its typical use-case. Use this information to accurately classify the user's instruction.

{{
    "Nutrition Management": {{
        "description": "Handles dietary intake tracking, nutritional analysis, and food-related recommendations. Use this category when the instruction involves reporting meals, asking for dietary advice, or similar tasks.",
        "example": "I had soup and bread for lunch at 12:30 PM."
    }},
    "Communication Assistance": {{
        "description": "Facilitates communication tasks like sending messages or notifications to family members, caregivers, or friends.",
        "example": "Can you tell my son I will be late for dinner tonight?"
    }},
    "Medication Management": {{
        "description": "Manages medication-related tasks such as reminders, scheduling, or inquiries about prescriptions and dosages.",
        "example": "Remind me to take my blood pressure medication at 8 PM."
    }},
    "Emotional and Social Support": {{
        "description": "Provides support related to emotional well-being and assists in social interactions, including companionship and conversational engagement.",
        "example": "I feel lonely today. Can you chat with me?"
    }},
    "Cognitive Support": {{
        "description": "Assists with memory tasks, mental exercises, reminders for cognitive activities, or any functions that stimulate mental acuity.",
        "example": "Help me remember to do my puzzles."
    }},
    "General information": {{
        "description": "Handles broader inquiries that do not strictly fall into one of the above categories, such as questions about the weather or news.",
        "example": "What's the weather like today?"
    }}
}}
Your task is to analyze the user instruction provided below and determine the primary command category to which it belongs. The response MUST be a JSON object with a single property "command" whose value is one of the keys listed above (e.g., "Nutrition Management", "Communication Assistance", etc.).

If the user instruction does not clearly match any of the categories, or if you are unsure, respond ONLY with the following JSON object:
{{
    "command": "unknown"
}}

Do not add any explanatory text before or after the JSON object.

User Instruction: "{user_instruction}"
"""
)
prompt_template_for_message = PromptTemplate.from_template(
    """You are a helpful AI assistant designed to format responses from a backend system into natural-sounding chat messages for the user. Your goal is to make the information feel like it's coming from a friendly human in a conversation.
Contextual information about the user (usercontext) and the conversation history or system state (llm_context) may be provided but should NOT be directly included in your final response unless specifically relevant to crafting the message based on the response_object.
User Context: {usercontext}
LLM Context: {llm_context}

**Input Format:**
The backend response is provided as a JSON object or a simple string within the 'response_object' variable.

**Output Format:**
Your output MUST be a single string representing the final chat message for the user. It should be clear, concise, grammatically correct, and sound natural and conversational. Use plain text only. Do NOT use Markdown formatting (like * or _).

**Instructions:**

1.  **Analyze `response_object`:** Determine if it's a structured JSON object or a simple string (like an error message or a direct answer).
2.  **Prioritize 'message' field (if JSON):** If `response_object` is a JSON object and contains a 'message' field, use that as the core of your response. Enhance it slightly for better flow (e.g., add "Okay, ", "Got it, ", or similar if appropriate).
3.  **Incorporate Data Fields (if JSON without 'message' or needs context):** If 'message' is absent or insufficient, look for relevant data fields in the JSON `response_object` (like 'food_item', 'recipient', 'medication_name', 'reminder_time', 'answer', 'error'). Weave these details into a natural sentence. Examples:
    * `{{"food_item": "Oatmeal", "meal_time": "8:00 AM"}}` -> "Okay, I've logged Oatmeal for your 8:00 AM meal."
    * `{{"recipient": "Son", "status": "Sent"}}` -> "Alright, the message to your Son has been sent."
    * `{{"reminder_time": "9 PM", "medication_name": "Aspirin"}}` -> "Got it. I've set a reminder for Aspirin at 9 PM."
    * `{{"error": "Database connection failed."}}` -> "I'm sorry, I encountered a problem and couldn't complete your request due to a database connection issue."
    * `{{"answer": "The weather will be sunny."}}` -> "The weather forecast shows it will be sunny today."
4.  **Handle Simple Strings:** If `response_object` is just a string (not JSON), present it clearly. If it looks like an error message, phrase it gently.
    * `"Could not find contact."` -> "Sorry, I couldn't find that contact."
    * `"Reminder set successfully."` -> "Okay, the reminder has been set successfully."
5.  **Handle Errors Gently:** If the `response_object` indicates an error (e.g., contains an 'error' field or is an error string), communicate this clearly but politely. Avoid overly technical jargon. Example: "I'm sorry, something went wrong while trying to do that. [Optional: Add simple detail from error message if helpful, e.g., 'I couldn't connect to the service.']"
6.  **Maintain Conversational Tone:** Use friendly, natural language. Vary sentence structure. Avoid robotic phrasing.
7.  **Be Concise:** Provide necessary information without unnecessary detail.

**Now, format the following backend response object into a single, plain text chat message:**
{response_object}
"""
)
gentle_prompt_template_unknown = PromptTemplate.from_template(
    """You are a helpful and gentle AI assistant designed to understand and respond to user instructions, particularly in an elderly care context.
Contextual information (usercontext, llm_context) is provided for your understanding but should not be repeated in the response.
User Context: {usercontext}
LLM Context: {llm_context}
User Instruction: "{user_input}"
Analyze the user's instruction.
If you can confidently understand and directly fulfill the request or answer the question based *only* on the instruction itself (without needing external tools or specific command handlers you don't have access to), provide a helpful and direct response.
However, if the user's instruction is unclear, ambiguous, too complex for a direct answer, seems to require a specific action you cannot perform (like setting a reminder or sending a message, which are handled by other modules), or falls outside your general knowledge capabilities, DO NOT attempt to guess or fulfill it. Instead, respond with ONE of the following gentle and encouraging messages, asking for clarification:
* "I'm sorry, I didn't quite understand that. Could you please try phrasing it differently?"
* "Could you please say that again, perhaps using different words? I want to make sure I help you correctly."
* "Hmm, I'm not quite sure what you mean. Could you please explain that in another way?"
* "I need a little more information to understand that. Could you please rephrase your request?"

Choose the clarification request that sounds most natural. Your response MUST be only the chosen clarification request. Do not add any other text. Respond in plain text only. Do not use Markdown.
"""
)
command_recognition_chain = command_recognition_prompt | llm
message_formatting_chain = prompt_template_for_message | llm
unknown_command_chain = gentle_prompt_template_unknown | llm
def process_instruction_from_text(user_input, u='a'):

    if not user_input or not isinstance(user_input, str) or user_input.strip() == "":
        print("No valid text input detected.")

        return "I didn't receive any input. Could you please repeat that?"

    session_user = auth_service.get_session_user()
    aux_context_data = get_session_data()      #
    user_context_for_llm = {
        "username": session_user.get("username"),
        "permissions": session_user.get("permissions")

    }
    llm_context_for_llm = aux_context_data[1] if len(
        aux_context_data) > 1 else {}
    print(
        f"Processing instruction for user: {session_user.get('username', 'Unknown')}")
    print(f"User Input: '{user_input}'")
    try:
        command_response = command_recognition_chain.invoke({
            "user_instruction": user_input
        })
        command_category = parse_command(
            command_response.content)  
    except Exception as e:
        print(
            f"Error invoking command recognition chain or parsing response: {e}")
        command_category = "unknown"
    print(f"Detected Command Category: {command_category}")
    backend_response = None
    handler_args = {
        "user_input": user_input,
        "llm": llm,
    }
    try:
        if command_category == "Nutrition Management":
            backend_response = handleNutritionCommand(**handler_args)
        elif command_category == "Communication Assistance":
            backend_response = handleCommunicationCommand(**handler_args)
        elif command_category == "Medication Management":
            backend_response = handleMedicationCommand(**handler_args)
        elif command_category == "Emotional and Social Support":
            backend_response = handleEmotionalCommand(**handler_args)
        elif command_category == "Cognitive Support":
            backend_response = handleCognitiveCommand(**handler_args)
        elif command_category == "General information":
            backend_response = handleGeneralCommand(**handler_args)
        else:
            print(
                "Command is unknown or could not be determined. Invoking gentle fallback.")

            fallback_response = unknown_command_chain.invoke({
                "user_input": user_input,
                "usercontext": user_context_for_llm,
                "llm_context": llm_context_for_llm
            })

            return fallback_response.content.strip()
    except Exception as e:
        print(f"Error executing command handler for '{command_category}': {e}")
        backend_response = {
            "error": f"An error occurred while processing your request for {command_category}."}
    print(
        f"Backend Response from handler ({command_category}): {backend_response}")
    try:
        final_message_response = message_formatting_chain.invoke({
            "response_object": json.dumps(backend_response) if isinstance(backend_response, dict) else str(backend_response),
            "usercontext": user_context_for_llm,
            "llm_context": llm_context_for_llm
        })
        final_message = final_message_response.content.strip()
        print(f"Formatted Final Message: {final_message}")
        if(u == 'tp'):
            return {"final_message":final_message, "user_input":user_input}
        return final_message
    except Exception as e:
        print(f"Error invoking message formatting chain: {e}")

        return "I've processed your request, but I'm having a little trouble phrasing the response right now."
@app.route('/')
def index():
    data = read_json_file(r"./data/sessionuser.json")
    if not data:
        return render_template('auth.html')
    return render_template('home.html')


@app.route('/upload_data', methods=['POST'])
@login_required
def upload_data_route():
    """Handles the upload of the four configuration JSON files."""
    session_user = auth_service.get_session_user()
    username = session_user.get('username', 'UnknownUser')
    print(f"Received request for /upload_data from user: {username}")

    required_files = {
        'medicationInfo': None,
        'healthConcerns': None,
        'emails': None,
        'contextInfo': None
    }
    uploaded_data = {}
    errors = {}

    for key in required_files.keys():
        if key not in request.files:
            errors[key] = f"Missing file part: {key}"
        else:
            file = request.files[key]
            if file.filename == '':
                errors[key] = f"No file selected for: {key}"
            elif not allowed_file(file.filename):
                errors[key] = f"Invalid file type for {key}. Only .json allowed."
            else:
                required_files[key] = file
    if errors:
        print(
            f"File upload failed for user {username}: Missing or invalid files - {errors}")
        # Bad Request
        return jsonify({'error': 'Missing or invalid files provided.', 'details': errors}), 400

    # --- 2. Read and validate JSON content ---
    for key, file in required_files.items():
        if file:
            try:
                file_content = file.read().decode('utf-8-sig')
                json_data = json.loads(file_content)
                uploaded_data[key] = json_data
                print(f"Successfully read and parsed JSON from file: {key}")
            except json.JSONDecodeError as e:
                errors[key] = f"Invalid JSON format in file {key}: {e}"
            except UnicodeDecodeError as e:
                errors[key] = f"File encoding error in {key}. Please ensure it's UTF-8: {e}"
            except Exception as e:
                errors[key] = f"Error processing file {key}: {e}"
                print(
                    f"Unexpected error processing file {key} for user {username}: {e}")
    if errors:
        print(
            f"File processing failed for user {username}: Invalid JSON or read errors - {errors}")
        # Bad Request
        return jsonify({'error': 'Error processing one or more files.', 'details': errors}), 400
    user_upload_dir = os.path.join(UPLOAD_FOLDER, username)
    try:
        if not os.path.exists(user_upload_dir):
            os.makedirs(user_upload_dir)
        for key, data in uploaded_data.items():
            save_path = os.path.join(user_upload_dir, f"{key}_uploaded.json")
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        print(f"Successfully saved uploaded data for user: {username}")
    except Exception as e:
        print(f"Error saving uploaded files for user {username}: {e}")
        return jsonify({'error': 'Data processed but failed to save.'}), 500
    print(f"Successfully processed all 4 files for user: {username}")
    handleUpdatingData()
    # OK
    return jsonify({'message': 'All files uploaded and processed successfully!'}), 200


def handleUpdatingData():
    contextInfo = read_json_file(
        r"user_data_uploads/krishna23-45/contextInfo_uploaded.json")
    emails_info = read_json_file(
        r"user_data_uploads/krishna23-45/emails_uploaded.json")
    health_concern = read_json_file(
        r"user_data_uploads/krishna23-45/healthConcerns_uploaded.json")
    medicationInfo = read_json_file(
        r"user_data_uploads/krishna23-45/medicationInfo_uploaded.json")
    write_json_file(r"data/context_infor.json", contextInfo)
    write_json_file(r"data/emails.json", emails_info)
    write_json_file(r"data/identify_health_concerns.json", health_concern)
    write_json_file(r"data/medicationInfo.json", medicationInfo)


@app.route('/auth/register', methods=['POST'])
def register_route():
    print("Received request for /auth/register")
    data = request.get_json()
    print("----------------------")
    print(data)
    if not data or 'username' not in data or 'password' not in data:
        print("Registration failed: Missing username or password.")
        return jsonify({'error': 'Username and password are required'}), 400
    username = data.get('username')
    password = data.get('password')
    try:
        new_user = auth_service.register(username, password)
        user_info = {k: v for k, v in new_user.items() if k != 'password'}
        print(f"Registration successful for user: {username}")
        # Created
        return jsonify({'message': 'Registration successful', 'user': user_info}), 201
    except Exception as e:
        error_message = str(e)
        print(f"Registration failed for {username}: {error_message}")
        status_code = 409 if 'already exists' in error_message else 500
        return jsonify({'error': error_message}), status_code


@app.route('/auth/login', methods=['POST'])
def login_route():
    """Logs in a user and establishes a session."""
    print("Received request for /auth/login")
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        print("Login failed: Missing username or password.")
        return jsonify({'error': 'Username and password are required'}), 400
    username = data.get('username')
    password = data.get('password')
    try:
        user = auth_service.login(username, password)
        user_info = {k: v for k, v in user.items() if k != 'password'}
        print(f"Login successful for user: {username}")
        return redirect("/")
    except Exception as e:
        error_message = str(e)
        print(f"Login failed for {username}: {error_message}")
        return jsonify({'error': error_message}), 401


@app.route('/add_data_page')
@login_required
def add_data_page():
    return render_template('add_data.html')


@app.route('/auth/logout', methods=['POST'])
@login_required
def logout_route():
    session_user = auth_service.get_session_user()
    username = session_user.get('username', 'Unknown user')
    print(f"Received request for /auth/logout from user: {username}")
    try:
        auth_service.clear_session_user()
        print(f"Logout successful for user: {username}")
        return redirect("/")
    except Exception as e:
        print(f"Error during logout for {username}: {e}")
        # Internal Server Error
        return jsonify({'error': 'Failed to clear session during logout'}), 500


@app.route('/auth/session', methods=['GET'])
def get_session_route():
    """Gets the current session user info (if logged in). Publicly accessible for session check."""
    print("Received request for /auth/session check")
    session_user = auth_service.get_session_user()
    if session_user and isinstance(session_user, dict) and session_user.keys():
        print(f"Active session found for user: {session_user.get('username')}")

        safe_session_info = {k: v for k,
                             v in session_user.items() if k != 'password_hash'}
        return jsonify({'user': safe_session_info}), 200
    else:
        print("No active session found.")

        return jsonify({'user': None, 'message': 'No active session'}), 200


@app.route('/process_audio', methods=['POST'])
@login_required
def process_audio_route():
    """Handles audio input, transcribes, processes, and returns text response."""
    session_user = auth_service.get_session_user()
    username = session_user.get('username', 'Unknown user')
    print(f"Received request for /process_audio from user: {username}")

    if whisper_model is None:
        print("Audio processing endpoint called but Whisper model is not available.")
        # Service Unavailable
        return jsonify({'error': 'Audio processing is currently unavailable.'}), 503

    if 'audio' not in request.files:
        print("Audio processing failed: No audio file provided.")
        # Bad Request
        return jsonify({'error': 'No audio file part in the request'}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        print("Audio processing failed: No selected audio file.")
        return jsonify({'error': 'No selected audio file'}), 400  # Bad Request

    try:
        audio_bytes = audio_file.read()
        print(
            f"Received audio file: {audio_file.filename}, size: {len(audio_bytes)} bytes")
        # Transcribe audio to text
        user_input = process_audio_file(audio_bytes)
        if not user_input:
            print("Audio processing failed: Transcription returned empty.")
            return jsonify({'response': "I couldn't understand the audio. Could you please speak clearly or check the recording?"}), 200
        print(f"Transcription result: '{user_input}'")
        result_text = process_instruction_from_text(user_input,"tp")
        print(f"Sending response for audio input: '{result_text}'")
        return jsonify({'response': result_text}), 200  # OK
    except Exception as e:
        print(f"Error in /process_audio route for user {username}: {e}")
        import traceback
        traceback.print_exc()
        # Internal Server Error
        return jsonify({'error': f'An unexpected error occurred during audio processing: {e}'}), 500
@app.route('/process_text', methods=['POST'])
@login_required
def process_text_route():
    """Handles text input, processes, and returns text response."""
    session_user = auth_service.get_session_user()
    username = session_user.get('username', 'Unknown user')
    print(f"Received request for /process_text from user: {username}")
    data = request.get_json()
    if not data or 'text' not in data or not data['text'].strip():
        print("Text processing failed: No text input provided.")
        # Bad Request
        return jsonify({'error': 'No text input provided.'}), 400

    user_input = data['text']
    print(f"Received text input: '{user_input}'")
    try:
        result_text = process_instruction_from_text(user_input)
        print(f"Sending response for text input: '{result_text}'")
        return jsonify({'response': result_text}), 200

    except Exception as e:
        print(f"Error in /process_text route for user {username}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'An unexpected error occurred during text processing: {e}'}), 500
@app.route('/synthesize_speech', methods=['POST'])
@login_required
def synthesize_speech_route():
    """Handles text input and returns synthesized speech audio (WAV)."""
    session_user = auth_service.get_session_user()
    username = session_user.get('username', 'Unknown user')
    print(f"Received request for /synthesize_speech from user: {username}")
    data = request.get_json()
    if not data or 'text' not in data or not data['text'].strip():
        print("Speech synthesis failed: No text provided.")
        return jsonify({'error': 'No text provided for synthesis.'}), 400
    text_to_speak = data['text']
    print(f"Synthesizing speech for text: '{text_to_speak[:100]}...'")
    try:
        audio_data_buffer = generate_speech_audio_data(text_to_speak)
        if audio_data_buffer:
            print("Speech synthesis successful, sending WAV data.")
            return send_file(
                audio_data_buffer,
                mimetype='audio/wav',
                as_attachment=False
            )
        else:
            print("Speech synthesis failed: generate_speech_audio_data returned None.")
            return jsonify({'error': 'Failed to generate speech audio.'}), 500
    except Exception as e:
        print(f"Error in /synthesize_speech route for user {username}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'An internal server error occurred during speech synthesis.'}), 500
if __name__ == "__main__":
    print("Starting Flask application...")

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir)
            print(f"Created data directory: {data_dir}")
        except OSError as e:
            print(f"Error creating data directory '{data_dir}': {e}")
            sys.exit(1)

    host = '0.0.0.0'
    port = 5000
    debug_mode = True
    print(
        f"Running Flask app on http://{host}:{port}/ (Debug Mode: {debug_mode})")
    app.run(debug=debug_mode, host=host, port=port)
