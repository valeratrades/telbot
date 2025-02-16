import requests
import asyncio
import sqlite3
import json
from datetime import datetime, timedelta
from telegram import Bot
from telegram.ext import Application, CommandHandler
import time
import threading
import logging


# Перевірка наявності символу на Binance
def get_current_price(symbol):
	url = f"https://fapi.binance.com/fapi/v2/ticker/price?symbol={symbol.upper()}"
	response = requests.get(url)
	data = response.json()

	# Перевірка, чи є символ в даних
	if "price" in data:
		return float(data["price"])
	else:
		return None  # Якщо символ не знайдено


# Створення з'єднання з базою даних
def create_connection():
	conn = sqlite3.connect("crypto_bot.db")
	return conn


# Перевірка алертів в базі даних
def check_alerts():
	conn = create_connection()
	cursor = conn.cursor()

	cursor.execute("SELECT * FROM alerts")
	alerts = cursor.fetchall()

	# Функція для видалення алерта з бази даних
	def delete_alert(alert_id):
		conn = create_connection()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
		conn.commit()
		conn.close()

	for alert in alerts:
		alert_id = alert[0]  # ID алерта
		symbol = alert[1].lstrip("/")  # Символ, прибираємо слеш, якщо він є
		alert_price = alert[2]  # Встановлена ціна
		chat_id = alert[3]  # Chat ID користувача

		current_price = get_current_price(symbol)

		if current_price is not None and current_price >= alert_price:
			message = f"🚨 {symbol} досяг {alert_price}$! Поточна ціна: {current_price}$."
			send_telegram_message(chat_id, message)

			# Видаляємо алерт після сповіщення
			delete_alert(alert_id)

	conn.close()


# Функція для надсилання повідомлень у Telegram
def send_telegram_message(chat_id, message):
	bot_token = "7567505791:AAE5Yqbd7gG9ydsx2_inJJmnS1Ln6rmh2Ts"
	url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
	payload = {"chat_id": chat_id, "text": message}
	requests.post(url, data=payload)


# Перевірка алертів періодично
def check_alerts_periodically():
	while True:
		check_alerts()  # Перевіряємо алерти
		time.sleep(3)  # Чекаємо 3 секунди перед наступною перевіркою


# Запуск перевірки в окремому потоці
alert_thread = threading.Thread(target=check_alerts_periodically)
alert_thread.daemon = True
alert_thread.start()


# Додавання нового алерта в базу даних
def add_alert(symbol, price, chat_id):
	conn = create_connection()
	cursor = conn.cursor()
	cursor.execute(
		"INSERT INTO alerts (symbol, price, chat_id) VALUES (?, ?, ?)",
		(symbol, price, chat_id),
	)
	conn.commit()
	conn.close()


# Функція для перевірки наявності алерта в базі даних
def check_alert(symbol, price):
	conn = create_connection()
	cursor = conn.cursor()

	cursor.execute("SELECT * FROM alerts WHERE symbol = ? AND price = ?", (symbol, price))
	alert = cursor.fetchone()

	conn.close()
	return alert


# Функція для перевірки символу на Binance
# TODO: load all symbols once on startup, check against it (pointless roundtrip rn)
def is_valid_symbol(symbol):
	# Видаляємо слеш перед символом, якщо він є
	symbol = symbol.lstrip("/")

	url = f"https://fapi.binance.com/fapi/v2/ticker/price?symbol={symbol.upper()}"
	response = requests.get(url)
	data = response.json()

	# Якщо символ не знайдений, повертаємо False
	return "price" in data


# Функція для обробки команди /addalert
async def add_alert_command(update, context):
	if len(context.args) != 2:
		await update.message.reply_text("Правильний формат: /addalert <символ> <ціна>")
		return

	symbol = context.args[0].upper()  # Наприклад, "ETHUSDT"
	price = float(context.args[1])  # Ціна як float
	chat_id = update.message.chat_id  # Ідентифікатор чату для прив'язки до користувача

	# Перевірка, чи є символ на Binance
	if not is_valid_symbol(symbol):
		await update.message.reply_text(f"Символ {symbol} не знайдений на Binance. Введіть правильний символ.")
		return

	add_alert(symbol, price, chat_id)  # Додаємо алерт в базу даних
	await update.message.reply_text(f"Алерт для {symbol} встановлений на ціну {price}$.")


# Функція для обробки команди /checkalert
async def check_alert_command(update, context):
	if len(context.args) != 2:
		await update.message.reply_text("Правильний формат: /checkalert <символ> <ціна>")
		return

	symbol = context.args[0].upper()  # Наприклад, "ETHUSDT"
	price = float(context.args[1])  # Ціна як float

	# Перевірка алерта в базі даних
	conn = create_connection()
	cursor = conn.cursor()

	cursor.execute("SELECT * FROM alerts WHERE symbol = ? AND price = ?", (symbol, price))
	alert = cursor.fetchone()  # Отримуємо перший знайдений алерт

	conn.close()

	if alert:
		await update.message.reply_text(f"Алерт для {symbol} встановлений на ціну {price}$.")
	else:
		await update.message.reply_text(f"Не знайдено алерта для {symbol} на ціну {price}$.")


