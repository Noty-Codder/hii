import ast
import operator
import random

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from ISTKHAR_CHATBOT import ISTKHAR_CHATBOT
from ISTKHAR_CHATBOT.modules.helpers.read import COLOURS

# ---------------------------------------------------------------- content

EIGHT_BALL = [
    "Haan, zaroor.", "Bilkul pakka.", "Abhi ke liye haan.", "Shayad.",
    "Mushkil se lagta hai.", "Nahi.", "Bilkul nahi.", "Dobara pucho baad mein.",
]

JOKES = [
    "Teacher: Bataao 'ghar' ka plural kya hai?\nStudent: Sir, 'ghar-wale'.",
    "Doctor: Aap roz 10 km walk karo.\nPatient: Doctor sahab, aap ne toh kaha tha bas 5 min ki exercise.",
    "Wifi ka password maangne ka sabse sahi tareeka: 'Bhai, net chal raha hai kya?'",
    "Mummy: Padhai kab karogi?\nBeta: Jab exam ka date aayega.\nMummy: Date toh aa gayi.\nBeta: Haan, par mera mood nahi aaya.",
]

FACTS = [
    "Honey kabhi kharab nahi hota. Purane Egypt ke maqbaron mein bhi khana mila hai jo sadiyon purana tha.",
    "Octopus ke teen dil hote hain.",
    "Bijli ki raftaar roshni se thodi kam hoti hai, par bahut tez hoti hai.",
    "Kela ek berry maana jata hai, par strawberry nahi.",
]

QUOTES = [
    "Mehnat ka phal hamesha milta hai, bas thoda intezaar karna padta hai.",
    "Jo gir ke uthta hai, wahi aage badhta hai.",
    "Sapne wo nahi jo sote waqt aate hain, sapne wo hain jo sone nahi dete.",
    "Waqt sabse bada teacher hai, par woh students ko kho deta hai.",
    "Khud pe yakeen rakho, duniya bhi yakeen karegi.",
]

RIDDLES = [
    ("Mujhe todo toh bolta hoon, par kabhi awaaz nahi karta. Main kya hoon?", "Khamoshi"),
    ("Jitna zyada loge utna chhota hota jaata hoon. Main kya hoon?", "Umr"),
    ("Chalta hai par pair nahi, sab kuch dekhta hai par aankh nahi. Kya hai?", "Samay"),
]

RIDDLE_ANSWERS = {}  # message_id -> answer

TRUTHS = [
    "Aapka sabse bada jhooth kya tha?",
    "Aapka pehla crush kaun tha?",
    "Aapne aakhri baar kab ro ke dekha tha?",
]
DARES = [
    "Apne group ko ek sher likh kar bhejo.",
    "Apne phone ka wallpaper 1 ghante ke liye batao.",
    "Kisi dost ko 'Good morning' bhejo.",
]
RPS_CHOICES = ["✊ Rock", "✋ Paper", "✌️ Scissors"]
SLOT_SYMBOLS = ["🍒", "🍋", "🔔", "⭐", "7️⃣"]


def _c():
    return random.choice(COLOURS)


def _main_text():
    return (
        f"{_c()} **ᴋᴀᴠʏᴀ ʜᴜʙ** {_c()}\n\n"
        "ʜᴇʀᴇ ɪs ᴡʜᴀᴛ ɪ ᴄᴀɴ ᴅᴏ:\n"
        "➪ ɢᴀᴍᴇs ᴀɴᴅ ғᴜɴ\n"
        "➪ ǫᴜᴏᴛᴇs, ᴊᴏᴋᴇs ᴀɴᴅ ғᴀᴄᴛs\n"
        "➪ ᴄᴀʟᴄᴜʟᴀᴛᴏʀ\n"
    )


def _main_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Games", callback_data="fun_games"),
         InlineKeyboardButton("😂 Fun", callback_data="fun_fun")],
        [InlineKeyboardButton("💬 Quotes", callback_data="fun_quote"),
         InlineKeyboardButton("🧮 Calc", callback_data="fun_calc")],
        [InlineKeyboardButton("❌ Close", callback_data="fun_close")],
    ])


def _back_markup():
    return InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Back", callback_data="fun_home")]])


