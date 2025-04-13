# auth_service.py
import sys
import os
import json 
import uuid

try:
    from utils.fileUtils import read_json_file, write_json_file
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    try:
        from utils.fileUtils import read_json_file, write_json_file
    except ImportError as e:
        print(f"Error importing fileUtils in authService: {e}")
        raise

USERS_FILE = r'./data/users.json'
SESSION_USER_FILE = r'./data/sessionuser.json' 

session_user = None


def generate_id():
    return str(uuid.uuid4())

def initialize_session():
    global session_user
    try:
        data_dir = os.path.dirname(SESSION_USER_FILE)
        if data_dir and not os.path.exists(data_dir):
             os.makedirs(data_dir)
             print(f"Created data directory: {data_dir}")
        session_user = read_json_file(SESSION_USER_FILE)
        print("-------- Initial Session User Check --------", session_user)
        if not session_user: 
            session_user = {}
            write_json_file(SESSION_USER_FILE, session_user)
            print("-------- Session Initialized as Empty --------")
    except FileNotFoundError:
         print(f"Session file {SESSION_USER_FILE} not found, initializing empty session.")
         session_user = {}
         data_dir = os.path.dirname(SESSION_USER_FILE)
         if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
         write_json_file(SESSION_USER_FILE, session_user)
    except Exception as error:
        print(f"Error initializing session: {error}. Setting session_user to empty dict.")
        session_user = {}



def simple_hash(password):
    """A simple, non-secure hashing function for demonstration purposes ONLY."""
    hash_value = 0
    for char in password:
        hash_value = (hash_value * 31 + ord(char)) & 0xFFFFFFFF # Basic hash algorithm
    return str(hash_value)


def login(username, password):
    """Logs in a user by verifying username and password."""
    try:
        users = read_json_file(USERS_FILE) 
        if not isinstance(users, list):
             raise Exception(f'Users file ({USERS_FILE}) format is incorrect, expected a list.')

        user = next((u for u in users if u.get('username') == username), None)

        if not user:
            raise Exception('Invalid username or password')

        if user.get('password') != simple_hash(password):
            raise Exception('Invalid username or password')

        session_data = {
            'userId': user.get('userId'),
            'username': user.get('username')
        }
        set_session_user(session_data)

        # Return user data (excluding password hash)
        user_info = {k: v for k, v in user.items() if k != 'password'}
        return user_info

    except FileNotFoundError:
         print(f"Login error: Users file '{USERS_FILE}' not found.")
         raise Exception('Login service configuration error.')
    except Exception as error:
        print(f"Login error for user '{username}': {error}")
        raise Exception(f'Login failed: {error}')


def get_user_by_id(user_id):
    """Retrieves a user by their userId."""
    try:
        users = read_json_file(USERS_FILE)
        if not isinstance(users, list):
             raise Exception(f'Users file ({USERS_FILE}) format is incorrect, expected a list.')
        user = next((u for u in users if str(u.get('userId')) == str(user_id)), None)

        if not user:
            raise Exception(f'User with ID {user_id} not found')

        print(f"Target user found with Id: {user.get('userId')}")
        user_info = {k: v for k, v in user.items() if k != 'password'}
        return user_info 

    except FileNotFoundError:
        print(f"Get user by ID error: Users file '{USERS_FILE}' not found.")
        raise Exception(f'Could not find user data file.')
    except Exception as err:
        print(f"Error finding user with ID {user_id}: {err}")
        raise Exception(f"Could not find the user with the given ID {user_id}: {err}")


def register(username, password):
    """Registers a new user. Permissions field removed."""
    # Basic validation
    if not username or not password:
        raise ValueError("Username and password cannot be empty.")
    try:
        data_dir = os.path.dirname(USERS_FILE)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"Created data directory for users file: {data_dir}")
        try:
            users = read_json_file(USERS_FILE)
            if not isinstance(users, list):
                 print(f"Warning: Users file {USERS_FILE} was not a list. Initializing as empty list.")
                 users = []
        except json.JSONDecodeError:
             print(f"Warning: Users file {USERS_FILE} contains invalid JSON. Initializing as empty list.")
             users = []

        existing_user = next((user for user in users if user.get('username') == username), None)
        if existing_user:
            raise Exception('Username already exists')

        user_id = generate_id()
        hashed_password = simple_hash(password)

        new_user = {
            'userId': user_id,
            'username': username,
            'password': hashed_password
        }

        users.append(new_user)
        write_json_file(USERS_FILE, users)
        print(f"User '{username}' registered successfully with ID '{user_id}'.")

        # Return new user info (excluding password)
        user_info = {k: v for k, v in new_user.items() if k != 'password'}
        return user_info

    except Exception as error:
        print(f"Registration error for username '{username}': {error}")
        # Re-raise the specific error (like 'Username already exists') or a generic one
        raise error


def get_session_user():
    """Gets the currently logged-in user's data from the session variable."""
    global session_user
    if session_user is None:
        print("Session user is None, re-initializing session...")
        initialize_session() # Attempt to load from file
    return session_user


def set_session_user(user_data):
    """Sets the currently logged-in user's data and writes it to the session file."""
    global session_user
    if user_data and not isinstance(user_data, dict):
         print("Error: Invalid data type passed to set_session_user. Expected dict.")
         return # Or raise error

    session_user = user_data if user_data is not None else {} # 
    try:
        data_dir = os.path.dirname(SESSION_USER_FILE)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
        write_json_file(SESSION_USER_FILE, session_user)
        print(f"Session user set and saved: {session_user.get('username') if session_user else 'None'}")
    except Exception as error:
        print(f"Error writing session user data to {SESSION_USER_FILE}: {error}")


def clear_session_user():
    global session_user
    session_user = {}
    try:
        data_dir = os.path.dirname(SESSION_USER_FILE)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
        write_json_file(SESSION_USER_FILE, session_user) # Write empty object to file
        print("Session user cleared and file updated.")
    except Exception as error:
        print(f"Error clearing session user file {SESSION_USER_FILE}: {error}")
