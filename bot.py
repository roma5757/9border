import telebot
from telebot import types
import json
import os

TOKEN = "8723811549:AAHjidPHxT0L9VgrDBtDXFsB970BK_dLc1c"
ADMIN_IDS = [2064987454]  # <- сюда можно добавить несколько админов
bot = telebot.TeleBot(TOKEN)

GIVEAWAYS_FILE = "giveaways_list.json"
TAKEN_FILE = "taken_giveaways.json"

# Загружаем раздачи
if os.path.exists(GIVEAWAYS_FILE):
    with open(GIVEAWAYS_FILE, "r", encoding="utf-8") as f:
        GIVEAWAYS = json.load(f)
else:
    GIVEAWAYS = {}

# Загружаем занятые раздачи
if os.path.exists(TAKEN_FILE):
    with open(TAKEN_FILE, "r", encoding="utf-8") as f:
        taken_giveaways = json.load(f)
else:
    taken_giveaways = {}

# Сохраняем занятые раздачи
def save_taken():
    with open(TAKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(taken_giveaways, f, ensure_ascii=False)

# Создание клавиатуры
def create_keyboard():
    markup = types.InlineKeyboardMarkup()
    for key in GIVEAWAYS.keys():
        if key not in taken_giveaways:
            markup.add(types.InlineKeyboardButton(key, callback_data=key))
    return markup

# /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = create_keyboard()
    if markup.keyboard:
        bot.send_message(
            message.chat.id,
            "Привет! 👋 Выбери раздачу ниже и получи свой бонус:",
            reply_markup=markup
        )
    else:
        bot.send_message(message.chat.id, "🎉 Все раздачи уже забраны!")

# /add - добавление новой раздачи админом
@bot.message_handler(commands=['add'])
def add_giveaway(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ Только админ может добавлять раздачи!")
        return

    try:
        parts = message.text.split("|")
        if len(parts) != 2:
            bot.reply_to(message, "❌ Используй формат: /add Название раздачи | Сообщение бонуса")
            return

        title = parts[0].replace("/add", "").strip()
        bonus = parts[1].strip()

        if title in GIVEAWAYS:
            bot.reply_to(message, "❌ Такая раздача уже существует!")
            return

        GIVEAWAYS[title] = bonus
        with open(GIVEAWAYS_FILE, "w", encoding="utf-8") as f:
            json.dump(GIVEAWAYS, f, ensure_ascii=False)
        bot.reply_to(message, f"✅ Раздача '{title}' добавлена!")

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")

# /view - посмотреть кто забрал раздачи (username)
@bot.message_handler(commands=['view'])
def view_taken(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ Только админ может видеть кто забрал раздачи!")
        return

    if not taken_giveaways:
        bot.reply_to(message, "ℹ️ Пока никто не забрал раздачи.")
        return

    text = "📋 Раздачи и пользователи:\n\n"
    for giveaway, username in taken_giveaways.items():
        text += f"{giveaway} — @{username}\n"  # отображаем username
    bot.reply_to(message, text)

# Обработка нажатий
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # получаем username или имя пользователя
    username = call.from_user.username or call.from_user.first_name
    selection = call.data

    if selection in GIVEAWAYS:
        if selection in taken_giveaways:
            bot.answer_callback_query(call.id, "❌ Эта раздача уже занята другим пользователем!")
        else:
            taken_giveaways[selection] = username  # сохраняем username
            save_taken()
            bot.answer_callback_query(call.id, "✅ Раздача отправлена!")
            bot.send_message(call.message.chat.id, f"{GIVEAWAYS[selection]}")

            markup = create_keyboard()
            if markup.keyboard:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
            else:
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
                bot.send_message(call.message.chat.id, "🎉 Все раздачи уже забраны!")
    else:
        bot.answer_callback_query(call.id, "⚠️ Ошибка, попробуй ещё раз!")

print("Бот запущен...")
bot.polling()