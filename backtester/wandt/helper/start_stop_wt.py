import os
import ast
import json
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
file_path = f'{BASE_DIR}/static/wts.json'

def start_wt_environment_set(user_running_strategy_id):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                wts = json.load(file)

            wts[user_running_strategy_id] = "started"
            with open(file_path, 'w') as file:
                json.dump(wts, file)
        else:
            with open(file_path, 'w') as file:
                wts = {}
                json.dump(wts, file)
    except Exception as e:
        print(f"An error occurred: {e}")
        start_wt_environment_set(user_running_strategy_id)
        


def squareoff_wt_environment_set(user_running_strategy_id): #squareoff
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                wts = json.load(file)

            wts[user_running_strategy_id] = "squareoff"
            with open(file_path, 'w') as file:
                json.dump(wts, file)
        else:
            with open(file_path, 'w') as file:
                wts = {}
                json.dump(wts, file)
    except Exception as e:
        print(f"An error occurred: {e}")
        squareoff_wt_environment_set(user_running_strategy_id)

def stop_wt_environment_set(user_running_strategy_id): #stop
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                wts = json.load(file)

            wts[user_running_strategy_id] = "stop"
            with open(file_path, 'w') as file:
                json.dump(wts, file)
        else:
            with open(file_path, 'w') as file:
                wts = {}
                json.dump(wts, file)
    except Exception as e:
        print(f"An error occurred: {e}")
        stop_wt_environment_set(user_running_strategy_id)


def get_wt_environment_value(user_running_strategy_id):
    status = ""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                wts = json.load(file)
                status = wts[str(user_running_strategy_id)]
    except Exception as e:
        print(f"An error occurred: {e}")
        get_wt_environment_value(user_running_strategy_id)
    finally:
        return status


# if __name__=="__main__": 
#     print(get_wt_environment_value(20))