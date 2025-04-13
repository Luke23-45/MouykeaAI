import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key(str):
  return os.getenv(str)

