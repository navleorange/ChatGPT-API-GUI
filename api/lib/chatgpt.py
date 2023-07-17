import os
import time
import logging
import configparser
import openai
import tiktoken
from dotenv import load_dotenv
from . import util
from api.res import prompts, settings

class ChatGPT:
    def __init__(self, inifile:configparser.ConfigParser, title:str) -> None:
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
        util.prepare_logs(log_path=self.inifile.get("log","path"), model_name=self.inifile.get("ChatGPT","model_name"))
        self.log_name =  util.get_date_time() + title 
        self.log_path = self.inifile.get("log","path") + self.inifile.get("ChatGPT","model_name") + "/" + self.log_name + ".log"
        self.logger = logging.getLogger(self.log_name)
        self.logger.setLevel(logging.DEBUG)
        self.log_handler = logging.FileHandler(self.log_path, mode="w", encoding="utf-8")
        self.logger.addHandler(self.log_handler)
        self.log_fmt = logging.Formatter("%(message)s")
        self.log_handler.setFormatter(self.log_fmt)

        # inform the model information
        model_data = dict(model=self.name, temperature=self.temperature, top_p=self.top_p, generate_num=self.generate_num, max_tokens=self.max_tokens, 
                          presence_penalry=self.presence_penalty, frequency_penalty=self.frequency_penalty)
        print(settings.gpt_info_separate_word)
        print("model\t\t\t: " + self.name)
        print("temperature\t\t: " + str(self.temperature))
        print("top_p\t\t\t: " + str(self.top_p))
        print("generate_num\t\t: " + str(self.generate_num))
        print("max_tokens\t\t: " + str(self.max_tokens))
        print("presence_penalty\t: " + str(self.presence_penalty))
        print("frequency_penalty\t: " + str(self.frequency_penalty))
        print(settings.separate_word)
        self.logger.info(model_data)
    
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

        time.sleep(0.5)    # last resort

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