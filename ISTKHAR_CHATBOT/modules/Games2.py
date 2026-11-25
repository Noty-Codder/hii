import random
import secrets

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from ISTKHAR_CHATBOT import ISTKHAR_CHATBOT

# ---------------------------------------------------------------- state (in memory)

TTT_GAMES = {}     # key -> {"board": [...], "over": bool}
GUESS_GAMES = {}   # chat_id -> {"secret": int, "tries": int}
HANGMAN_GAMES = {} # chat_id -> {"word": str, "guessed": set, "wrong": int}
QUIZ = {}          # key -> correct option index

WORDS = ["python", "telegram", "bot", "music", "chatbot", "heroku", "cricket", "mango"]
HANG_STAGES = ["😀", "😐", "😕", "😟", "😨", "💀", "☠️"]

QUIZ_QUESTIONS = [
    ("Bharat ki rajdhani kya hai?", ["Mumbai", "New Delhi", "Kolkata", "Chennai"], 1),
    ("Pani ka chemical formula kya hai?", ["CO2", "H2O", "O2", "NaCl"], 1),
    ("Ek saptah mein kitne din hote hain?", ["5", "6", "7", "8"], 2),
    ("Python ek kya hai?", ["Snake", "Programming language", "Game", "Fruit"], 1),
]


def _key():
    return secrets.token_hex(4)


# ---------------------------------------------------------------- tic-tac-toe

WIN_LINES = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]


def _winner(board):
    for a, b, c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if all(board):
        return "draw"
    return None


def _ttt_markup(key, board, over=False):
    rows = []
    for r in range(3):
        row = []
        for c in range(3):
            i = r * 3 + c
            label = board[i] or "·"
            cb = "gm_noop" if (over or board[i]) else f"gm_ttt_{key}_{i}"
            row.append(InlineKeyboardButton(label, callback_data=cb))
        rows.append(row)
    return InlineKeyboardMarkup(rows)


@ISTKHAR_CHATBOT.on_cmd("ttt")
async def ttt_start(client, m: Message):
    key = _key()
    TTT_GAMES[key] = {"board": [""] * 9, "over": False}
    await m.reply_text("❌⭕ **Tic-Tac-Toe**\nTum ❌ ho, bot ⭕.", reply_markup=_ttt_markup(key, TTT_GAMES[key]["board"]))


def _bot_move(board):
    empty = [i for i, v in enumerate(board) if not v]
    # Win if possible, else block, else random
    for player, pick_from in (("O", empty), ("X", empty)):
        for i in pick_from:
            test = board.copy()
            test[i] = player
            if _winner(test) == player:
                return i
    return random.choice(empty)


# ---------------------------------------------------------------- quiz

@ISTKHAR_CHATBOT.on_cmd("quiz")
async def quiz(client, m: Message):
    q, options, correct = random.choice(QUIZ_QUESTIONS)
    key = _key()
    QUIZ[key] = correct
    rows = [[InlineKeyboardButton(opt, callback_data=f"gm_q_{key}_{i}")] for i, opt in enumerate(options)]
    await m.reply_text(f"📚 {q}", reply_markup=InlineKeyboardMarkup(rows))


# ---------------------------------------------------------------- guess the number

@ISTKHAR_CHATBOT.on_cmd("guess")
async def guess_start(client, m: Message):
    GUESS_GAMES[m.chat.id] = {"secret": random.randint(1, 100), "tries": 0}
    await m.reply_text("🔢 Maine 1 se 100 ke beech ek number socha hai.\nGuess karne ke liye: `/g 42`")


@ISTKHAR_CHATBOT.on_cmd("g")
async def guess_try(client, m: Message):
    game = GUESS_GAMES.get(m.chat.id)
    if not game:
        return await m.reply_text("Pehle `/guess` se game shuru karo.")
    if len(m.command) < 2 or not m.command[1].isdigit():
        return await m.reply_text("Use: `/g 42`")
    n = int(m.command[1])
    game["tries"] += 1
    if n == game["secret"]:
        GUESS_GAMES.pop(m.chat.id, None)
        return await m.reply_text(f"🎉 Sahi jawab! {game['secret']} tha. {game['tries']} try mein.")
    hint = "Zyada" if n < game["secret"] else "Kam"
    await m.reply_text(f"{hint} socho.")


