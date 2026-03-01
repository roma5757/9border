import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.enums import ParseMode

TOKEN = "8723811549:AAHjidPHxT0L9VgrDBtDXFsB970BK_dLc1c"

bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

participants = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Привет! Я бот для проведения розыгрышей 🎉")

@dp.message(Command("giveaway"))
async def create_giveaway(message: types.Message):
    if message.chat.type != "channel":
        await message.answer("Команду нужно использовать в канале.")
        return
    
    giveaway_id = random.randint(1000, 9999)
    participants[giveaway_id] = []

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎉 Участвовать", callback_data=f"join_{giveaway_id}")]
        ]
    )

    await message.answer(
        f"🎁 <b>РОЗЫГРЫШ!</b>\n\n"
        f"Нажми кнопку ниже, чтобы участвовать!",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data.startswith("join_"))
async def join_giveaway(callback: types.CallbackQuery):
    giveaway_id = int(callback.data.split("_")[1])

    if callback.from_user.id not in participants[giveaway_id]:
        participants[giveaway_id].append(callback.from_user.id)
        await callback.answer("Вы участвуете! 🎉", show_alert=True)
    else:
        await callback.answer("Вы уже участвуете!", show_alert=True)

@dp.message(Command("winner"))
async def choose_winner(message: types.Message):
    if message.chat.type != "channel":
        return

    if not participants:
        await message.answer("Нет активных розыгрышей.")
        return

    giveaway_id = list(participants.keys())[-1]
    users = participants[giveaway_id]

    if not users:
        await message.answer("Нет участников.")
        return

    winner = random.choice(users)

    await message.answer(f"🏆 Победитель: <a href='tg://user?id={winner}'>Участник</a>")

    del participants[giveaway_id]

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())