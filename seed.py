from database import SessionLocal, engine
from models import Discipline, Base

def seed_data():
    db = SessionLocal()
    
    # Очищаємо таблицю перед наповненням, щоб уникнути дублікатів
    db.query(Discipline).delete()
    
    disciplines = [
        # === 1 КУРС ===
        Discipline(
            title="Алгоритми та структури даних",
            description="Вивчення базових і складних структур даних, алгоритмів пошуку, сортування та роботи з графами.",
            instructor_name="Павлюк О.М.",
            material_summary="Масиви, списки, дерева, хеш-таблиці, алгоритми на графах, оцінка складності O(n).",
            has_practical_labs=True,
            credits=5,
            course_year=1,
            specialty="Комп'ютерні науки"
        ),
        Discipline(
            title="Дискретна математика",
            description="Математичні основи комп'ютерних наук: множини, логіка, комбінаторика, графи.",
            instructor_name="Бойко Н.І.",
            material_summary="Теорія множин, булева алгебра, графи та дерева, машини Тюрінга.",
            has_practical_labs=False,
            credits=4,
            course_year=1,
            specialty="Комп'ютерні науки"
        ),
        Discipline(
            title="Об'єктно-орієнтоване програмування",
            description="Основи ООП: інкапсуляція, успадкування, поліморфізм, створення класів та об'єктів.",
            instructor_name="Ковальчук І.В.",
            material_summary="Робота з C++ та Java, патерни проектування, SOLID-принципи.",
            has_practical_labs=True,
            credits=5,
            course_year=1,
            specialty="Комп'ютерні науки"
        ),

        # === 2 КУРС ===
        Discipline(
            title="Організація баз даних",
            description="Проектування реляційних баз даних, написання SQL-запитів, нормалізація.",
            instructor_name="Григорчук А.С.",
            material_summary="РДБМС (PostgreSQL, MySQL), ключі, індекси, транзакції, процедури, тригери.",
            has_practical_labs=True,
            credits=4,
            course_year=2,
            specialty="Комп'ютерні науки"
        ),
        Discipline(
            title="Операційні системи",
            description="Принципи роботи сучасних ОС, управління пам'яттю, процесами та файловими системами.",
            instructor_name="Сидорчук В.П.",
            material_summary="Архітектура Linux/Windows, багатопоточність, синхронізація процесів.",
            has_practical_labs=True,
            credits=4,
            course_year=2,
            specialty="Комп'ютерні науки"
        ),
        Discipline(
            title="Web-технології та web-дизайн",
            description="Розробка фронтенд та бекенд частин веб-додатків, адаптивна верстка.",
            instructor_name="Левченко Д.О.",
            material_summary="HTML, CSS, JavaScript, React/Vue, основи роботи з REST API.",
            has_practical_labs=True,
            credits=5,
            course_year=2,
            specialty="Комп'ютерні науки"
        ),

        # === 3 КУРС ===
        Discipline(
            title="Проектування інформаційних систем",
            description="Вивчення методологій проектування, CASE-засобів та моделювання бізнес-процесів для створення автоматизованих систем.",
            instructor_name="Дорошенко А.В.",
            material_summary="IDEF, DFD, UML діаграми, концептуальне проектування БД, розробка ужитків баз даних.",
            has_practical_labs=True,
            credits=5,
            course_year=3,
            specialty="Комп'ютерні науки"
        ),
        Discipline(
            title="Програмування та автоматизація процесів",
            description="Розробка скриптів та ботів для автоматизації рутинних задач, взаємодія з API.",
            instructor_name="Мельник О.Г.",
            material_summary="Python, Node.js, використання бібліотек Telethon, aiogram, TDLib, робота з базами даних SQL/Firebase.",
            has_practical_labs=True,
            credits=4,
            course_year=3,
            specialty="Комп'ютерні науки"
        ),
        Discipline(
            title="Інженерія програмного забезпечення",
            description="Підходи до промислової розробки ПЗ, тестування, контроль версій та CI/CD.",
            instructor_name="Ткаченко М.С.",
            material_summary="Git, GitHub Actions, модульне тестування, рефакторинг, архітектурні патерни.",
            has_practical_labs=True,
            credits=4,
            course_year=3,
            specialty="Комп'ютерні науки"
        ),

        # === 4 КУРС ===
        Discipline(
            title="Обчислювальний інтелект смарт-систем",
            description="Вивчення методів штучного інтелекту для розв'язання складних оптимізаційних та класифікаційних задач.",
            instructor_name="Теслюк В.М.",
            material_summary="Нейронні мережі, нечітка логіка, побудова байєсівських мереж, розробка нечітких контролерів у Python.",
            has_practical_labs=True,
            credits=5,
            course_year=4,
            specialty="Комп'ютерні науки"
        ),
        Discipline(
            title="Системи штучного інтелекту",
            description="Основи машинного навчання, нейромережі, обробка природної мови.",
            instructor_name="Кравченко О.П.",
            material_summary="Python, Pandas, Scikit-learn, TensorFlow, базові алгоритми класифікації.",
            has_practical_labs=True,
            credits=5,
            course_year=4,
            specialty="Комп'ютерні науки"
        ),
        Discipline(
            title="Управління ІТ-проектами",
            description="Методології розробки програмного забезпечення та управління командами.",
            instructor_name="Ушакова І.О.",
            material_summary="Agile, Scrum, життєвий цикл ПЗ, аналіз чинників ризику, використання AI інструментів (GitHub Copilot, Cursor) у розробці.",
            has_practical_labs=False,
            credits=3,
            course_year=4,
            specialty="Комп'ютерні науки"
        ),
        Discipline(
            title="Хмарні технології",
            description="Розгортання та адміністрування додатків у хмарних середовищах.",
            instructor_name="Шевченко В.А.",
            material_summary="AWS, Google Cloud, Docker, Kubernetes, мікросервісна архітектура, бази даних у хмарі.",
            has_practical_labs=True,
            credits=4,
            course_year=4,
            specialty="Комп'ютерні науки"
        )
    ]
    
    db.add_all(disciplines)
    db.commit()
    db.close()
    print("Базу даних успішно наповнено логічно розподіленими дисциплінами!")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_data()