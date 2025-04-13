
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.emotionalService import emotionalSerivce

def handleEmotionalCommand(user_input,llm):
  return emotionalSerivce(user_input,llm)