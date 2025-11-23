"""
Скрипт для очистки базы данных
Удаляет все старые reviews из БД
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def clear_all_reviews():
    """Очистить все reviews из БД"""
    print("🗑️ Очищаю базу данных...")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Удалить все reviews
        result = conn.execute(text("DELETE FROM code_reviews"))
        conn.commit()
        
        print(f"✅ Удалено {result.rowcount} reviews")
        
        # Проверить что пусто
        count = conn.execute(text("SELECT COUNT(*) FROM code_reviews")).scalar()
        print(f"📊 В БД осталось reviews: {count}")

if __name__ == "__main__":
    clear_all_reviews()
