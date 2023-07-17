import os
import errno
import re
import json
import datetime
import configparser
from typing import NoReturn
import openai
from api.res import settings

def read_log(log_path:str) -> list:
     with open(log_path,"r") as f:
        return f.readlines()

def is_directory_exist(directory_path:str) -> bool:
    return os.path.isdir(directory_path)

def is_file_exist(file_path:str) -> bool:
    return os.path.isfile(file_path)

def alert_file(file_path:str) -> NoReturn:
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)

def make_directory(directory_path:str) -> None:
    if not is_directory_exist(directory_path=directory_path):
        os.mkdir(directory_path)

def load_config(config_path:str) -> configparser.ConfigParser:
    if not is_file_exist(file_path=config_path):
        alert_file(file_path=config_path)
    
    return configparser.ConfigParser()

def prepare_logs(log_path:str, model_name:str) -> None:
    make_directory(directory_path=log_path)
    make_directory(directory_path=log_path+model_name)

def get_date_time() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

def set_billing_address(model_name:str) -> None:

    if settings.gpt3 in model_name:
        openai.organization = os.environ.get("OPENAI_ORGANIZATION_3.5")
    else:
        openai.organization = os.environ.get("OPENAI_ORGANIZATION_4")

def convert_prompts(messages:list) -> str:
    # convert prompts for human readable

    result = ""

    for message in messages:
        result += message["content"] + "\n"

    return result

def get_model_list(log_path:str) -> list:
    # search log file
    if not is_directory_exist(directory_path=log_path): return None
    model_dir = [log_path + model_name for model_name in os.listdir(log_path)]
    if len(model_dir) == 0:  return None
    
    return model_dir

def get_log_list(log_path:str) -> list:
    model_dir = get_model_list(log_path=log_path)
    if model_dir == None:  return None

    log_list = []

    for model_path in model_dir:
        log_list.extend([model_path + "/" + log_name for log_name in os.listdir(model_path)])
        # log_list.extend(os.listdir(model_path))

    return log_list

def remove_dir_pattern(log_name:str) -> str:
    dir_pattern = ".+/"
    return re.sub(dir_pattern,"",log_name)

def remove_time_pattern(log_name:str) -> str:
    # log example: 2023-07-17_20:40:20名前テスト
    time_pattern = "\d{4}(-\d{2}){2}_(\d{2}:){2}\d{2}"
    return re.sub(time_pattern,"",log_name)

def get_log_name(log_list:list) -> list:

    if log_list == None: return None
    
    result = []

    for log in log_list:
        log_name = remove_dir_pattern(log_name=log)
        log_name = remove_time_pattern(log_name=log_name)
        log_name = log_name.replace(".log","")
        result.append(log_name)

    return result

def check_post_event(request:str, event:str) -> bool:
    result_flag = False

    for key in request.keys():
        if re.fullmatch(event,key):
            result_flag = True
            break
    
    return result_flag

def is_new_log_button_event(request:str) -> bool:
    add_log_event = "add_log_button"
    return check_post_event(request=request, event=add_log_event)

def is_log_button_event(request:str) -> bool:
    log_event = "log\d+"
    return check_post_event(request=request, event=log_event)

def get_display_log_index(request:str) -> int:
    log_event = "log\d+"
    non_digits = "\D"
    result = -1

    for key in request.keys():
        if re.fullmatch(log_event,key):
            result = int(re.sub(non_digits,"",key))
            break
    
    return result

def str_to_dict(text:str) -> dict:
    return json.loads(text.replace("'","\""))

def get_past_messages(log_path:str, display_log_index:int) -> list:
    log_list = get_log_list(log_path=log_path)

    log_lines = read_log(log_path=log_list[display_log_index])
    del log_lines[0]    # 0: model info

    return [str_to_dict(text=line) for line in log_lines]   # string to dict