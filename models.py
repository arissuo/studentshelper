from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Student(Base):
    """
    Модель студента для збереження інформації про студента та його побажання щодо навчання.
    """
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)  # Новий поле
    name = Column(String, nullable=False)
    current_course_year = Column(Integer, nullable=False)
    specialty = Column(String, nullable=False)
    learning_preferences = Column(Text, nullable=True)

    # Зв'язок one-to-many: один студент має багато рекомендованих програм
    recommended_curriculums = relationship(
        "RecommendedCurriculum",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.name}', specialty='{self.specialty}')>"

    # Зв'язок one-to-many: один студент має багато рекомендованих програм
    recommended_curriculums = relationship(
        "RecommendedCurriculum",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Student(id={self.id}, name='{self.name}', specialty='{self.specialty}')>"


class Discipline(Base):
    """
    Модель дисципліни для збереження інформації про навчальні дисципліни.
    """
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    instructor_name = Column(String, nullable=False)
    material_summary = Column(Text, nullable=True)
    has_practical_labs = Column(Boolean, default=False)
    credits = Column(Integer, nullable=False)
    course_year = Column(Integer, nullable=False, default=1)  # Новий поле
    specialty = Column(String, nullable=False, default="General")  # Новий поле

    # Зв'язок one-to-many: одна дисципліна може бути рекомендована багатьом студентам
    recommended_curriculums = relationship(
        "RecommendedCurriculum",
        back_populates="discipline",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Discipline(id={self.id}, title='{self.title}', credits={self.credits})>"


class RecommendedCurriculum(Base):
    """
    Модель для збереження ШІ-згенерованого навчального плану для студента.
    Зв'язує студента та дисципліну з поясненням від ШІ.
    """
    __tablename__ = "recommended_curriculums"

    id = Column(Integer, primary_key=True, index=True)
    
    # Зовнішні ключі
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"), nullable=False, index=True)
    
    # Дані про рекомендацію
    match_reason = Column(Text, nullable=True)  # Пояснення від ШІ, чому обрано дисципліну
    is_selected = Column(Boolean, default=False)  # Чи студент обрав цю дисципліну

    # Зв'язки many-to-one: багато рекомендацій до одного студента та дисципліни
    student = relationship(
        "Student",
        back_populates="recommended_curriculums"
    )
    discipline = relationship(
        "Discipline",
        back_populates="recommended_curriculums"
    )

    def __repr__(self):
        return (
            f"<RecommendedCurriculum(id={self.id}, "
            f"student_id={self.student_id}, "
            f"discipline_id={self.discipline_id}, "
            f"is_selected={self.is_selected})>"
        )
