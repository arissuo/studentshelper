import os
import json
import logging
import google.generativeai as genai

# Налаштовуємо логування
logger = logging.getLogger(__name__)

# Налаштовуємо ключ API для Google Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
logger.info("[AI_SERVICE] Google Gemini API configured")


def generate_study_plan(student_prompt: str, disciplines: list) -> dict:
    """
    Генерує персоналізований навчальний план за допомогою Google Gemini API.
    
    Функція використовує модель gemini-2.5-flash для аналізу побажань студента,
    створює детальний академічний звіт та рекомендує відповідні дисципліни
    на основі його спеціальності та преференцій.
    
    Args:
        student_prompt (str): Побажання студента (текстовий опис його вимог та переваг)
        disciplines (list): Список доступних дисциплін у форматі:
                           [{"id": int, "title": str, "description": str, "credits": int}, ...]
    
    Returns:
        dict: Словник з двома ключами:
              - "general_report" (str): Детальний академічний звіт/порада для студента
              - "recommendations" (list): Масив словників [{"discipline_id": int, "match_reason": str}, ...]
    
    Raises:
        ValueError: Якщо модель повернула невалідний JSON
        Exception: Якщо виникла помилка при зв'язку з API
    """
    logger.info("[AI_SERVICE] Starting curriculum generation")
    logger.debug(f"[AI_SERVICE] Student prompt: {student_prompt[:100]}...")
    logger.debug(f"[AI_SERVICE] Available disciplines: {len(disciplines)}")
    
    # Форматуємо список дисциплін у зрозумілий формат для моделі
    disciplines_text = "\n".join([
        f"- ID: {d['id']}, Назва: {d['title']}, Опис: {d['description']}, Кредити: {d['credits']}"
        for d in disciplines
    ])
    logger.debug(f"[AI_SERVICE] Formatted {len(disciplines)} disciplines for AI")
    
    # Системний промпт для моделі
    system_prompt = """Ти є академічним єдвайзером з багаторічним досвідом. 
Твоя задача - проаналізувати побажання студента, надати детальний звіт та рекомендувати дисципліни.

ВАЖЛИВО: Ти ПОВИНЕН повернути відповідь СУВОРО у форматі JSON-об'єкту.
Формат відповіді має бути РІВНО таким:
{
    "general_report": "<Детальний академічний звіт/порада для студента. Аналізуй його побажання, спеціальність та рівень навчання. Напиши конкретні поради та пропозиції щодо розвитку. 3-5 речень на українській мові>",
    "recommendations": [
        {"discipline_id": <число>, "match_reason": "<1-2 речення пояснення на українській мові>"},
        {"discipline_id": <число>, "match_reason": "<1-2 речення пояснення на українській мові>"},
        ...
    ]
}

Вимоги:
1. general_report має бути детальним (3-5 речень) та корисним для студента
2. Рекомендуй 2-4 найбільш відповідних дисципліни
3. Кожен match_reason має бути короткий (1-2 речення)
4. Враховуй побажання студента, його спеціальність і рівень навчання
5. Повертай ТІЛЬКИ JSON-об'єкт (не масив), нічого більше
6. Переконайся, що JSON синтаксис абсолютно правильний"""
    
    # Формуємо запит до моделі
    user_message = f"""Побажання студента:
{student_prompt}

Доступні дисципліни:
{disciplines_text}

Проаналізуй побажання студента, напиши детальний звіт з порадами та порекомендуй найбільш відповідні дисципліни у форматі JSON-об'єкту."""
    
    try:
        # Ініціалізуємо модель
        logger.info("[AI_SERVICE] Initializing Gemini 2.5 Flash model")
        model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=system_prompt)
        
        # Генеруємо відповідь
        logger.info("[AI_SERVICE] Sending request to Gemini API (this may take 10-15 seconds)...")
        response = model.generate_content(user_message)
        logger.info("[AI_SERVICE] Received response from Gemini API")
        
        # Отримуємо текст відповіді
        response_text = response.text.strip()
        logger.debug(f"[AI_SERVICE] Raw response length: {len(response_text)} characters")
        logger.debug(f"[AI_SERVICE] Raw response preview: {response_text[:200]}...")
        
        # Спробуємо спарсити JSON
        # Іноді модель може мати додаткові символи, тому шукаємо JSON в тексті
        if "```json" in response_text:
            logger.info("[AI_SERVICE] Detected JSON in markdown code block (```json)")
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            logger.info("[AI_SERVICE] Detected JSON in markdown code block (```)")
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        logger.debug(f"[AI_SERVICE] Cleaned response preview: {response_text[:200]}...")
        
        # Парсимо JSON
        logger.info("[AI_SERVICE] Parsing JSON response")
        result = json.loads(response_text)
        logger.info("[AI_SERVICE] JSON parsed successfully")
        
        # Валідуємо структуру
        logger.info("[AI_SERVICE] Validating response structure")
        if not isinstance(result, dict):
            raise ValueError(f"Відповідь має бути JSON-об'єктом, отримано: {type(result)}")
        
        if "general_report" not in result or "recommendations" not in result:
            missing_fields = []
            if "general_report" not in result:
                missing_fields.append("general_report")
            if "recommendations" not in result:
                missing_fields.append("recommendations")
            raise ValueError(f"Відповідь має містити поля: {', '.join(missing_fields)}")
        
        if not isinstance(result["recommendations"], list):
            raise ValueError(f"Поле 'recommendations' має бути масивом, отримано: {type(result['recommendations'])}")
        
        logger.info(f"[AI_SERVICE] Found {len(result['recommendations'])} recommendations")
        
        for i, item in enumerate(result["recommendations"]):
            if not isinstance(item, dict):
                raise ValueError(f"Елемент {i} 'recommendations' не є об'єктом: {type(item)}")
            if "discipline_id" not in item:
                raise ValueError(f"Елемент {i} 'recommendations' не має поля 'discipline_id'")
            if "match_reason" not in item:
                raise ValueError(f"Елемент {i} 'recommendations' не має поля 'match_reason'")
            logger.debug(f"[AI_SERVICE] Recommendation {i+1}: discipline_id={item['discipline_id']}")
        
        logger.info("[AI_SERVICE] Response validation passed. Curriculum generation successful")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"[AI_SERVICE] JSON decode error: {e}", exc_info=True)
        logger.error(f"[AI_SERVICE] Failed to parse JSON response. Raw text: {response_text[:500]}")
        raise ValueError(f"Помилка при парсингу JSON від ШІ: {str(e)}. Спробуйте ще раз.")
    except ValueError as e:
        logger.error(f"[AI_SERVICE] Validation error: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"[AI_SERVICE] Unexpected error: {e}", exc_info=True)
        raise Exception(f"Помилка при роботі з Google Gemini API: {str(e)}")
