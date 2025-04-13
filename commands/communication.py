
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from services.communicationService import handleCommunicationService


def handleCommunicationCommand(user_input,llm):
  return handleCommunicationService(user_input,llm)
  

  
