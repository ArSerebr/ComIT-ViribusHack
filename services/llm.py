from .deepseek import DeepSeek   # диалоги
from .gemini import Gemini       # задачи
from .gpt_nano import GPT_nano   # быстрая классификация
import os
import logging

log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

agent_logger = logging.getLogger("agent_logger")
agent_logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(os.path.join(log_dir, "agents.log"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))

if not agent_logger.handlers:
    agent_logger.addHandler(file_handler)


def llm(prompt: str, model: str) -> str:
    if model == "deepseek":
        ans = DeepSeek(prompt)
        logging.info(f"model=DeepSeek prompt={prompt[:80]} answer={str(ans)[:80]}")
        return ans
    elif model == "gemini":
        ans = Gemini(prompt)
        logging.info(f"model=Gemini prompt={prompt[:80]} answer={str(ans)[:80]}")
        return ans
    elif model == "gpt_nano":
        ans = GPT_nano(prompt)
        logging.info(f"model=GPT_nano prompt={prompt[:80]} answer={str(ans)[:80]}")
        return ans
    else:
        ans = DeepSeek(prompt)
        logging.info(f"model=DeepSeek_default prompt={prompt[:80]} answer={str(ans)[:80]}")
        return ans
