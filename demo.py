#!/usr/bin/env python3
"""
Демонстрация работы сервиса-советника по Сивасу
"""

from vector_store import SivasVectorStore
import json

def demo_search():
    """Демонстрация поиска по векторной базе данных"""
    print("🏛️  ДЕМОНСТРАЦИЯ СЕРВИСА-СОВЕТНИКА ПО СИВАСУ")
    print("=" * 50)
    
    # Инициализируем векторную БД
    print("📊 Загружаем векторную базу данных...")
    vs = SivasVectorStore()
    
    # Получаем статистику
    stats = vs.get_collection_stats()
    print(f"✅ Загружено {stats['total_chunks']} чанков контента")
    print()
    
    # Тестовые запросы
    test_queries = [
        "Какие достопримечательности есть в Сивасе?",
        "Что попробовать из еды в Сивасе?", 
        "Какие активности доступны туристам?",
        "Расскажите об истории Сиваса",
        "Что можно посмотреть за 48 часов?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"🔍 ЗАПРОС {i}: {query}")
        print("-" * 40)
        
        # Поиск релевантного контента
        results = vs.search(query, n_results=3)
        
        if results:
            print(f"📚 Найдено {len(results)} релевантных фрагментов:")
            
            for j, result in enumerate(results, 1):
                metadata = result.get('metadata', {})
                title = metadata.get('title', 'Без названия')
                category = metadata.get('category', 'general')
                text = result.get('text', '')[:200] + '...'
                
                print(f"\n{j}. 📄 {title} ({category})")
                print(f"   💬 {text}")
                
        else:
            print("❌ Релевантный контент не найден")
            
        print("\n" + "=" * 50)
    
    # Показываем доступные категории
    print("📋 ДОСТУПНЫЕ КАТЕГОРИИ КОНТЕНТА:")
    print("-" * 30)
    
    # Загружаем исходные данные для анализа
    with open('scraped_data/sivas_content.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    categories = {}
    for page in data:
        cat = page.get('category', 'general')
        categories[cat] = categories.get(cat, 0) + 1
    
    for category, count in categories.items():
        print(f"  • {category}: {count} страниц")
    
    print(f"\n📈 ОБЩАЯ СТАТИСТИКА:")
    total_words = sum(page.get('word_count', 0) for page in data)
    print(f"  • Всего страниц: {len(data)}")
    print(f"  • Всего слов: {total_words}")
    print(f"  • Чанков в БД: {stats['total_chunks']}")
    
    print("\n🎉 ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА!")
    print("Векторная база данных успешно работает и готова для интеграции с Claude API")

if __name__ == "__main__":
    demo_search()
