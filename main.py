from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from database import engine, Base, get_db
from ai_service import generate_study_plan
from models import Student, Discipline, RecommendedCurriculum
from crud import (
    create_student,
    get_student_by_id,
    get_student_by_telegram_id,
    create_discipline,
    get_all_disciplines,
    save_recommended_curriculum,
    get_recommended_curriculum_by_student
)
from schemas import (
    StudentCreate,
    StudentResponse,
    DisciplineCreate,
    DisciplineResponse,
    PromptRequest,
    RecommendedCurriculumListResponse,
    GenerationResponse,
    CurriculumResponse
)

# Налаштовуємо логування
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Створюємо всі таблиці в базі даних при старті додатку
Base.metadata.create_all(bind=engine)

# Ініціалізуємо FastAPI додаток
app = FastAPI(
    title="Personalized Learning Curriculum System",
    description="ШІ система для генерації персоналізованих навчальних програм",
    version="1.0.0"
)


# ==================== ТЕСТОВІ ЕНДПОІНТИ ====================

@app.get("/")
def read_root():
    """
    Тестовий ендпоінт для перевірки, що сервер працює.
    
    Returns:
        dict: Статус системи та повідомлення
    """
    return {"status": "ok", "message": "System is running"}


@app.get("/health")
def health_check():
    """
    Ендпоінт для перевірки здоров'я системи.
    
    Returns:
        dict: Статус системи та інформація про БД
    """
    return {
        "status": "healthy",
        "message": "All systems operational",
        "database": "connected"
    }


# ==================== СТУДЕНТИ ====================

@app.post("/students/", response_model=StudentResponse)
def register_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    """
    Реєструє нового студента в системі.
    
    Args:
        student: Дані студента для реєстрації
        db: Сесія бази даних
        
    Returns:
        StudentResponse: Дані зареєстрованого студента
    """
    db_student = create_student(db, student)
    return db_student


@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Отримує інформацію про студента за ID.
    
    Args:
        student_id: ID студента
        db: Сесія бази даних
        
    Returns:
        StudentResponse: Дані студента
        
    Raises:
        HTTPException: Якщо студента не знайдено
    """
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student


@app.get("/students/by-telegram/{telegram_id}", response_model=StudentResponse)
def get_student_by_telegram(
    telegram_id: str,
    db: Session = Depends(get_db)
):
    """
    Отримує інформацію про студента за Telegram ID.
    
    Args:
        telegram_id: Telegram ID студента
        db: Сесія бази даних
        
    Returns:
        StudentResponse: Дані студента
        
    Raises:
        HTTPException: Якщо студента не знайдено
    """
    db_student = get_student_by_telegram_id(db, telegram_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student


# ==================== ДИСЦИПЛІНИ ====================

@app.post("/disciplines/", response_model=DisciplineResponse)
def create_new_discipline(
    discipline: DisciplineCreate,
    db: Session = Depends(get_db)
):
    """
    Створює нову дисципліну в каталозі.
    
    Args:
        discipline: Дані дисципліни
        db: Сесія бази даних
        
    Returns:
        DisciplineResponse: Створена дисципліна
    """
    db_discipline = create_discipline(db, discipline)
    return db_discipline


@app.get("/disciplines/", response_model=list[DisciplineResponse])
def get_disciplines(db: Session = Depends(get_db)):
    """
    Отримує каталог всіх доступних дисциплін.
    
    Args:
        db: Сесія бази даних
        
    Returns:
        list[DisciplineResponse]: Список дисциплін
    """
    disciplines = get_all_disciplines(db)
    return disciplines


# ==================== ГЕНЕРАЦІЯ НАВЧАЛЬНОЇ ПРОГРАМИ ====================

@app.post("/students/{student_id}/generate-curriculum", response_model=GenerationResponse)
def generate_curriculum(
    student_id: int,
    request: PromptRequest,
    db: Session = Depends(get_db)
):
    """
    Генерує персоналізовану навчальну програму для студента на основі його побажань.
    
    Ендпоінт використовує Google Gemini API для:
    - Аналізу побажань студента
    - Створення детального академічного звіту з порадами
    - Рекомендації найбільш відповідних дисциплін
    - Збереження рекомендацій у БД
    
    Args:
        student_id: ID студента
        request: Побажання студента (prompt_text)
        db: Сесія бази даних
        
    Returns:
        GenerationResponse: Звіт та рекомендовані дисципліни
        
    Raises:
        HTTPException: Якщо студента не знайдено, немає дисциплін або помилка ШІ
    """
    logger.info(f"[API] Starting curriculum generation for student_id={student_id}")
    
    # Перевіряємо чи студент існує
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        logger.warning(f"[API] Student not found: student_id={student_id}")
        raise HTTPException(status_code=404, detail="Student not found")
    
    logger.info(f"[API] Found student: {db_student.name}, specialty={db_student.specialty}")
    
    # Отримуємо всі доступні дисципліни
    all_disciplines = get_all_disciplines(db)
    if not all_disciplines:
        logger.error(f"[API] No disciplines available in database")
        raise HTTPException(status_code=400, detail="No disciplines available")
    
    logger.info(f"[API] Found {len(all_disciplines)} disciplines in database")
    
    # Форматуємо дисципліни для передачі в ШІ
    disciplines_for_ai = [
        {
            "id": d.id,
            "title": d.title,
            "description": d.description or "",
            "credits": d.credits
        }
        for d in all_disciplines
    ]
    
    # Формуємо промпт для ШІ з інформацією про студента та його побажання
    student_info = f"""Студент: {db_student.name}
