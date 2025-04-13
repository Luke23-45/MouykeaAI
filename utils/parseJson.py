import json
import re
def parse_json_object(input_str):

    # This regex finds text between ```json and ```
    pattern = r"```json\s*(.*?)\s*```"
    match = re.search(pattern, input_str, re.DOTALL)
  
    if match:
        json_str = match.group(1)
    else:
        json_str = input_str

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError("Failed to parse JSON") from e