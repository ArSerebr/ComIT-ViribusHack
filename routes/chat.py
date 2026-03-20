from fastapi import APIRouter, Query, BackgroundTasks
import logging

from state.state_manager import (get_state, save_state, create_task, update_task, save_message, set_agent_status)
from agents.agent_registry import classifier_agent, conversation_agent
from pipelines.idea_generation_pipeline import IdeaGenerationPipeline
from pipelines.idea_refinement_pipeline import IdeaRefinementPipeline

router = APIRouter()

@router.post("/api/chat")
def chat(payload: dict, background_tasks: BackgroundTasks, uid: str = Query(...)):
    task_id = create_task(uid)
    background_tasks.add_task(process_chat, task_id, uid, payload)
    return {"task_id": task_id}

def update_task_and_save(task_id: str, uid: str, status: str, result: dict):
    update_task(task_id, status, result)
    if status == "READY" and result:
        save_message(uid, result.get("role", "ai"), result.get("content", ""), result.get("buttons", []))

def process_chat(task_id: str, uid: str, payload: dict):
    print("PROCESS_CHAT START", task_id)
    try:
        message = payload.get("message", "")
        is_arena = payload.get("is_arena", False) # По умолчанию используем Арену
        
        save_message(uid, "user", message)
        state = get_state(uid)
        print({"message": message})
        # 1. Классификация
        set_agent_status(uid, "Classifier", 10)
        classification = classifier_agent.run({"message": message})
        msg_type = classification.get("type", "other")
        print(classification)
        # Если это запрещенная тема или оффтоп
        if msg_type in ["notit", "other"]:
            set_agent_status(uid, "PulsAR", 100)
            res = conversation_agent.run({"message": message, "state": state})
            result = {
                "role": "ai",
                "content": res.get("reply", "Извините, я могу обсуждать только IT-проекты."),
                "buttons": ["Вернуться к проекту"]
            }
            update_task_and_save(task_id, uid, "READY", result)
            return

        # Если это вопрос о сервисе
        if msg_type == "question":
            set_agent_status(uid, "PulsAR", 100)
            res = conversation_agent.run({"message": message, "state": state})
            result = {
                "role": "ai",
                "content": res.get("reply", "Я PulsAR, ваш помощник в создании IT-проектов."),
                "buttons": ["Вернуться к проекту"]
            }
            update_task_and_save(task_id, uid, "READY", result)
            return

        # Если переход в планировщик
        if msg_type == "gotoplanner":
            result = {
                "role": "ai",
                "content": "Переходим в планировщик...",
                "buttons": ["Продолжить в планировщике"]
            }
            update_task_and_save(task_id, uid, "READY", result)
            return

        # 2. Обработка Идей
        # Если это новая идея или "answer" (который может быть идеей в контексте)
        if msg_type in ["idea", "answer"]:
            
            # Проверяем, не является ли это выбором идеи (например, "Идея 1")
            if message.strip().lower().startswith("идея") or (state.get("stage") == "await_selection" and message.strip() in ["1", "2", "3"]):
                # Логика выбора идеи (упрощенно)
                try:
                    import re
                    match = re.search(r'\d+', message)
                    idea_id = int(match.group()) if match else 1
                except:
                    idea_id = 1
                
                state["selected_idea"] = idea_id
                state["stage"] = "idea_selected"
                save_state(uid, state)
                
                result = {
                    "role": "ai",
                    "content": f"Вы выбрали Идею {idea_id}. Хотите её доработать или продолжим в планировщике?",
                    "buttons": ["Доработать идею", "Продолжить в планировщике"]
                }
                update_task_and_save(task_id, uid, "READY", result)
                return

            # Функция обратного вызова для обновления статуса
            def on_step(agent_name, progress):
                set_agent_status(uid, agent_name, progress)

            # Запуск пайплайна генерации
            pipeline = IdeaGenerationPipeline(mode="arena" if is_arena else "linear", on_step_start=on_step)
            #print("AFTER PIPELINE", get_task(task_id))
            final_memory = pipeline.run({"message": message})
            
            ideas = final_memory.get("final_ideas", final_memory.get("ideas", []))
            
            # Сохраняем в стейт
            state["ideas"] = ideas
            state["stage"] = "await_selection"
            save_state(uid, state)
            
            content = "Вот какие проекты я подготовил:\n\n"
            for i, idea in enumerate(ideas):
                title = idea.get("title", f"Проект {i+1}")
                concept = idea.get("concept", idea.get("final", ""))
                content += f"### {i+1}. {title}\n{concept}\n\n"
            
            result = {
                "role": "ai",
                "content": content,
                "buttons": ["Идея 1", "Идея 2", "Идея 3"]
            }
            update_task_and_save(task_id, uid, "READY", result)
            return

        # Если доработка идеи
        if msg_type == "project": # Классификатор может пометить детальное сообщение как проект
             # В ТЗ: "Если это доработка старой идеи то пайплайн доработки"
             selected_id = state.get("selected_idea")
             if selected_id:
                 # Берем текст идеи
                 ideas = state.get("ideas", [])
                 idea_to_refine = next((i for i in ideas if i.get("id") == selected_id), ideas[0] if ideas else {})
                 
                 # Функция обратного вызова для обновления статуса
                 def on_step(agent_name, progress):
                     set_agent_status(uid, agent_name, progress)

                 pipeline = IdeaRefinementPipeline(on_step_start=on_step)
                 res_memory = pipeline.run({"idea": idea_to_refine, "message": message})
                 improved_text = res_memory.get("final_idea", "")
                 
                 # Обновляем в списке
                 for i in ideas:
                     if i.get("id") == selected_id:
                         i["final"] = improved_text
                         i["concept"] = improved_text
                 
                 state["ideas"] = ideas
                 save_state(uid, state)
                 
                 result = {
                     "role": "ai",
                     "content": f"Я обновил идею согласно вашим пожеланиям:\n\n{improved_text}",
                     "buttons": ["Продолжить в планировщике"]
                 }
                 update_task_and_save(task_id, uid, "READY", result)
                 return
             else:
                 # Если идея не выбрана, но пользователь прислал подробности - считаем это новой идеей
                 # Функция обратного вызова для обновления статуса
                 def on_step(agent_name, progress):
                     set_agent_status(uid, agent_name, progress)

                 pipeline = IdeaGenerationPipeline(mode="arena" if is_arena else "linear", on_step_start=on_step)
                 final_memory = pipeline.run({"message": message})
                 # ... (аналогично коду выше)
                 # Для краткости вызываем рекурсивно или копируем
                 process_chat(task_id, uid, {"message": message, "is_arena": is_arena})
                 return

        # Fallback
        res = conversation_agent.run({"message": message, "state": state})
        result = {
            "role": "ai",
            "content": res.get("reply", "Я готов помочь с вашим проектом. Опишите вашу идею!"),
            "buttons": ["Вернуться к проекту"]
        }
        update_task_and_save(task_id, uid, "READY", result)

    except Exception as e:
        logging.error(f"Error in process_chat: {e}")
        update_task(task_id, "FAILED", {"error": str(e)})
