import os
import logging
import configparser
import openai
import tiktoken
from dotenv import load_dotenv
from . import util
from res import prompts, settings

class ChatGPT:
    def __init__(self, inifile:configparser.ConfigParser) -> None:
        # ChatGPT settings
        self.model = openai.ChatCompletion
        self.inifile = inifile
        self.name = inifile.get("ChatGPT","model_name")
        self.temperature = inifile.getfloat("ChatGPT","temperature")
        self.top_p = inifile.getfloat("ChatGPT","to_p")
        self.generate_num = inifile.getint("ChatGPT","generate_num")
        self.stream_flag = inifile.getboolean("ChatGPT","stream")
        self.max_tokens = inifile.getint("ChatGPT","max_tokens")
        self.presence_penalty = inifile.getfloat("ChatGPT","presence_penalty")
        self.frequency_penalty = inifile.getfloat("ChatGPT","frequency_penalty")
        self.token_model = tiktoken.encoding_for_model(model_name=self.name)

        # variables setting
        self.talk_history = []

        # load api_key
        api_key_path = inifile.get("ChatGPT","api_key_path")
        if not util.is_file_exist(file_path=api_key_path): util.alert_file(file_path=api_key_path)
        load_dotenv(api_key_path)
        openai.api_key = os.environ.get("OPENAI_API_KEY")

        # set billing address
        util.set_billing_address(model_name=self.name)
        
        # log settings
        self.logger = None
        self.log_handler = None
    
    def check_model_info(self) -> None:
        print(settings.gpt_info_separate_word)
        print("model\t\t\t: " + self.name)
        print("temperature\t\t: " + str(self.temperature))
        print("top_p\t\t\t: " + str(self.top_p))
        print("generate_num\t\t: " + str(self.generate_num))
        print("max_tokens\t\t: " + str(self.max_tokens))
        print("presence_penalty\t: " + str(self.presence_penalty))
        print("frequency_penalty\t: " + str(self.frequency_penalty))
        print(settings.separate_word)
    
    def get_tokens(self, text:str) -> None:
        tokens = self.token_model.encode(text)
        return len(tokens)

    def make_message(self, role:str, content:str) -> dict:
        # change text to ChatCompletion format

        # remove space
        role = role.replace("\u200b","")
        role = role.replace("\u3000","")
        content = content.replace("\u200b","")
        content = content.replace("\u3000","")

        message = dict(role=role,content=content)

        return message
    
    def update_history(self, role:str, text:str) -> None:
        self.talk_history.append(self.make_message(role=role, content=text))
    
    def add_stream_content(self, pos:int, content:str) -> None:
        if len(self.talk_history) == pos:
            self.talk_history.append(self.make_message(role=prompts.chatgpt_role, content=content))
        else:
            self.talk_history[pos]["content"] += content
        
    def create_comment_stream(self, text:str) -> dict:
        # write log
        if self.logger == None: self.set_logger(title=text)
        message_data = dict(role=prompts.user_role, content=text)
        self.logger.info(message_data)

        self.update_history(role=prompts.user_role, text=text)
        messages = self.talk_history.copy()

        response = self.model.create(
            model = self.name,
            messages = messages,
            temperature = self.temperature,
            top_p = self.top_p,
            n = self.generate_num,
            stream = self.stream_flag,
            max_tokens = self.max_tokens,
            presence_penalty = self.presence_penalty,
            frequency_penalty = self.frequency_penalty
        )

        response_content = ""
        add_pos = len(self.talk_history)

        for chunk in response:
            if chunk:
                content = chunk["choices"][0]["delta"].get("content")
                if content:
                    response_content += content
                    self.add_stream_content(pos=add_pos, content=content)
                    yield dict(index=len(self.talk_history) - 1, message=self.talk_history[-1])    # (talk_index, latest content)

        # write log
        self.logger.info(self.talk_history[-1])

        return dict(index=len(self.talk_history) - 1, message=response_content)    # (talk_index, latest content)

    def create_comment(self, text:str) -> str:

        self.update_history(role=prompts.user_role, text=text)
        messages = self.talk_history.copy()

        try:
            response = self.model.create(
                model = self.name,
                messages = messages,
                temperature = self.temperature,
                top_p = self.top_p,
                n = self.generate_num,
                stream = self.stream_flag,
                max_tokens = self.max_tokens,
                presence_penalty = self.presence_penalty,
                frequency_penalty = self.frequency_penalty
            )

            print(response["choices"][0]["message"]["content"])
            response_content = response["choices"][0]["message"]["content"]
            self.update_history(role=prompts.chatgpt_role, text=response_content)

            # write log
            self.logger.info(util.convert_prompts(messages=messages))
            self.logger.info(response_content)

        except:
            self.logger.info(settings.gpt_failed_generate)
            self.logger.info(response_content)
        

        self.update_history(role=prompts.chatgpt_role, text=response_content)

        return response_content
    
    def load_history(self, log_path:str, display_log_index:int) -> None:
        # read log
        log_list = util.get_log_list(log_path=log_path)
        log_path = log_list[display_log_index]
        log_lines = util.read_log(log_path=log_path)

        # model settings
        model_data = util.str_to_dict(text=log_lines.pop(0))
        self.name = model_data["model"]
        self.temperature = model_data["temperature"]
        self.top_p = model_data["top_p"]
        self.generate_num = model_data["generate_num"]
        self.max_tokens = model_data["max_tokens"]
        self.presence_penalty = model_data["presence_penalry"]
        self.frequency_penalty = model_data["frequency_penalty"]

        self.check_model_info()

        # set history and logger
        self.set_history(history_list=log_lines)
        self.set_logger(log_name=util.remove_dir_pattern(log_name=log_path), log_path=log_path)

    def set_logger(self, log_name:str=None, log_path:str=None, title:str=None) -> None:
        self.clear_logger()

        if log_name == None:
            util.prepare_logs(log_path=self.inifile.get("log","path"), model_name=self.inifile.get("ChatGPT","model_name"))
            title = title.replace("\n","").replace("\r","").replace("\t","")
            if len(title) >= 20: title = title[:10]
            self.log_name = util.get_date_time() +  title
            self.log_path = self.inifile.get("log","path") + self.inifile.get("ChatGPT","model_name") + "/" + self.log_name + ".log"
            self.log_handler = logging.FileHandler(self.log_path, mode="w", encoding="utf-8")
        else:
            print(log_path)
            self.log_name = log_name
            self.log_path = log_path
            self.log_handler = logging.FileHandler(self.log_path, mode="a", encoding="utf-8")

        self.logger = logging.getLogger(self.log_name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.log_handler)
        self.log_fmt = logging.Formatter("%(message)s")
        self.log_handler.setFormatter(self.log_fmt)

        # inform the model information
        self.check_model_info()

        if log_name == None:
            # write model information to log
            model_data = self.get_model_data()
            self.logger.info(model_data)
        
    def clear_logger(self) -> None:
        # close logger
        if self.logger != None and self.log_handler != None:
            self.logger.removeHandler(self.log_handler)
            self.log_handler.close()
        
        self.logger = self.log_handler = None

    def set_history(self, history_list:list) -> None:
        self.talk_history.clear()
        self.talk_history = [util.str_to_dict(text=history) for history in history_list]

    def clear_history(self) -> None:
        self.talk_history.clear()
    
    def reset_model(self) -> None:
        self.name = self.inifile.get("ChatGPT","model_name")
        self.temperature = self.inifile.getfloat("ChatGPT","temperature")
        self.top_p = self.inifile.getfloat("ChatGPT","to_p")
        self.generate_num = self.inifile.getint("ChatGPT","generate_num")
        self.stream_flag = self.inifile.getboolean("ChatGPT","stream")
        self.max_tokens = self.inifile.getint("ChatGPT","max_tokens")
        self.presence_penalty = self.inifile.getfloat("ChatGPT","presence_penalty")
        self.frequency_penalty = self.inifile.getfloat("ChatGPT","frequency_penalty")
    
    def get_model_data(self) -> dict:
        model_data = dict(model=self.name, temperature=self.temperature, top_p=self.top_p, generate_num=self.generate_num, max_tokens=self.max_tokens, 
                            presence_penalty=self.presence_penalty, frequency_penalty=self.frequency_penalty)
        return model_data
    
    def change_model(self, model_name:str) -> None:
        self.name = model_name
        self.check_model_info()