# ---------------------------------------------------------------- safe calculator

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval(expr: str):
    """Evaluate simple arithmetic only. No names, calls or attribute access."""
    if len(expr) > 100:
        raise ValueError("Expression bahut lamba hai.")

    def _ev(node):
        if isinstance(node, ast.Expression):
            return _ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_ev(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            left, right = _ev(node.left), _ev(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise ValueError("Power bahut bada hai.")
            return _OPS[type(node.op)](left, right)
        raise ValueError("Sirf numbers aur + - * / % ** chalega.")

    return _ev(ast.parse(expr, mode="eval"))


# ---------------------------------------------------------------- commands

@ISTKHAR_CHATBOT.on_cmd("hub")
async def fun_hub(client, m: Message):
    await m.reply_text(_main_text(), reply_markup=_main_markup())


@ISTKHAR_CHATBOT.on_cmd("8ball")
async def eight_ball(client, m: Message):
    await m.reply_text(f"🎱 {random.choice(EIGHT_BALL)}")


@ISTKHAR_CHATBOT.on_cmd("joke")
async def joke(client, m: Message):
    await m.reply_text(f"😂 {random.choice(JOKES)}")


@ISTKHAR_CHATBOT.on_cmd("fact")
async def fact(client, m: Message):
    await m.reply_text(f"📖 {random.choice(FACTS)}")


@ISTKHAR_CHATBOT.on_cmd("quote")
async def quote(client, m: Message):
    await m.reply_text(f"💬 {random.choice(QUOTES)}")


@ISTKHAR_CHATBOT.on_cmd("calc")
async def calc(client, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("Use: `/calc 12*(3+4)`")
    expr = m.text.split(None, 1)[1]
    try:
        result = safe_eval(expr)
    except ZeroDivisionError:
        return await m.reply_text("❌ Zero se divide nahi ho sakta.")
    except Exception as ex:
        return await m.reply_text(f"❌ {ex}")
    await m.reply_text(f"🧮 `{expr}` = **{result}**")


@ISTKHAR_CHATBOT.on_cmd("riddle")
async def riddle(client, m: Message):
    q, a = random.choice(RIDDLES)
    sent = await m.reply_text(
        f"🧩 {q}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👀 Show answer", callback_data=f"fun_ans_{m.id}")]]),
    )
    RIDDLE_ANSWERS[sent.id] = a


@ISTKHAR_CHATBOT.on_cmd("lovemeter")
async def lovemeter(client, m: Message):
    names = m.text.split(None, 1)[1] if len(m.command) > 1 else ""
    if not names:
        return await m.reply_text("Use: `/lovemeter Name1 Name2`")
    # Stable score for the same pair of names
    score = sum(ord(ch) for ch in names.lower()) % 101
    await m.reply_text(f"💘 **{names}**\nLove meter: **{score}%**")


@ISTKHAR_CHATBOT.on_cmd("dice")
async def dice(client, m: Message):
    await m.reply_dice()


@ISTKHAR_CHATBOT.on_cmd("rps")
async def rps(client, m: Message):
    await m.reply_text(f"🤖 Mera choice: **{random.choice(RPS_CHOICES)}**")


@ISTKHAR_CHATBOT.on_cmd("slots")
async def slots(client, m: Message):
    reels = [random.choice(SLOT_SYMBOLS) for _ in range(3)]
    result = " | ".join(reels)
    verdict = "🎉 Jackpot!" if len(set(reels)) == 1 else "Try again."
    await m.reply_text(f"🎰 {result}\n{verdict}")


@ISTKHAR_CHATBOT.on_cmd("truth")
async def truth(client, m: Message):
    await m.reply_text(f"🟦 Truth: {random.choice(TRUTHS)}")


@ISTKHAR_CHATBOT.on_cmd("dare")
async def dare(client, m: Message):
    await m.reply_text(f"🟥 Dare: {random.choice(DARES)}")


# ---------------------------------------------------------------- menu callbacks
# group=-1 runs before the generic callback handler in Callback.py.

@ISTKHAR_CHATBOT.on_callback_query(filters.regex(r"^fun_"), group=-1)
async def fun_callbacks(client, q: CallbackQuery):
    data = q.data

    if data == "fun_home":
        await q.edit_message_text(_main_text(), reply_markup=_main_markup())
    elif data == "fun_games":
        await q.edit_message_text(
            "🎮 **ɢᴀᴍᴇs**\n\n/8ball <sawaal>\n/riddle\n/dice\n/rps\n/slots\n/truth\n/dare\n/lovemeter <name1> <name2>\n/ttt\n/quiz\n/guess then /g <number>\n/hangman then /hg <letter>\n/calc <expression>",
            reply_markup=_back_markup(),
        )
    elif data == "fun_fun":
        await q.edit_message_text(
            "😂 **ғᴜɴ**\n\n/joke\n/fact\n/quote\n/lovemeter <name1> <name2>",
            reply_markup=_back_markup(),
        )
    elif data == "fun_quote":
        await q.edit_message_text(f"💬 {random.choice(QUOTES)}", reply_markup=_back_markup())
    elif data == "fun_calc":
        await q.edit_message_text(
            "🧮 **ᴄᴀʟᴄᴜʟᴀᴛᴏʀ**\n\nUse: `/calc 12*(3+4)`\nSupports + - * / % **",
            reply_markup=_back_markup(),
        )
    elif data == "fun_close":
        await q.message.delete()
    elif data.startswith("fun_ans_"):
        answer = RIDDLE_ANSWERS.pop(q.message.id, "Answer nahi mila.")
        await q.answer(f"Answer: {answer}", show_alert=True)
    # Anything else is left for other handlers.
