from pydantic import BaseModel
from typing import List, Optional


class StudentBase(BaseModel):
    """Базова схема для студента"""
    telegram_id: str  # Новий параметр
    name: str
    current_course_year: int
    specialty: str
    learning_preferences: Optional[str] = None


class StudentCreate(StudentBase):
    """Схема для створення студента"""
    pass


class StudentResponse(StudentBase):
    """Схема для відповіді зі студентом"""
    id: int

    class Config:
        from_attributes = True  # Дозволяє використовувати ORM-об'єкти


class DisciplineBase(BaseModel):
    """Базова схема для дисципліни"""
    title: str
    description: Optional[str] = None
    instructor_name: str
    material_summary: Optional[str] = None
    has_practical_labs: bool = False
    credits: int
    course_year: int = 1  # Новий параметр
    specialty: str = "General"  # Новий параметр


class DisciplineCreate(DisciplineBase):
    """Схема для створення дисципліни"""
    pass


class DisciplineResponse(DisciplineBase):
    """Схема для відповіді з дисципліною"""
    id: int

    class Config:
        from_attributes = True


class CurriculumResponse(BaseModel):
    """Схема для відображення рекомендованої дисципліни"""
    id: int
    discipline: DisciplineResponse
    match_reason: Optional[str] = None
    is_selected: bool = False

    class Config:
        from_attributes = True


class PromptRequest(BaseModel):
    """Схема для прийому текстового побажання студента"""
    prompt_text: str


class RecommendedCurriculumListResponse(BaseModel):
    """Схема для списку рекомендованих дисциплін"""
    student_id: int
    recommendations: List[CurriculumResponse]
    total_credits: int = 0


class GenerationResponse(BaseModel):
    """Схема для відповіді при генерації навчальної програми ШІ"""
    general_report: str
    recommendations: List[CurriculumResponse]
    total_credits: int
