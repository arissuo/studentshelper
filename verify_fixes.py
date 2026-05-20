#!/usr/bin/env python3
"""
Скрипт для перевірки, що всі виправлення були застосовані коректно
"""

import os
import re
from pathlib import Path

def check_file_content(filepath, search_patterns):
    """Перевіряє наявність патернів в файлі"""
    if not os.path.exists(filepath):
        return False, f"❌ Файл не знайдено: {filepath}"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    missing = []
    for pattern_name, pattern in search_patterns:
        if not re.search(pattern, content, re.MULTILINE | re.DOTALL):
            missing.append(pattern_name)
    
    if missing:
        return False, f"❌ Відсутні: {', '.join(missing)}"
    return True, "✅ Усі виправлення знайдено"

# Перевірки для кожного файлу
checks = {
    "bot.py": [
        ("Таймаут в httpx", r"httpx\.AsyncClient\(.*timeout=30\.0.*\)"),
        ("Логування пагінації", r"\[PAGINATION\]"),
        ("Обробка помилок edit_text", r"if not callback\.message:"),
        ("Логування генерації програми", r"\[CURRICULUM\]"),
        ("Обробка помилок API", r'if "400" in error_msg:'),
    ],
    
    "ai_service.py": [
        ("Import logging", r"import logging"),
        ("Logger initialization", r"logger = logging\.getLogger\(__name__\)"),
        ("Логування початку", r"\[AI_SERVICE\] Starting curriculum generation"),
        ("Логування Gemini call", r"\[AI_SERVICE\] Sending request to Gemini API"),
        ("Детальна обробка JSON помилок", r"\[AI_SERVICE\] JSON decode error"),
        ("Логування успіху parsing", r"\[AI_SERVICE\] JSON parsed successfully"),
    ],
    
    "main.py": [
        ("Import logging", r"import logging"),
        ("Logger initialization", r"logger = logging\.getLogger\(__name__\)"),
        ("Логування початку генерації", r"\[API\] Starting curriculum generation"),
        ("Розділена обробка ValueError", r"except ValueError as e:"),
        ("Розділена обробка Exception", r"except Exception as e:"),
        ("Логування збереження", r"\[API\] Saving.*recommendations to database"),
    ],
}

print("=" * 70)
print("🔍 ПЕРЕВІРКА ВИПРАВЛЕНЬ ДЕБАГ-ПРОБЛЕМ")
print("=" * 70)
print()

all_passed = True
for filepath, patterns in checks.items():
    full_path = f"d:\\OneDrive\\Робочий стіл\\курсова3\\{filepath}"
    print(f"📄 Файл: {filepath}")
    
    passed, message = check_file_content(full_path, patterns)
    print(f"   {message}")
    
    if not passed:
        all_passed = False
    print()

print("=" * 70)
if all_passed:
    print("✅ ВСІ ВИПРАВЛЕННЯ ЗАСТОСОВАНІ УСПІШНО!")
    print()
    print("🎯 Наступні кроки:")
    print("   1. Запустіть API:  uvicorn main:app --reload")
    print("   2. Запустіть бот:  python bot.py")
    print("   3. Тестуйте пагінацію та генерацію програми")
    print("   4. Перевіряйте логи для [PAGINATION], [CURRICULUM], [API], [AI_SERVICE]")
else:
    print("❌ ДЕЯКІ ВИПРАВЛЕННЯ НЕ ЗНАЙДЕНО!")
    print("   Будь ласка, перевірте вищезазначені файли")
print("=" * 70)
