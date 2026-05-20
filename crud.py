from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from models import Student, Discipline, RecommendedCurriculum
from schemas import StudentCreate, DisciplineCreate


# ==================== СТУДЕНТИ ====================

def create_student(db: Session, student: StudentCreate) -> Student:
    """
    Створює новога студента в базі даних.
    
    Args:
        db: Сесія бази даних
        student: Дані студента для створення
        
    Returns:
        Student: Створений об'єкт студента
    """
    db_student = Student(
        telegram_id=student.telegram_id,
        name=student.name,
        current_course_year=student.current_course_year,
        specialty=student.specialty,
        learning_preferences=student.learning_preferences
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_student_by_id(db: Session, student_id: int) -> Optional[Student]:
    """
    Отримує студента за ID.
    
    Args:
        db: Сесія бази даних
        student_id: ID студента
        
    Returns:
        Student or None: Об'єкт студента або None якщо не знайдено
    """
    return db.query(Student).filter(Student.id == student_id).first()


def get_student_by_telegram_id(db: Session, telegram_id: str) -> Optional[Student]:
    """
    Отримує студента за Telegram ID.
    
    Args:
        db: Сесія бази даних
        telegram_id: Telegram ID студента
        
    Returns:
        Student or None: Об'єкт студента або None якщо не знайдено
    """
    return db.query(Student).filter(Student.telegram_id == telegram_id).first()


# ==================== ДИСЦИПЛІНИ ====================

def create_discipline(db: Session, discipline: DisciplineCreate) -> Discipline:
    """
    Створює нову дисципліну в базі даних.
    
    Args:
        db: Сесія бази даних
        discipline: Дані дисципліни для створення
        
    Returns:
        Discipline: Створений об'єкт дисципліни
    """
    db_discipline = Discipline(
        title=discipline.title,
        description=discipline.description,
        instructor_name=discipline.instructor_name,
        material_summary=discipline.material_summary,
        has_practical_labs=discipline.has_practical_labs,
        credits=discipline.credits,
        course_year=discipline.course_year,
        specialty=discipline.specialty
    )
    db.add(db_discipline)
    db.commit()
    db.refresh(db_discipline)
    return db_discipline


def get_all_disciplines(db: Session) -> List[Discipline]:
    """
    Отримує всі дисципліни з бази даних.
    
    Args:
        db: Сесія бази даних
        
    Returns:
        List[Discipline]: Список всіх дисциплін
    """
    return db.query(Discipline).all()


def get_discipline_by_id(db: Session, discipline_id: int) -> Optional[Discipline]:
    """
    Отримує дисципліну за ID.
    
    Args:
        db: Сесія бази даних
        discipline_id: ID дисципліни
        
    Returns:
        Discipline or None: Об'єкт дисципліни або None якщо не знайдено
    """
    return db.query(Discipline).filter(Discipline.id == discipline_id).first()


# ==================== РЕКОМЕНДОВАНІ НАВЧАЛЬНІ ПРОГРАМИ ====================

def save_recommended_curriculum(
    db: Session,
    student_id: int,
    discipline_ids: List[int],
    match_reasons: List[str]
) -> List[RecommendedCurriculum]:
    """
    Зберігає список рекомендованих дисциплін для студента.
    Спочатку видаляє старі рекомендації, потім зберігає нові.
    
    Args:
        db: Сесія бази даних
        student_id: ID студента
        discipline_ids: Список ID дисциплін
        match_reasons: Список причин для кожної дисципліни
        
    Returns:
        List[RecommendedCurriculum]: Список створених рекомендацій
    """
    # Видаляємо старі рекомендації для цього студента
    db.query(RecommendedCurriculum).filter(
        RecommendedCurriculum.student_id == student_id
    ).delete()
    db.commit()
    
    # Створюємо нові рекомендації
    recommendations = []
    for discipline_id, match_reason in zip(discipline_ids, match_reasons):
        recommendation = RecommendedCurriculum(
            student_id=student_id,
            discipline_id=discipline_id,
            match_reason=match_reason,
            is_selected=False
        )
        db.add(recommendation)
        recommendations.append(recommendation)
    
    db.commit()
    
    # Оновлюємо об'єкти перед поверненням
    for recommendation in recommendations:
        db.refresh(recommendation)
    
    return recommendations


def get_recommended_curriculum_by_student(
    db: Session,
    student_id: int
) -> List[RecommendedCurriculum]:
    """
    Отримує всі рекомендовані дисципліни для студента.
    
    Args:
        db: Сесія бази даних
        student_id: ID студента
        
    Returns:
        List[RecommendedCurriculum]: Список рекомендацій для студента
    """
    return db.query(RecommendedCurriculum).filter(
        RecommendedCurriculum.student_id == student_id
    ).all()
