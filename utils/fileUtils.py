import os
import json

def file_exists(file_path):
    try:
        os.stat(file_path)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        raise e

def ensure_file(file_path):
    if not file_exists(file_path):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            # Write the default data.
            default_data = []
            write_json_file(file_path, default_data)
            print(f"File {file_path} created with default data.")
        except Exception as e:
            print(f"Error ensuring file {file_path}: {e}")
            raise e

def write_json_file(file_path, data, ensure=True):
    """Writes JSON data to a file."""
    if ensure:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise Exception(f"Error writing JSON file: {file_path} - {e}")

def read_json_file(file_path):
    ensure_file(file_path)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
            if not data.strip():
                return []
            return json.loads(data)
    except json.JSONDecodeError as parse_error:
        raise Exception(f"Error parsing JSON file: {file_path} - {parse_error}")
    except Exception as e:
        raise Exception(f"Error reading file: {file_path} - {e}")

def main():
    file_path = 'data/log_meal.json'
    exists = file_exists(file_path)
    print(f"File '{file_path}' exists: {exists}")
    ensure_file(file_path)
    exists = file_exists(file_path)
    print(f"File '{file_path}' exists after ensure: {exists}")
    test_data = [{'name': 'Test', 'value': 1}]
    write_json_file(file_path, test_data)
    print(f"Wrote data to '{file_path}'")

    read_data = read_json_file(file_path)
    print(f"Read data from '{file_path}': {read_data}")

    ensure_file(file_path)
    print(f"Ensured file '{file_path}' again (should not create)")

    empty_file_path = 'temp/empty.json'
    ensure_file(empty_file_path)
    empty_data = read_json_file(empty_file_path)
    print(f"Read data from empty file '{empty_file_path}' with 'u' flag: {empty_data}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())