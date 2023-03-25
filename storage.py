import json


def load_data(file_name="laundry_data.json"):
    try:
        with open(file_name, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data


def save_data(data, file_name="laundry_data.json"):
    with open(file_name, "w") as file:
        json.dump(data, file)
