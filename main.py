import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

app = Flask(__name__)

# Налаштовуємо шлях до бази даних чітко всередині папки /instance
# Flask автоматично знайде або створить папку instance поруч із app.py
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'billing_system.db')}"

app.config['SECRET_KEY'] = 'billing-system-production-key-2026'
db = SQLAlchemy(app)


# --- ЄДИНА СТАБІЛЬНА МОДЕЛЬ ТРАНЗАКЦІЙ (РЕЄСТР БІЛІНГУ) ---
class BillingRegistry(db.Model):
    # Внутрішні системні поля білінгу
    id = db.Column(db.String(100), primary_key=True)  # Унікальний ID транзакції від банку
    bank_source = db.Column(db.String(50), default="Monobank")
    imported_at = db.Column(db.String(20))  # Дата/час реєстрації в нашому білінгу
    tx_type = db.Column(db.String(10), nullable=False)  # INCOME або EXPENSE

    # Повний набір оригінальних полів з банківської виписки (Data Ingestion як є)
    time = db.Column(db.Integer)  # Оригінальний UNIX timestamp
    formatted_date = db.Column(db.String(20))  # Читабельний формат (YYYY-MM-DD HH:MM:SS)
    description = db.Column(db.String(255))  # Назва торгової точки / Опис операції
    mcc = db.Column(db.Integer)  # Числовий код MCC
    original_mcc = db.Column(db.Integer)  # Оригінальний MCC торгової точки
    amount = db.Column(db.Integer)  # Сума в копійках (рахунок картки)
    operation_amount = db.Column(db.Integer)  # Сума в копійках (валюта операції)
    currency_code = db.Column(db.Integer)  # ISO код валюти (напр. 980)
    commission_rate = db.Column(db.Integer)  # Комісія банку в копійках
    cashback_amount = db.Column(db.Integer)  # Нарахований кешбек в копійках
    balance = db.Column(db.Integer)  # Залишок на балансі ПІСЛЯ проведення транзакції
    hold = db.Column(db.Boolean)  # Чи заблоковані гроші (холдування)
    receipt_id = db.Column(db.String(100), nullable=True)  # ID чеку/квитанції


@app.route('/')
def index():
    # Дістаємо абсолютно всі зареєстровані транзакції, сортуємо від нових до старих
    transactions = BillingRegistry.query.order_by(BillingRegistry.time.desc()).all()
    return render_template('index.html', transactions=transactions)


@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'bank_file' not in request.files:
        flash("Помилка: Файл виписки відсутній у запиті.")
        return redirect(url_for('index'))

    file = request.files['bank_file']
    if file.filename == '':
        flash("Помилка: Файл не вибрано.")
        return redirect(url_for('index'))

    if file and file.filename.endswith('.json'):
        try:
            raw_data = json.loads(file.read().decode('utf-8'))
            added_count = 0
            dup_count = 0

            for tx in raw_data:
                tx_id = str(tx.get('id'))

                # Захист від дублікатів на рівні первинного ключа білінгу
                if BillingRegistry.query.get(tx_id):
                    dup_count += 1
                    continue

                amount = tx.get('amount', 0)
                # Визначаємо фінансовий напрямок транзакції
                transaction_direction = "INCOME" if amount > 0 else "EXPENSE"

                # Перетворюємо UNIX-timestamp у зрозумілу дату для фінансового логу
                dt = datetime.fromtimestamp(tx.get('time', 0))

                # Записуємо ВСІ оригінальні параметри без жодних модифікацій чи округлень
                billing_entry = BillingRegistry(
                    id=tx_id,
                    bank_source="Monobank",
                    imported_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    tx_type=transaction_direction,

                    time=tx.get('time'),
                    formatted_date=dt.strftime('%Y-%m-%d %H:%M:%S'),
                    description=tx.get('description', 'Невідомий контрагент'),
                    mcc=tx.get('mcc'),
                    original_mcc=tx.get('originalMcc'),
                    amount=amount,
                    operation_amount=tx.get('operationAmount'),
                    currency_code=tx.get('currencyCode'),
                    commission_rate=tx.get('commissionRate'),
                    cashback_amount=tx.get('cashbackAmount'),
                    balance=tx.get('balance'),
                    hold=tx.get('hold'),
                    receipt_id=tx.get('receiptId')
                )
                db.session.add(billing_entry)
                added_count += 1

            db.session.commit()
            flash(
                f"Імпорт завершено успішно! Зареєстровано нових транзакцій: {added_count}. Виявлено дублікатів: {dup_count}")

        except Exception as e:
            db.session.rollback()
            flash(f"Критична помилка обробки фінансових даних: {str(e)}")
    else:
        flash("Помилка: Дозволено завантаження лише файлів формату .json")

    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Створить папку /instance та файл billing_system.db автоматично, якщо їх немає
    app.run(port=5000, debug=True)