TOKEN = "7567505791:AAE5Yqbd7gG9ydsx2_inJJmnS1Ln6rmh2Ts"
# Створення додатка для бота
application = Application.builder().token(TOKEN).build()

# Додаємо обробники команд
application.add_handler(CommandHandler("addalert", add_alert_command))
application.add_handler(CommandHandler("checkalert", check_alert_command))

# Запускаємо бота
if __name__ == "__main__":
	application.run_polling()

# Завантаження токену та Chat ID
CHAT_ID_FILE = "chat_ids.json"
try:
	with open(CHAT_ID_FILE, "r") as file:
		config = json.load(file)
except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
	print(f"Помилка завантаження JSON: {e}")
	config = {"TOKEN": "", "CHAT_ID": []}
	with open(CHAT_ID_FILE, "w") as file:
		json.dump(config, file)

TOKEN = config.get("TOKEN", "")
CHAT_IDS = config.get("CHAT_ID", [])

if not TOKEN:
	raise ValueError("Токен не знайдено або він порожній!")

BASE_URL = "https://fapi.binance.com"
ENDPOINT = "/fapi/v1/ticker/price"
THRESHOLDS = [0.01, 0.04, 0.09, 0.20]  # Пороги змін: 2%, 4%, 9%, 20%
CHECK_INTERVAL = 1.5  # Обмеження Binance - 1 раз на 1.5 секунди

bot = Bot(token=TOKEN)

# Словник для зберігання цін за ключем символу
price_history = {}

# Налаштування логування
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()


# Оновлена функція для отримання поточних цін з Binance
async def get_current_prices():
	try:
		logger.debug("Відправляється запит до API Binance для отримання цін...")
		response = requests.get(BASE_URL + ENDPOINT, timeout=5)
		logger.debug(f"Запит до API Binance, статус-код: {response.status_code}")

		if response.status_code == 200:
			prices = response.json()
			logger.debug(f"Отримані ціни: {prices}")
			return {item["symbol"]: float(item["price"]) for item in prices}
		else:
			logger.error(f"Помилка при отриманні цін: {response.status_code} - {response.text}")
			return {}
	except requests.exceptions.RequestException as e:
		logger.error(f"Помилка при запиті до API: {e}")
		return {}


# Оновлення функції для перевірки змін ціни
async def check_price_changes(new_prices):
	now = datetime.now()
	messages = []

	logger.debug(f"Перевірка зміни цін для: {new_prices}")

	for symbol, new_price in new_prices.items():
		data = price_history.get(symbol)

		# Якщо історія ціни для цього символу відсутня, зберігаємо поточну ціну
		if data is None:
			price_history[symbol] = {"open_price": new_price, "last_checked": now}
			logger.debug(f"Збережено нову ціну для {symbol}: {new_price}")
			continue

		open_price = data["open_price"]
		last_checked = data["last_checked"]

		# Якщо зміна ціни відбулась більше ніж 5 хвилин тому, зберігаємо нову ціну
		if now - last_checked >= timedelta(minutes=5):
			price_history[symbol] = {"open_price": new_price, "last_checked": now}
			logger.debug(f"Оновлення ціни для {symbol}: {new_price}")
			continue

		# Обчислюємо зміну ціни
		change = (new_price - open_price) / open_price
		abs_change = abs(change)

		# Перевіряємо чи зміна ціни перевищує пороги
		for threshold in THRESHOLDS:
			if abs_change >= threshold and not data.get(f"notified_{threshold}", False):
				direction = "🟢" if change > 0 else "🔴"
				change_percent = abs_change * 100
				message = f"{direction} {symbol} BINANCE 5m {change_percent:.1f}%"
				messages.append(message)
				price_history[symbol][f"notified_{threshold}"] = True
				logger.info(f"Відправлено сповіщення: {message}")
				break

	await send_notifications(messages)


# Оновлена функція для надсилання повідомлень
async def send_notifications(messages):
	if messages:
		full_message = "\n".join(messages)  # Об'єднуємо повідомлення в одне
		logger.debug(f"Готуємо повідомлення для надсилання: {full_message}")
		for chat_id in CHAT_IDS:
			try:
				await bot.send_message(chat_id=chat_id, text=full_message)
				logger.info(f"Сповіщення відправлено до {chat_id}: {full_message}")
			except Exception as e:
				logger.error(f"Помилка надсилання до {chat_id}: {e}")


async def main():
	while True:
		new_prices = await get_current_prices()
		if new_prices:
			await check_price_changes(new_prices)
		await asyncio.sleep(CHECK_INTERVAL)
