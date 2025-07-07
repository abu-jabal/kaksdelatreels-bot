import logging
import random
import os
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ChatAction
from openai import OpenAI

# Загрузка ключей из .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Инициализация клиента OpenAI
client = OpenAI(api_key=openai_api_key)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOPICS = {
    "Психология": ["Почему прокрастинация — это не лень", "Как управлять эмоциями за 15 секунд"],
    "Маркетинг": ["Почему 99% людей покупают из-за эмоций", "Что нужно говорить, чтобы тебя запомнили"],
    "Бизнес": ["Как запустить продукт без денег", "Главная ошибка начинающих предпринимателей"]
}

HOOKS = [
    "что большинство людей не замечают",
    "что влияет на результативность",
    "что сдерживает тебя уже много лет"
]

CORES = [
    "страх ошибки сильнее желания выиграть",
    "продажи — это эмоции, не логика",
    "наш мозг цепляется за знакомое, даже если это мешает росту"
]

ADVICE = [
    "разбей задачу на микродействия",
    "замени фокус с результата на процесс",
    "запиши автоматические фразы и замени их на ресурсные"
]

def generate_script(selected_topic=None):
    try:
        topic = selected_topic if selected_topic else random.choice(list(TOPICS.keys()))
        title = random.choice(TOPICS[topic])
        hook = random.choice(HOOKS)
        core = random.choice(CORES)
        advice = random.choice(ADVICE)

        prompt = f"""
Ты — сценарист для Instagram Reels. Напиши короткий (60–90 сек) речевой текст от первого лица, живым языком.
Тема: {title}
Смысл: {core}
Хук: {hook}
Совет: {advice}

Формат:
- Вступление (захват внимания)
- Главная идея
- Пример
- Вывод с лёгким призывом

Язык: русский, тон — личный, энергичный, уверенный.
"""

        logging.info(f"Отправляю запрос в OpenAI по теме: {title}")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты сценарист, маркетолог и психолог. Пиши цепко и лаконично."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.85,
            max_tokens=400
        )

        text = response.choices[0].message.content
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        logging.info("Получил ответ от OpenAI")
        return f"🧠 *AI-Сценарий для Reels*\n📌 *{title}*\n🕒 {timestamp}\n\n{text}"
    except Exception as e:
        logging.error(f"Ошибка при генерации сценария: {e}")
        return "❌ Ошибка при генерации сценария. Попробуйте позже."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"User {update.effective_user.id} вызвал /start")
    keyboard = [[InlineKeyboardButton(topic, callback_data=topic)] for topic in TOPICS.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Выбери тему, по которой сгенерировать сценарий:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    topic = query.data
    logging.info(f"Пользователь выбрал тему: {topic}")
    await query.edit_message_text(text=f"Генерирую сценарий по теме: {topic}...")
    script = generate_script(topic)
    await query.message.reply_markdown(script)

async def script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"User {update.effective_user.id} вызвал /script")
    await update.message.chat.send_action(action=ChatAction.TYPING)
    text = generate_script()
    await update.message.reply_markdown(text)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("script", script))
    app.add_handler(CallbackQueryHandler(button))
    logging.info("Bot started!")
    app.run_polling()

