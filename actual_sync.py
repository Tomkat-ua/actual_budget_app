import config as c,db
import requests
from datetime import datetime

# Псевдокод для отримання категорій
def get_actual_categories():
    # Виклик до твого інстансу Actual Budget
    # Повертає список типу: [{'id': 'uuid-1', 'name': 'Продукти'}, ...]
    import requests
    url = f"{c.actual_api_url}/v1/budgets/{c.actual_sync_id}/categories"
    headers = {
        "x-api-key": c.actual_api_key,
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Отримуємо основний словник
        json_response = response.json()

        # Дістаємо список з ключа "data"
        categories_data = json_response.get('data', [])

        flat_categories = []
        for cat in categories_data:
            # Ігноруємо приховані категорії, якщо потрібно
            if cat.get('hidden'):
                continue

            flat_categories.append({
                'id': cat.get('id'),
                'name': cat.get('name'),
                'is_income': cat.get('is_income')
            })

        return flat_categories

    except Exception as e:
        print(f"❌ Помилка парсингу категорій: {e}")
        return []


def sync_actual_categories_to_db( db_conn):
    # 1. Отримуємо категорії через твій виправлений парсер
    categories = get_actual_categories()  # функція з попереднього кроку

    if not categories:
        print("Категорії не знайдені або помилка API")
        return
    try:
        with db_conn.cursor() as cursor:
            sql = """
            INSERT INTO actual_categories (id, name, is_income)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                name = VALUES(name),
                is_income = VALUES(is_income)
            """

            data_to_update = [
                (c['id'], c['name'], 1 if c['is_income'] else 0)
                for c in categories
            ]

            cursor.executemany(sql, data_to_update)
            db_conn.commit()
            print(f"✅ Синхронізовано {len(categories)} категорій з Actual Budget.")

    except Exception as e:
        print(f"❌ Помилка запису в БД: {e}")

def sync_transactions():
    # 1. Читаємо JSON (твоя імітація через Nginx)
    # Використовуємо .json(), щоб отримати список словників
    try:
        response = requests.get(c.bank_api_url)
        response.raise_for_status()
        transactions = response.json()
    except Exception as e:
        print(f"Помилка запиту до банку: {e}")
        return
    conn = db.get_connection()
    try:
        data_to_insert = []
        for tx in transactions:
            # Конвертуємо Unix timestamp у формат MariaDB
            unix_time = tx.get('time')
            formatted_dt = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S') if unix_time else None

            data_to_insert.append((
                tx.get('id'),
                'Monobank',
                unix_time,
                formatted_dt,  # Наше нове поле
                tx.get('description'),
                tx.get('mcc'),
                tx.get('amount'),
                tx.get('operationAmount'),
                tx.get('currencyCode'),
                tx.get('commissionRate', 0),
                tx.get('cashbackAmount', 0),
                tx.get('balance'),
                1 if tx.get('hold') else 0,
                tx.get('receiptId'),
                tx.get('counterName')
            ))

        with conn.cursor() as cursor:
            # Викликаємо процедуру для кожної транзакції
            for tx_data in data_to_insert:
                cursor.callproc('UpsertTransaction', tx_data)
            conn.commit()
            print(f"Успішно оновлено. Додано нових записів: {cursor.rowcount}")
    finally:
        conn.close()

