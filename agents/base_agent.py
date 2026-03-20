import logging
import json
from pathlib import Path
from typing import Dict, Any, List
from services.llm import llm
from agents.prompts import prompts

# Определяем путь к текущему файлу
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "agents.log"

# Настройка логгера
logger = logging.getLogger("agents")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


class Agent:
    def __init__(
        self,
        name: str,
        model: str,
        use_context: bool,
        input_fields: List[str],
        output_fields: List[str],
        system_prompt_key: str,
        additional_prompt: str = ""
    ):
        self.name = name
        self.model = model
        self.use_context = use_context
        self.input_fields = input_fields
        self.output_fields = output_fields
        self.system_prompt_key = system_prompt_key
        self.additional_prompt = additional_prompt

    def run(self, memory: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = prompts.get(self.system_prompt_key, "")
        input_data = {field: memory.get(field, "") for field in self.input_fields}

        try:
            formatted_system_prompt = (
                system_prompt.format(**memory)
                if (system_prompt and self.use_context)
                else system_prompt
            )
        except (KeyError, IndexError, ValueError) as e:
            logger.warning(
                f"Agent {self.name}: Error formatting system prompt: {e}"
            )
            formatted_system_prompt = system_prompt

        full_prompt = f"{formatted_system_prompt}\n{self.additional_prompt}\n"

        for field, value in input_data.items():
            if f"{{{field}}}" not in system_prompt:
                full_prompt += f"\n{field}: {value}"

        try:
            response_text = llm(full_prompt, self.model)

            result = {}
            if len(self.output_fields) == 1:
                result[self.output_fields[0]] = response_text
            else:
                try:
                    parsed_json = json.loads(response_text)
                    if isinstance(parsed_json, dict):
                        for field in self.output_fields:
                            result[field] = parsed_json.get(field)
                    else:
                        result[self.output_fields[0]] = response_text
                except json.JSONDecodeError:
                    result[self.output_fields[0]] = response_text

            log_entry = {
                "agent": self.name,
                "model": self.model,
                "input": input_data,
                "output": result,
            }
            logger.info(json.dumps(log_entry, ensure_ascii=False))

            return result

        except Exception as e:
            error_entry = {
                "agent": self.name,
                "model": self.model,
                "input": input_data,
                "error": str(e),
            }
            logger.error(json.dumps(error_entry, ensure_ascii=False))
            raise