import os
import errno
import datetime
import configparser
from typing import NoReturn
import openai
from api.res import settings

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

def get_log_list(log_path:str) -> list:
    # search log file
    if not is_directory_exist(directory_path=log_path): return None
    model_dir = os.listdir(log_path)
    if len(model_dir) == 0:  return None

    result = []

    for model_path in model_dir:
        entity_path = log_path + model_path
        log_list = os.listdir(entity_path)
        
        if len(log_list) == 0: return None

        for log in log_list:
            result.append(log.replace(".log",""))

    return result