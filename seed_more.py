from database import SessionLocal, engine
from models import Discipline, Base

def seed_data():
    db = SessionLocal()
    
    disciplines = [
        Discipline(
            title="Алгоритми та структури даних",
            description="Вивчення базових і складних структур даних, алгоритмів пошуку, сортування та роботи з графами.",
            instructor_name="Павлюк О.М.",
            material_summary="Масиви, списки, дерева, хеш-таблиці, алгоритми на графах, оцінка складності O(n).",
            has_practical_labs=True,
            credits=5
        ),
        Discipline(
            title="Об'єктно-орієнтоване програмування",
            description="Основи ООП: інкапсуляція, успадкування, поліморфізм, створення класів та об'єктів.",
            instructor_name="Ковальчук І.В.",
            material_summary="Робота з C++ та Java, патерни проектування, SOLID-принципи, розробка графічних інтерфейсів.",
            has_practical_labs=True,
            credits=5
        ),
        Discipline(
            title="Організація баз даних",
            description="Проектування реляційних баз даних, написання SQL-запитів, нормалізація.",
            instructor_name="Григорчук А.С.",
            material_summary="РДБМС (PostgreSQL, MySQL), ключі, індекси, транзакції, процедури, тригери.",
            has_practical_labs=True,
            credits=4
        ),
        Discipline(
            title="Операційні системи",
            description="Принципи роботи сучасних ОС, управління пам'яттю, процесами та файловими системами.",
            instructor_name="Сидорчук В.П.",
            material_summary="Архітектура Linux/Windows, багатопоточність, синхронізація процесів, створення завантажувальних носіїв, кастомні прошивки.",
            has_practical_labs=True,
            credits=4
        ),
        Discipline(
            title="Комп'ютерні мережі",
            description="Архітектура та протоколи комп'ютерних мереж, маршрутизація, модель OSI та TCP/IP.",
            instructor_name="Романюк Т.І.",
            material_summary="Налаштування мережевого обладнання, IP-адресація, DNS, DHCP, аналіз трафіку.",
            has_practical_labs=True,
            credits=4
        ),
        Discipline(
            title="Web-технології та web-дизайн",
            description="Розробка фронтенд та бекенд частин веб-додатків, адаптивна верстка.",
            instructor_name="Левченко Д.О.",
            material_summary="HTML, CSS, JavaScript, React/Vue, основи роботи з REST API.",
            has_practical_labs=True,
            credits=5
        ),
        Discipline(
            title="Захист інформації",
            description="Методи шифрування, криптографія, захист мереж від несанкціонованого доступу.",
            instructor_name="Мороз Ю.В.",
            material_summary="Симетричне та асиметричне шифрування, RSA, хешування, цифрові підписи, аналіз вразливостей.",
            has_practical_labs=True,
            credits=3
        ),
        Discipline(
            title="Інженерія програмного забезпечення",
            description="Підходи до промислової розробки ПЗ, тестування, контроль версій та CI/CD.",
            instructor_name="Ткаченко М.С.",
            material_summary="Git, GitHub Actions, модульне тестування, рефакторинг, архітектурні патерни.",
            has_practical_labs=True,
            credits=4
        ),
        Discipline(
            title="Системи штучного інтелекту",
            description="Основи машинного навчання, нейромережі, обробка природної мови.",
            instructor_name="Кравченко О.П.",
            material_summary="Python, Pandas, Scikit-learn, TensorFlow, базові алгоритми класифікації та регресії.",
            has_practical_labs=True,
            credits=5
        ),
        Discipline(
            title="Дискретна математика",
            description="Математичні основи комп'ютерних наук: множини, логіка, комбінаторика, графи.",
            instructor_name="Бойко Н.І.",
            material_summary="Теорія множин, булева алгебра, графи та дерева, машини Тюрінга.",
            has_practical_labs=False,
            credits=4
        ),
        Discipline(
            title="Хмарні технології",
            description="Розгортання та адміністрування додатків у хмарних середовищах.",
            instructor_name="Шевченко В.А.",
            material_summary="AWS, Google Cloud, Docker, Kubernetes, мікросервісна архітектура, бази даних у хмарі.",
            has_practical_labs=True,
            credits=4
        ),
        Discipline(
            title="Розробка мобільних додатків",
            description="Створення нативних та кросплатформних додатків для iOS та Android.",
            instructor_name="Мартинюк С.О.",
            material_summary="Flutter / Dart, робота з мобільними сенсорами, локальні бази даних (SQLite), публікація в сторах.",
            has_practical_labs=True,
            credits=4
        )
     ]
    db.add_all(disciplines)
    db.commit()
    db.close()
    print("Базу даних успішно наповнено реалістичними дисциплінами!")

if __name__ == "__main__":
    # Створюємо таблиці, якщо їх раптом ще немає
    Base.metadata.create_all(bind=engine)
    seed_data()