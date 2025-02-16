import sqlite3

def create_connection():
    conn = sqlite3.connect('crypto_bot.db')
    return conn
def get_alerts():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM alerts;")
    alerts = cursor.fetchall()
    conn.close()
    return alerts
def check_specific_alert(symbol, price):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Запит для перевірки конкретного алерта
    cursor.execute("SELECT symbol, price FROM alerts WHERE symbol = ? AND price = ?", (symbol, price))
    alert = cursor.fetchone()  # Отримаємо перший знайдений алерт (якщо є)
    
    conn.close()
    
    return alert
def check_alert_command(update, context):
    if len(context.args) != 2:
        update.message.reply_text("Правильний формат: /checkalert <символ> <ціна>")
        return
    
    symbol = context.args[0].upper()  # Наприклад, "ETHUSDT"
    price = float(context.args[1])  # Ціна як float
    
    alert = check_specific_alert(symbol, price)  # Викликаємо функцію для перевірки алерта
    
    if alert:
        update.message.reply_text(f"Алерт для {alert[0]} встановлений на ціну {alert[1]}$.")
    else:
        update.message.reply_text(f"Не знайдено алерта для {symbol} на ціну {price}$.")



def add_alert(symbol, price, chat_id):
    conn = create_connection()  # Використовуємо функцію create_connection
    cursor = conn.cursor()
    cursor.execute("INSERT INTO alerts (symbol, price, chat_id) VALUES (?, ?, ?)", (symbol, price, chat_id))
    conn.commit()
    conn.close()

def create_tables():
    try:
        conn = sqlite3.connect('crypto_bot.db')
        cursor = conn.cursor()

        # Створення таблиць
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_ids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER UNIQUE
        );
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT,
            price REAL,
            chat_id INTEGER,
            FOREIGN KEY(chat_id) REFERENCES chat_ids(id) 
        );
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            symbol TEXT PRIMARY KEY,
            open_price REAL,
            last_checked DATETIME
        );
        ''')

        conn.commit()
        print("Таблиці створено успішно!")

    except sqlite3.Error as e:
        print(f"Помилка: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_tables()