# ---------------------------------------------------------------- hangman

def _hang_view(game):
    shown = " ".join(ch if ch in game["guessed"] else "_" for ch in game["word"])
    wrong = ", ".join(sorted(game["guessed"] - set(game["word"]))) or "none"
    return f"{HANG_STAGES[min(game['wrong'], len(HANG_STAGES) - 1)]} `{shown}`\nGalat letters: {wrong}"


@ISTKHAR_CHATBOT.on_cmd("hangman")
async def hangman_start(client, m: Message):
    HANGMAN_GAMES[m.chat.id] = {"word": random.choice(WORDS), "guessed": set(), "wrong": 0}
    await m.reply_text("🪢 Hangman shuru! Letter guess karne ke liye: `/hg a`\n\n" + _hang_view(HANGMAN_GAMES[m.chat.id]))


@ISTKHAR_CHATBOT.on_cmd("hg")
async def hangman_guess(client, m: Message):
    game = HANGMAN_GAMES.get(m.chat.id)
    if not game:
        return await m.reply_text("Pehle `/hangman` se game shuru karo.")
    if len(m.command) < 2 or len(m.command[1]) != 1 or not m.command[1].isalpha():
        return await m.reply_text("Use: `/hg a`")
    letter = m.command[1].lower()
    if letter in game["guessed"]:
        return await m.reply_text("Ye letter pehle guess ho chuka hai.")
    game["guessed"].add(letter)
    if letter not in game["word"]:
        game["wrong"] += 1
    if all(ch in game["guessed"] for ch in game["word"]):
        HANGMAN_GAMES.pop(m.chat.id, None)
        return await m.reply_text(f"🎉 Jeet gaye! Word tha **{game['word']}**.")
    if game["wrong"] >= 6:
        HANGMAN_GAMES.pop(m.chat.id, None)
        return await m.reply_text(f"💀 Hang ho gaye! Word tha **{game['word']}**.")
    await m.reply_text(_hang_view(game))


# ---------------------------------------------------------------- callbacks
# group=-1: runs before the generic callback handler in Callback.py.

@ISTKHAR_CHATBOT.on_callback_query(filters.regex(r"^gm_"), group=-1)
async def games2_callbacks(client, q: CallbackQuery):
    parts = q.data.split("_")

    if q.data == "gm_noop":
        return await q.answer()

    if parts[1] == "ttt":
        key, idx = parts[2], int(parts[3])
        game = TTT_GAMES.get(key)
        if not game or game["over"]:
            return await q.answer("Ye game khatam ho chuka hai.", show_alert=True)
        board = game["board"]
        if board[idx]:
            return await q.answer("Ye jagah bhari hai.")
        board[idx] = "X"
        result = _winner(board)
        if not result:
            bot_i = _bot_move(board)
            board[bot_i] = "O"
            result = _winner(board)
        if result:
            game["over"] = True
            text = {"X": "🎉 Tum jeet gaye!", "O": "🤖 Bot jeet gaya!", "draw": "🤝 Draw!"}[result]
            return await q.edit_message_text(f"❌⭕ **Tic-Tac-Toe**\n{text}", reply_markup=_ttt_markup(key, board, over=True))
        await q.edit_message_text("❌⭕ **Tic-Tac-Toe**\nTumhari baari.", reply_markup=_ttt_markup(key, board))

    elif parts[1] == "q":
        key, choice = parts[2], int(parts[3])
        correct = QUIZ.pop(key, None)
        if correct is None:
            return await q.answer("Ye quiz khatam ho chuka hai.", show_alert=True)
        verdict = "✅ Sahi jawab!" if choice == correct else "❌ Galat jawab."
        await q.edit_message_text(verdict)
