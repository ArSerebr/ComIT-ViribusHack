import logging
import threading
from typing import Dict, Any, List, Union
from concurrent.futures import ThreadPoolExecutor
from agents.base_agent import Agent

class Pipeline:
    def __init__(
        self,
        name: str,
        agents: List[Union[Agent, List[Agent]]],
        memory: Dict[str, Any] = None,
        meta: Dict[str, Any] = None,
        on_step_start: callable = None
    ):
        self.name = name
        self.agents = agents
        self.memory = memory if memory is not None else {}
        self._lock = threading.Lock()
        self.on_step_start = on_step_start
        self._meta = meta if meta is not None else {
            "pipeline_name": name,
            "steps": []
        }

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Совпадающие поля из входных переписываются в память
        with self._lock:
            self.memory.update(input_data)
        
        try:
            total_steps = len(self.agents)
            for i, step in enumerate(self.agents):
                progress = int((i / total_steps) * 100)
                
                if isinstance(step, list):
                    # Для параллельного шага уведомляем о первом агенте или общем прогрессе
                    if self.on_step_start:
                        self.on_step_start(step[0].name, progress)
                    # Параллельное выполнение
                    self._run_parallel_step(step)
                else:
                    if self.on_step_start:
                        self.on_step_start(step.name, progress)
                    # Последовательное выполнение
                    self._run_single_agent(step)
                
                # Если во время выполнения шага возникла ошибка, прерываем пайплайн
                if self._meta.get("status") == "error":
                    return self.memory

            self._meta["status"] = "success"
            if self.on_step_start:
                self.on_step_start("PulsAR", 100) # Завершение
            
        except Exception as e:
            self._meta["status"] = "critical_error"
            self._meta["error_message"] = str(e)
            logging.critical(f"Pipeline {self.name}: Critical error: {e}")

        # На выход - память словаря
        return self.memory

    def _run_single_agent(self, agent: Agent):
        try:
            step_info = {"agent": agent.name, "status": "started", "mode": "sequential"}
            with self._lock:
                self._meta["steps"].append(step_info)
            
            # Выполнение агента
            agent_output = agent.run(self.memory)
            
            # Обновление памяти результатами работы агента
            self._merge_results(agent_output)
            
            step_info["status"] = "completed"
            logging.info(f"Pipeline {self.name}: Agent {agent.name} completed successfully.")
        except Exception as e:
            self._handle_error(agent, e)

    def _run_parallel_step(self, agents: List[Agent]):
        logging.info(f"Pipeline {self.name}: Starting parallel step with agents: {[a.name for a in agents]}")
        
        # Делаем snapshot памяти для агентов, чтобы они работали на одних данных
        with self._lock:
            memory_snapshot = self.memory.copy()

        with ThreadPoolExecutor(max_workers=len(agents)) as executor:
            futures = {executor.submit(agent.run, memory_snapshot): agent for agent in agents}
            
            for future in futures:
                agent = futures[future]
                try:
                    agent_output = future.result()
                    self._merge_results(agent_output)
                    
                    with self._lock:
                        self._meta["steps"].append({
                            "agent": agent.name, 
                            "status": "completed", 
                            "mode": "parallel"
                        })
                except Exception as e:
                    self._handle_error(agent, e)

    def _merge_results(self, agent_output: Dict[str, Any]):
        with self._lock:
            for key, value in agent_output.items():
                if key in self.memory:
                    # Если в памяти уже есть список, и агент вернул список - объединяем (extend)
                    if isinstance(self.memory[key], list) and isinstance(value, list):
                        self.memory[key].extend(value)
                    # Если это словари - можно было бы делать deep merge, но пока просто перезаписываем
                    # или оставляем как есть, если нужно избежать повреждения данных.
                    # В данном ТЗ просили "безопасную запись", extend для списков - это главное.
                    else:
                        self.memory[key] = value
                else:
                    self.memory[key] = value

    def _handle_error(self, agent: Agent, e: Exception):
        error_msg = str(e)
        logging.error(f"Pipeline {self.name}: Error in agent {agent.name}: {error_msg}")
        
        with self._lock:
            self._meta["status"] = "error"
            self._meta["error_agent"] = agent.name
            self._meta["error_message"] = error_msg
            self._meta["steps"].append({
                "agent": agent.name, 
                "status": "failed", 
                "error": error_msg
            })

    @property
    def meta(self):
        return self._meta
