from flask import Flask, render_template, request, redirect
import db


app = Flask(__name__)


@app.route('/mcc-mapping', methods=['GET', 'POST'])
def mcc_mapping():
    conn = db.get_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'POST':
                mcc = request.form.get('mcc')
                cat_id = request.form.get('cat_id')
                # Вставляємо мапінг у твою нову таблицю mcc_map
                cursor.execute(
                    "INSERT INTO mcc_map (mcc_code, cat_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE cat_id=VALUES(cat_id)",
                    (mcc, cat_id)
                )
                conn.commit()
                return redirect('/mcc-mapping')

            # 1. Отримуємо незмаплені MCC
            cursor.execute("""
                SELECT DISTINCT t.mcc, t.description 
                FROM transactions t
                LEFT JOIN mcc_map m ON t.mcc = m.mcc_code
                WHERE m.mcc_code IS NULL AND t.mcc IS NOT NULL
            """)
            unmapped = cursor.fetchall()

            # 2. Отримуємо категорії для випадаючого списку
            cursor.execute("SELECT id, name FROM actual_categories ORDER BY name")
            categories = cursor.fetchall()

    finally:
        conn.close() # Важливо закривати з'єднання

    return render_template('mcc_mapping.html', unmapped=unmapped, categories=categories)

@app.route('/sync-categories')
def sync_categories():
    import actual_sync # твій модуль, де лежить функція sync_actual_categories_to_db
    conn = db.get_connection()
    try:
        # s — твій словник секретів з Infisical
        actual_sync.sync_actual_categories_to_db(conn)
    finally:
        conn.close()
    return redirect('/mcc-mapping') # або на головну

#### 2. Перегляд та Експорт транзакцій (`/transactions`)

@app.route('/transactions')
def show_transactions():
    conn = db.get_connection()
    try:
        with conn.cursor() as cursor:
            # Виводимо лише змаплені транзакції, які ще не в бюджеті
            cursor.execute("""
                SELECT t.id, t.formatted_date, t.description, t.amount, c.name as cat_name
                FROM transactions t
                JOIN mcc_map m ON t.mcc = m.mcc_code
                JOIN actual_categories c ON m.cat_id = c.id
                WHERE t.imported_at IS NULL
                ORDER BY t.formatted_date DESC
            """)
            ready_tx = cursor.fetchall()
    finally:
        conn.close()
    return render_template('transactions.html', transactions=ready_tx)


@app.route('/')
def show_ready_transactions():
    conn = db.get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    t.formatted_date, 
                    t.description, 
                    t.amount, 
                    c.name as cat_name,
                    t.mcc
                FROM transactions t
                JOIN mcc_map m ON t.mcc = m.mcc_code
                JOIN actual_categories c ON m.cat_id = c.id
                WHERE t.imported_at IS NULL
                ORDER BY t.formatted_date DESC
            """
            cursor.execute(sql)
            transactions = cursor.fetchall()

            # Рахуємо загальну суму для перевірки
            total = sum(tx['amount'] for tx in transactions) / 100

    finally:
        conn.close()

    return render_template('ready_transactions.html',
                           transactions=transactions,
                           total=total)


@app.route('/fetch-data')
def fetch_data():
    from actual_sync import sync_transactions

    try:
        # Викликаємо твою готову процедуру
        sync_transactions()
        # Після успішного завантаження йдемо на мапінг
        return redirect('/mcc-mapping')
    except Exception as e:
        return f"Крах при синхронізації: {e}", 500
###############################################################################################################


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)