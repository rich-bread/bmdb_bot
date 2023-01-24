import json

def open_json(filename) -> dict or list:
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data