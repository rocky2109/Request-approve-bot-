from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import random

# Sample in-memory dictionary for active math games
math_games = {}

# Generates a random math question
def generate_question():
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    question = f"{a} + {b}"
    answer = a + b
    options = [answer, answer + 2, answer - 3, answer + 5]
    random.shuffle(options)
    return question, answer, options

# /math command handler
@Client.on_message(filters.command("math"))
async def start_math_game(client: Client, message: Message):
    user_id = message.from_user.id
    args = message.command[1:]

    if args and args[0].startswith("@"):
        opponent = args[0].replace("@", "")
        game_key = f"{user_id}-{opponent}"
        math_games[game_key] = {"players": [user_id, opponent], "score": {user_id: 0, opponent: 0}, "turn": user_id}
        await message.reply(f"🤝 Math game started with @{opponent}")
        await send_math_question(client, message.chat.id, game_key)
    else:
        game_key = f"{user_id}-bot"
        math_games[game_key] = {"players": [user_id, "BOT"], "score": {user_id: 0, "BOT": 0}, "turn": user_id}
        await message.reply("🧠 Math game started against BOT")
        await send_math_question(client, message.chat.id, game_key)

# Send question with buttons
async def send_math_question(client, chat_id, game_key):
    game = math_games[game_key]
    question, answer, options = generate_question()
    game["current_answer"] = answer

    buttons = [
        [InlineKeyboardButton(str(opt), callback_data=f"math_{game_key}_{opt}")]
        for opt in options
    ]
    markup = InlineKeyboardMarkup(buttons)
    await client.send_message(chat_id, f"❓ Solve: <b>{question}</b>", reply_markup=markup)

# Answer handler
@Client.on_callback_query(filters.regex(r"^math_"))
async def handle_math_answer(client, query):
    _, game_key, selected = query.data.split("_", 2)
    selected = int(selected)

    game = math_games.get(game_key)
    if not game:
        await query.answer("⚠️ Game not found", show_alert=True)
        return

    user_id = query.from_user.id
    correct = game["current_answer"]

    if selected == correct:
        game["score"][user_id] = game["score"].get(user_id, 0) + 1
        await query.answer("✅ Correct!", show_alert=False)
    else:
        await query.answer(f"❌ Wrong! Correct: {correct}", show_alert=True)

    await send_math_question(client, query.message.chat.id, game_key)
