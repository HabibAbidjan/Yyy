from keep_alive import keep_alive import telebot from telebot import types import random import time

TOKEN = "8161107014:AAH1I0srDbneOppDw4AsE2kEYtNtk7CRjOw" bot = telebot.TeleBot(TOKEN)

user_balances = {} user_games = {} user_aviator = {} ADMIN_ID = 5815294733

=== /start komandasi ===

@bot.message_handler(commands=['start']) def start(message): user_id = message.from_user.id user_balances.setdefault(user_id, 1000)

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup.add('💣 Play Mines', '🛩 Play Aviator')
markup.add('💰 Balance', '💸 Pul chiqarish')
markup.add('💳 Hisob toldirish')

bot.send_message(message.chat.id, "Xush kelibsiz! O'yinni tanlang:", reply_markup=markup)

=== Balance ===

@bot.message_handler(func=lambda m: m.text == "💰 Balance") def balance(message): user_id = message.from_user.id bal = user_balances.get(user_id, 0) bot.send_message(message.chat.id, f"💰 Balansingiz: {bal} so‘m")

=== Play Mines ===

@bot.message_handler(func=lambda m: m.text == "💣 Play Mines") def start_mines(message): user_id = message.from_user.id if user_id in user_games: bot.send_message(message.chat.id, "Avvalgi o‘yinni tugating yoki pulni yeching.") return msg = bot.send_message(message.chat.id, "🎯 Stavka miqdorini kiriting (min 1000):") bot.register_next_step_handler(msg, init_mines)

def init_mines(message): try: user_id = message.from_user.id stake = int(message.text) if stake < 1000: bot.send_message(message.chat.id, "❌ Kamida 1000 so‘m tikish kerak.") return if user_balances.get(user_id, 0) < stake: bot.send_message(message.chat.id, "❌ Yetarli balans yo‘q.") return

user_balances[user_id] -= stake
    bombs = random.sample(range(25), 3)
    user_games[user_id] = {
        'stake': stake,
        'bombs': bombs,
        'opened': [],
        'multiplier': 1.0
    }
    send_mines_board(message.chat.id, user_id, bomb_triggered=False)

except ValueError:
    bot.send_message(message.chat.id, "❌ Raqam kiriting.")

def send_mines_board(chat_id, user_id, bomb_triggered=False): game = user_games.get(user_id) if not game: return

markup = types.InlineKeyboardMarkup(row_width=5)
buttons = []

for i in range(25):
    if i in game['opened']:
        btn = types.InlineKeyboardButton("✅", callback_data="ignore")
    else:
        btn = types.InlineKeyboardButton(str(i + 1), callback_data=f"open_{i}")
    buttons.append(btn)

for i in range(0, 25, 5):
    markup.row(*buttons[i:i + 5])

if not bomb_triggered:
    markup.add(types.InlineKeyboardButton("💸 Pulni yechish", callback_data="cashout"))

text = f"""💣 MINES O'yini

Bombalar: 3 Stavka: {game['stake']} so‘m Multiplikator: x{round(game['multiplier'], 2)}""" bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True) def handle_callback(call): user_id = call.from_user.id if user_id not in user_games: bot.answer_callback_query(call.id, "O‘yin topilmadi.") return

game = user_games[user_id]

if call.data == "cashout":
    win = min(int(game['stake'] * game['multiplier']), int(game['stake'] * 2))
    user_balances[user_id] += win
    del user_games[user_id]
    bot.edit_message_text(f"{win} so‘m yutdingiz! Tabriklaymiz!", call.message.chat.id, call.message.message_id)
    return

if call.data.startswith("open_"):
    idx = int(call.data.split("_")[1])
    if idx in game['opened']:
        bot.answer_callback_query(call.id, "Bu katak ochilgan.")
        return

    if idx in game['bombs']:
        game['opened'] = list(set(game['opened'] + game['bombs']))
        send_mines_board(call.message.chat.id, user_id, bomb_triggered=True)
        del user_games[user_id]
        bot.edit_message_text("💥 Bomba topildi! Siz yutqazdingiz.", call.message.chat.id, call.message.message_id)
        return

    game['opened'].append(idx)
    game['multiplier'] *= 1.08
    send_mines_board(call.message.chat.id, user_id, bomb_triggered=False)

=== Aviator ===

@bot.message_handler(func=lambda m: m.text == "🛩 Play Aviator") def play_aviator(message): user_id = message.from_user.id if user_id in user_aviator: bot.send_message(message.chat.id, "⏳ Avvalgi Aviator o‘yini tugamagani uchun kuting.") return if user_balances.get(user_id, 0) < 1000: bot.send_message(message.chat.id, "❌ Kamida 1000 so‘m kerak.") return

user_balances[user_id] -= 1000
user_aviator[user_id] = True
multiplier = 1.0
crashed = False

for _ in range(30):
    time.sleep(0.7)
    multiplier = round(multiplier + random.uniform(0.1, 0.4), 2)
    if random.random() < 0.1:
        crashed = True
        break
    bot.send_message(message.chat.id, f"🛩 Ko‘tarilmoqda... x{multiplier}")

if crashed:
    bot.send_message(message.chat.id, "💥 Samolyot portladi! Siz yutqazdingiz.")
else:
    win = int(1000 * multiplier)
    user_balances[user_id] += win
    bot.send_message(message.chat.id, f"✅ Samolyot to‘liq uchdi! Yutuq: {win} so‘m")

del user_aviator[user_id]

=== Hisob toldirish ===

@bot.message_handler(func=lambda m: m.text == "💳 Hisob toldirish") def deposit(message): bot.send_message(message.chat.id, "💳 Hisob toldirish uchun quyidagi manzilga murojaat qiling: @YourAdminUsername\nYoki to‘lov uchun link: https://payme.uz/example")

=== Pul chiqarish ===

@bot.message_handler(func=lambda m: m.text == "💸 Pul chiqarish") def withdraw(message): user_id = message.from_user.id if user_balances.get(user_id, 0) < 5000: bot.send_message(message.chat.id, "❌ Minimal chiqarish 5000 so‘m.") return msg = bot.send_message(message.chat.id, "💳 Karta raqamingizni yuboring:") bot.register_next_step_handler(msg, process_withdraw)

def process_withdraw(message): user_id = message.from_user.id card = message.text amount = user_balances[user_id] user_balances[user_id] = 0

bot.send_message(message.chat.id, f"✅ So‘rov yuborildi. {amount} so‘m karta {card} raqamiga yuboriladi.")
bot.send_message(ADMIN_ID, f"📤 Yangi pul chiqarish so‘rovi:\n👤 Foydalanuvchi: @{message.from_user.username or user_id}\n💳 Karta: {card}\n💰 Miqdor: {amount} so‘m")

=== Bot ishga tushurish ===

print("Bot ishga tushdi...") keep_alive() bot.polling(none_stop=True)