Спеціальність: {db_student.specialty}
Рівень навчання: {db_student.current_course_year} курс
Побажання студента: {request.prompt_text}
Додаткові преференції: {db_student.learning_preferences or 'Не вказано'}"""
    
    logger.info(f"[API] Calling Gemini AI for student_id={student_id}...")
    
    try:
        # Генеруємо рекомендацію за допомогою Google Gemini
        # Результат містить "general_report" та "recommendations"
        ai_result = generate_study_plan(student_info, disciplines_for_ai)
        logger.info(f"[API] AI generation completed successfully for student_id={student_id}")
        
    except ValueError as e:
        # JSON parsing або validation error
        logger.error(f"[API] AI validation error for student_id={student_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid AI response format: {str(e)}. Please try again."
        )
    except Exception as e:
        # Інші помилки (network, timeout, etc.)
        logger.error(f"[API] AI API error for student_id={student_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating curriculum from AI: {str(e)}. This may be a temporary issue. Please try again later."
        )
    
    # Екстрагуємо рекомендації з результату ШІ
    ai_recommendations = ai_result["recommendations"]
    general_report = ai_result["general_report"]
    
    logger.info(f"[API] AI returned {len(ai_recommendations)} recommendations")
    
    # Екстрагуємо discipline_id та match_reason
    discipline_ids = [rec["discipline_id"] for rec in ai_recommendations]
    match_reasons = [rec["match_reason"] for rec in ai_recommendations]
    
    try:
        # Зберігаємо рекомендації в БД
        logger.info(f"[API] Saving {len(discipline_ids)} recommendations to database")
        recommendations = save_recommended_curriculum(
            db,
            student_id,
            discipline_ids,
            match_reasons
        )
        logger.info(f"[API] Successfully saved recommendations for student_id={student_id}")
        
    except Exception as e:
        logger.error(f"[API] Database error while saving recommendations for student_id={student_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error saving recommendations to database: {str(e)}"
        )
    
    # Формуємо список рекомендованих дисциплін для відповіді
    curriculum_list = []
    total_credits = 0
    
    for rec in recommendations:
        db.refresh(rec)  # Перезавантажуємо об'єкт, щоб отримати зв'язки
        total_credits += rec.discipline.credits
        
        curriculum_list.append(CurriculumResponse(
            id=rec.id,
            discipline=DisciplineResponse.from_orm(rec.discipline),
            match_reason=rec.match_reason,
            is_selected=rec.is_selected
        ))
    
    logger.info(f"[API] Generated response for student_id={student_id}: {len(curriculum_list)} items, {total_credits} total credits")
    
    # Повертаємо відповідь з звітом та рекомендаціями
    return GenerationResponse(
        general_report=general_report,
        recommendations=curriculum_list,
        total_credits=total_credits
    )


@app.get("/students/{student_id}/curriculum", response_model=RecommendedCurriculumListResponse)
def get_student_curriculum(
    student_id: int,
    db: Session = Depends(get_db)
):
    """
    Отримує поточну рекомендовану навчальну програму для студента.
    
    Args:
        student_id: ID студента
        db: Сесія бази даних
        
    Returns:
        RecommendedCurriculumListResponse: Навчальна програма студента
        
    Raises:
        HTTPException: Якщо студента не знайдено
    """
    db_student = get_student_by_id(db, student_id)
    if not db_student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    recommendations = get_recommended_curriculum_by_student(db, student_id)
    
    curriculum_list = []
    total_credits = 0
    
    for rec in recommendations:
        total_credits += rec.discipline.credits
        curriculum_list.append(CurriculumResponse(
            id=rec.id,
            discipline=DisciplineResponse.from_orm(rec.discipline),
            match_reason=rec.match_reason,
            is_selected=rec.is_selected
        ))
    
    return RecommendedCurriculumListResponse(
        student_id=student_id,
        recommendations=curriculum_list,
        total_credits=total_credits
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

