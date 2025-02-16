import sqlite3

DB_FILE = "crypto_bot.db"

def check_alerts_in_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM alerts")
    alerts = cursor.fetchall()
    
    if not alerts:
        print("❌ Алерти не знайдено в базі!")
    else:
        print("✅ Виявлені алерти в базі:")
        for alert in alerts:
            print(alert)

    conn.close()

if __name__ == "__main__":
    check_alerts_in_db()