from .deepseek import DeepSeek # Самый дешевый для диалогов
from .gemini import Gemini # Самый дешевый для заданий
from .gpt_nano import GPT_nano # Самый быстрый + дешевый
from .gpt_52 import GPT # Дорогой, для сложных заданий
from .claude_opus import Opus # Дорогой, для сложных заданий
from .claude_haiku import Haiku # Средний, для заданий
import os
import logging

# Создаем папку для логов, если её нет
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Настраиваем отдельный логгер для LLM
agent_logger = logging.getLogger("agent_logger")
agent_logger.setLevel(logging.INFO)

# Создаем обработчик для записи в файл
file_handler = logging.FileHandler(os.path.join(log_dir, "agents.log"), encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
if not agent_logger.handlers:
    agent_logger.addHandler(file_handler)

def llm(prompt: str, model: str) -> str:
    if model == "deepseek":
        ans = DeepSeek(prompt)
        logging.info(f"model=DeepSeek \n\n prompt={prompt} \n\n answer={ans}")
        return ans
    elif model == "gemini":
        ans = Gemini(prompt)
        logging.info(f"model=Gemini \n\n prompt={prompt} \n\n answer={ans}")
        return ans
    elif model == "gpt_nano":
        ans = GPT_nano(prompt)
        logging.info(f"model=GPT_nano \n\n prompt={prompt} \n\n answer={ans}")
        return ans
    elif model == "gpt":
        ans = GPT(prompt)
        logging.info(f"model=GPT \n\n prompt={prompt} \n\n answer={ans}")
        return ans
    elif model == "opus":
        ans = Opus(prompt)
        logging.info(f"model=Opus \n\n prompt={prompt} \n\n answer={ans}")
        return ans
    elif model == "haiku":
        ans = Haiku(prompt)
        logging.info(f"model=Haiku \n\n prompt={prompt} \n\n answer={ans}")
        return ans
    else: # Модель по умолчанию - самая дешевая
        ans = DeepSeek(prompt)
        logging.info(f"model=DeepSeek_default \n\n prompt={prompt} \n\n answer={ans}")
        return ans
