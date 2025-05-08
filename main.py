from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import random
from typing import Dict, List, Set, Tuple

users = {}
banned_users = set()
trades = {}
nicknames = {}
reverse_nicknames = {}

cases = {
    "case1": {
        "name": "Обычный кейс",
        "price": 100,
        "skins": [
            {"name": "AK-47 | Красная линия", "rarity": "Обычный", "price": 50},
            {"name": "AWP | Электрический hive", "rarity": "Обычный", "price": 60},
            {"name": "M4A4 | Зевс", "rarity": "Обычный", "price": 70},
            {"name": "Glock-18 | Водянистый", "rarity": "Обычный", "price": 40},
            {"name": "USP-S | Кровавый тигр", "rarity": "Обычный", "price": 55},
        ],
    },
    "case2": {
        "name": "Редкий кейс",
        "price": 500,
        "skins": [
            {"name": "Нож | Бабочка", "rarity": "Редкий", "price": 1000},
            {"name": "Перчатки | Спектр", "rarity": "Редкий", "price": 1200},
            {"name": "AWP | Дракон Лор", "rarity": "Редкий", "price": 800},
            {"name": "Karambit | Мраморный узор", "rarity": "Редкий", "price": 1500},
            {"name": "M9 Bayonet | Ультрафиолет", "rarity": "Редкий", "price": 1300},
        ],
    },
    "case3": {
        "name": "Эпический кейс",
        "price": 1000,
        "skins": [
            {"name": "Нож | Сапфир", "rarity": "Эпический", "price": 5000},
            {"name": "Перчатки | Дракон", "rarity": "Эпический", "price": 6000},
            {"name": "AWP | Медуза", "rarity": "Эпический", "price": 4000},
            {"name": "Karambit | Лоре", "rarity": "Эпический", "price": 7000},
            {"name": "M9 Bayonet | Рубин", "rarity": "Эпический", "price": 6500},
        ],
    },
    "case4": {
        "name": "Легендарный кейс",
        "price": 5000,
        "skins": [
            {"name": "Нож | Ультрафиолетовый дракон", "rarity": "Легендарный", "price": 10000},
            {"name": "Перчатки | Лунный свет", "rarity": "Легендарный", "price": 12000},
            {"name": "AWP | Галактический дракон", "rarity": "Легендарный", "price": 15000},
            {"name": "Karambit | Золотой тигр", "rarity": "Легендарный", "price": 20000},
            {"name": "M9 Bayonet | Алмазный король", "rarity": "Легендарный", "price": 25000},
        ],
    },
    "case5": {
        "name": "Мифический кейс",
        "price": 9999999,
        "skins": [
            {"name": "Нож | Космический император", "rarity": "Мифический", "price": 1000000},
            {"name": "Перчатки | Звездная пыль", "rarity": "Мифический", "price": 1200000},
            {"name": "AWP | Божественный дракон", "rarity": "Мифический", "price": 1500000},
            {"name": "Karambit | Небесный владыка", "rarity": "Мифический", "price": 2000000},
            {"name": "M9 Bayonet | Вечный огонь", "rarity": "Мифический", "price": 2500000},
        ],
    },
}

promo_codes = {
    "FREE100": 100,
    "CSGODROP": 500,
    "BIGMONEY": 1000,
    "STEPAN": 99999,
    "LEGENDARY": 5000
}

used_promo_codes = set()
ADMIN_PASSWORD = "vadimka"

WAITING_FOR_BAN = 1
WAITING_FOR_UNBAN = 2
WAITING_FOR_RESET = 3
WAITING_FOR_NICKNAME = 4
WAITING_FOR_TRADE_TARGET = 5
WAITING_FOR_TRADE_AMOUNT = 6
WAITING_FOR_TRADE_SKINS = 7
WAITING_FOR_TRADE_CONFIRMATION = 8
WAITING_FOR_TRANSFER_TARGET = 9
WAITING_FOR_TRANSFER_AMOUNT = 10

main_keyboard = ReplyKeyboardMarkup(
    [["💰 Баланс", "📦 Кейсы"],
     ["🎒 Инвентарь", "🎁 Промокод"],
     ["🏆 Топ игроков", "📝 Сменить ник"],
     ["💸 Перевести деньги", "🤝 Трейд"]],
    resize_keyboard=True
)

admin_keyboard = ReplyKeyboardMarkup(
    [["🔨 Забанить", "🔓 Разбанить"],
     ["💸 Сбросить деньги", "📊 Статистика"]],
    resize_keyboard=True
)

def is_banned(user_id: int) -> bool:
    return user_id in banned_users

def resolve_user_identifier(identifier: str):
    try:
        return int(identifier)
    except ValueError:
        return reverse_nicknames.get(identifier.lower())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if is_banned(user_id):
        await update.message.reply_text("Вы забанены и не можете использовать бота.")
        return

    if user_id not in users:
        users[user_id] = {"balance": 1000, "skins": []}
        default_nick = f"Игрок_{user_id % 1000:03d}"
        nicknames[user_id] = default_nick
        reverse_nicknames[default_nick.lower()] = user_id

    await update.message.reply_text(
        f"👋 Добро пожаловать, {nicknames[user_id]}!\n"
        f"💰 Ваш баланс: {users[user_id]['balance']}$\n"
        f"🆔 Ваш ID: {user_id}\n"
        f"📝 Ваш ник: {nicknames[user_id]}",
        reply_markup=main_keyboard
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    text = update.message.text

    if context.user_data.get('waiting_for') == WAITING_FOR_BAN:
        await process_ban(update, context)
        return
    elif context.user_data.get('waiting_for') == WAITING_FOR_UNBAN:
        await process_unban(update, context)
        return
    elif context.user_data.get('waiting_for') == WAITING_FOR_RESET:
        await process_reset(update, context)
        return
    elif context.user_data.get('waiting_for') == WAITING_FOR_NICKNAME:
        await process_nickname_change(update, context)
        return
    elif context.user_data.get('waiting_for') == WAITING_FOR_TRADE_TARGET:
        await process_trade_target(update, context)
        return
    elif context.user_data.get('waiting_for') == WAITING_FOR_TRADE_AMOUNT:
        await process_trade_amount(update, context)
        return
    elif context.user_data.get('waiting_for') == WAITING_FOR_TRADE_SKINS:
        await process_trade_skins(update, context)
        return
    elif context.user_data.get('waiting_for') == WAITING_FOR_TRADE_CONFIRMATION:
        await process_trade_confirmation(update, context)
        return
    elif context.user_data.get('waiting_for') == WAITING_FOR_TRANSFER_TARGET:
        await process_transfer_target(update, context)
        return
    elif context.user_data.get('waiting_for') == WAITING_FOR_TRANSFER_AMOUNT:
        await process_transfer_amount(update, context)
        return

    if text == "💰 Баланс":
        await show_balance(update, context)
    elif text == "📦 Кейсы":
        await show_cases(update, context)
    elif text == "🎒 Инвентарь":
        await inventory(update, context)
    elif text == "🎁 Промокод":
        await update.message.reply_text("Введите промокод:")
    elif text == "🏆 Топ игроков":
        await show_leaderboard(update, context)
    elif text == "📝 Сменить ник":
        context.user_data['waiting_for'] = WAITING_FOR_NICKNAME
        await update.message.reply_text("Введите новый никнейм (уникальный, без пробелов):")
    elif text == "🔨 Забанить":
        context.user_data['waiting_for'] = WAITING_FOR_BAN
        await update.message.reply_text("Введите ID или ник пользователя для бана:")
    elif text == "🔓 Разбанить":
        context.user_data['waiting_for'] = WAITING_FOR_UNBAN
        await update.message.reply_text("Введите ID или ник пользователя для разбана:")
    elif text == "💸 Сбросить деньги":
        context.user_data['waiting_for'] = WAITING_FOR_RESET
        await update.message.reply_text("Введите ID или ник пользователя для сброса денег и инвентаря:")
    elif text == "📊 Статистика":
        await show_admin_stats(update, context)
    elif text == "💸 Перевести деньги":
        context.user_data['waiting_for'] = WAITING_FOR_TRANSFER_TARGET
        await update.message.reply_text("Введите ID или ник получателя:")
    elif text == "🤝 Трейд":
        context.user_data['waiting_for'] = WAITING_FOR_TRADE_TARGET
        await update.message.reply_text("Введите ID или ник пользователя для трейда:")
    elif text in promo_codes:
        await activate_promo(update, context)
    else:
        await update.message.reply_text("Используйте кнопки для навигации", reply_markup=main_keyboard)

async def process_nickname_change(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    new_nick = update.message.text.strip()

    if not new_nick:
        await update.message.reply_text("Никнейм не может быть пустым!")
        return

    if len(new_nick) > 20:
        await update.message.reply_text("Никнейм слишком длинный (макс. 20 символов)!")
        return

    if ' ' in new_nick:
        await update.message.reply_text("Никнейм не должен содержать пробелов!")
        return

    if new_nick.lower() in reverse_nicknames and reverse_nicknames[new_nick.lower()] != user_id:
        await update.message.reply_text("Этот никнейм уже занят!")
        return

    if user_id in nicknames:
        old_nick = nicknames[user_id]
        if old_nick.lower() in reverse_nicknames:
            del reverse_nicknames[old_nick.lower()]

    nicknames[user_id] = new_nick
    reverse_nicknames[new_nick.lower()] = user_id

    await update.message.reply_text(
        f"✅ Ваш никнейм изменен на: {new_nick}",
        reply_markup=main_keyboard
    )
    context.user_data['waiting_for'] = None

async def process_ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    identifier = update.message.text.strip()
    target_id = resolve_user_identifier(identifier)

    if not target_id:
        await update.message.reply_text("❌ Пользователь не найден! Проверьте ID или никнейм.")
    else:
        banned_users.add(target_id)
        target_nick = nicknames.get(target_id, f"ID:{target_id}")
        await update.message.reply_text(
            f"🔨 Пользователь {target_nick} (ID:{target_id}) забанен.",
            reply_markup=admin_keyboard
        )

    context.user_data['waiting_for'] = None

async def process_unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    identifier = update.message.text.strip()
    target_id = resolve_user_identifier(identifier)

    if not target_id:
        await update.message.reply_text("❌ Пользователь не найден! Проверьте ID или никнейм.")
    else:
        banned_users.discard(target_id)
        target_nick = nicknames.get(target_id, f"ID:{target_id}")
        await update.message.reply_text(
            f"🔓 Пользователь {target_nick} (ID:{target_id}) разбанен.",
            reply_markup=admin_keyboard
        )

    context.user_data['waiting_for'] = None

async def process_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    identifier = update.message.text.strip()
    target_id = resolve_user_identifier(identifier)

    if not target_id:
        await update.message.reply_text("❌ Пользователь не найден! Проверьте ID или никнейм.")
    elif target_id not in users:
        await update.message.reply_text("❌ Пользователь не зарегистрирован в системе.")
    else:
        users[target_id]["balance"] = 0
        users[target_id]["skins"] = []
        target_nick = nicknames.get(target_id, f"ID:{target_id}")
        await update.message.reply_text(
            f"💸 Деньги и инвентарь пользователя {target_nick} (ID:{target_id}) сброшены.",
            reply_markup=admin_keyboard
        )

    context.user_data['waiting_for'] = None

async def process_transfer_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    identifier = update.message.text.strip()
    target_id = resolve_user_identifier(identifier)
    user_id = update.message.from_user.id

    if not target_id:
        await update.message.reply_text("❌ Пользователь не найден! Проверьте ID или никнейм.")
        context.user_data['waiting_for'] = None
        return

    if target_id == user_id:
        await update.message.reply_text("❌ Нельзя перевести деньги самому себе!")
        context.user_data['waiting_for'] = None
        return

    context.user_data['transfer_target'] = target_id
    context.user_data['waiting_for'] = WAITING_FOR_TRANSFER_AMOUNT
    await update.message.reply_text("Введите сумму для перевода:")

async def process_transfer_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    target_id = context.user_data['transfer_target']

    try:
        amount = int(update.message.text.strip())
        if amount <= 0:
            await update.message.reply_text("❌ Сумма должна быть положительной!")
            return

        if users[user_id]["balance"] < amount:
            await update.message.reply_text("❌ Недостаточно средств для перевода!")
            return

        users[user_id]["balance"] -= amount
        users[target_id]["balance"] += amount

        target_nick = nicknames.get(target_id, f"ID:{target_id}")
        await update.message.reply_text(
            f"✅ Вы перевели {amount}$ пользователю {target_nick}\n"
            f"💰 Ваш баланс: {users[user_id]['balance']}$",
            reply_markup=main_keyboard
        )
    except ValueError:
        await update.message.reply_text("❌ Введите корректную сумму!")
    finally:
        context.user_data['waiting_for'] = None
        context.user_data.pop('transfer_target', None)

async def process_trade_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    identifier = update.message.text.strip()
    target_id = resolve_user_identifier(identifier)
    user_id = update.message.from_user.id

    if not target_id:
        await update.message.reply_text("❌ Пользователь не найден! Проверьте ID или никнейм.")
        context.user_data['waiting_for'] = None
        return

    if target_id == user_id:
        await update.message.reply_text("❌ Нельзя совершить трейд с самим собой!")
        context.user_data['waiting_for'] = None
        return

    if target_id not in users:
        await update.message.reply_text("❌ Пользователь не зарегистрирован в системе.")
        context.user_data['waiting_for'] = None
        return

    context.user_data['trade_target'] = target_id
    context.user_data['trade_skins'] = []
    context.user_data['waiting_for'] = WAITING_FOR_TRADE_AMOUNT
    await update.message.reply_text("Введите сумму денег, которую хотите предложить (или 0 если только скины):")

async def process_trade_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    try:
        amount = int(update.message.text.strip())
        if amount < 0:
            await update.message.reply_text("❌ Сумма не может быть отрицательной!")
            return

        if users[user_id]["balance"] < amount:
            await update.message.reply_text("❌ Недостаточно средств для трейда!")
            return

        context.user_data['trade_amount'] = amount
        context.user_data['waiting_for'] = WAITING_FOR_TRADE_SKINS

        if users[user_id]["skins"]:
            skins_list = "\n".join(
                f"{i + 1}. {skin['name']} ({skin['rarity']}) - 💵 {skin['price']}$"
                for i, skin in enumerate(users[user_id]["skins"])
            )
            await update.message.reply_text(
                f"📋 Ваши скины:\n{skins_list}\n\n"
                "Введите номера скинов через пробел, которые хотите предложить (или 0 если только деньги):"
            )
        else:
            context.user_data['trade_skins'] = []
            await process_trade_skins(update, context)
    except ValueError:
        await update.message.reply_text("❌ Введите корректную сумму!")

async def process_trade_skins(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if text == "0":
        context.user_data['trade_skins'] = []
    else:
        try:
            skin_indices = [int(i) - 1 for i in text.split()]
            valid_skins = []

            for index in skin_indices:
                if 0 <= index < len(users[user_id]["skins"]):
                    valid_skins.append(users[user_id]["skins"][index])
                else:
                    await update.message.reply_text(f"❌ Скин с номером {index + 1} не найден!")
                    return

            context.user_data['trade_skins'] = valid_skins
        except ValueError:
            await update.message.reply_text("❌ Пожалуйста, введите номера скинов в виде чисел!")
            return

    target_id = context.user_data['trade_target']
    target_nick = nicknames.get(target_id, f"ID:{target_id}")
    amount = context.user_data.get('trade_amount', 0)
    skins = context.user_data.get('trade_skins', [])

    trade_id = f"{user_id}_{target_id}_{random.randint(1000, 9999)}"

    trades[trade_id] = {
        "from_user": user_id,
        "to_user": target_id,
        "amount": amount,
        "skins": skins,
        "status": "pending"
    }

    trade_text = f"🤝 Предложение трейда для {target_nick}:\n\n"
    trade_text += f"💸 Ваше предложение: {amount}$\n"

    if skins:
        trade_text += "🔫 Ваши скины:\n"
        trade_text += "\n".join(f"- {skin['name']} ({skin['rarity']})" for skin in skins)
    else:
        trade_text += "🔫 Скины не предложены\n"

    keyboard = [
        [InlineKeyboardButton("✅ Принять", callback_data=f"trade_accept_{trade_id}")],
        [InlineKeyboardButton("❌ Отклонить", callback_data=f"trade_decline_{trade_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        trade_text,
        reply_markup=reply_markup
    )

    try:
        from_nick = nicknames.get(user_id, f"ID:{user_id}")
        await context.bot.send_message(
            chat_id=target_id,
            text=f"🤝 Вам поступило предложение трейда от {from_nick}:\n\n{trade_text}",
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Ошибка при отправке уведомления о трейде: {e}")

    context.user_data['waiting_for'] = None

async def process_trade_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("trade_accept_"):
        trade_id = data.split("_")[2]
        await accept_trade(update, context, trade_id)
    elif data.startswith("trade_decline_"):
        trade_id = data.split("_")[2]
        await decline_trade(update, context, trade_id)

async def accept_trade(update: Update, context: ContextTypes.DEFAULT_TYPE, trade_id: str) -> None:
    if trade_id not in trades:
        await update.callback_query.edit_message_text("❌ Трейд не найден или уже обработан")
        return

    trade = trades[trade_id]
    from_user = trade["from_user"]
    to_user = trade["to_user"]
    amount = trade["amount"]
    skins = trade["skins"]

    if users[from_user]["balance"] < amount:
        await update.callback_query.edit_message_text("❌ У отправителя недостаточно средств")
        del trades[trade_id]
        return

    for skin in skins:
        if skin not in users[from_user]["skins"]:
            await update.callback_query.edit_message_text("❌ У отправителя больше нет некоторых скинов")
            del trades[trade_id]
            return

    try:
        users[from_user]["balance"] -= amount
        users[to_user]["balance"] += amount

        for skin in skins:
            users[from_user]["skins"].remove(skin)
            users[to_user]["skins"].append(skin)

        trades[trade_id]["status"] = "accepted"

        from_nick = nicknames.get(from_user, f"ID:{from_user}")
        to_nick = nicknames.get(to_user, f"ID:{to_user}")

        await context.bot.send_message(
            chat_id=from_user,
            text=f"✅ {to_nick} принял ваш трейд!\n"
                 f"💸 Переведено: {amount}$\n"
                 f"🔫 Передано скинов: {len(skins)}\n"
                 f"💰 Ваш баланс: {users[from_user]['balance']}$"
        )

        await update.callback_query.edit_message_text(
            f"✅ Вы приняли трейд от {from_nick}!\n"
            f"💸 Получено: {amount}$\n"
            f"🔫 Получено скинов: {len(skins)}\n"
            f"💰 Ваш баланс: {users[to_user]['balance']}$"
        )

    except Exception as e:
        print(f"Ошибка при выполнении трейда: {e}")
        await update.callback_query.edit_message_text("❌ Произошла ошибка при выполнении трейда")
    finally:
        if trade_id in trades:
            del trades[trade_id]

async def decline_trade(update: Update, context: ContextTypes.DEFAULT_TYPE, trade_id: str) -> None:
    if trade_id not in trades:
        await update.callback_query.edit_message_text("❌ Трейд не найден или уже обработан")
        return

    trade = trades[trade_id]
    from_user = trade["from_user"]
    to_user = update.callback_query.from_user.id

    trades[trade_id]["status"] = "declined"

    from_nick = nicknames.get(from_user, f"ID:{from_user}")
    to_nick = nicknames.get(to_user, f"ID:{to_user}")

    await context.bot.send_message(
        chat_id=from_user,
        text=f"❌ {to_nick} отклонил ваш трейд"
    )

    await update.callback_query.edit_message_text(
        f"❌ Вы отклонили трейд от {from_nick}"
    )

    del trades[trade_id]

async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in users:
        await update.message.reply_text("Сначала начните игру с помощью /start")
        return

    await update.message.reply_text(
        f"💰 Ваш баланс: {users[user_id]['balance']}$",
        reply_markup=main_keyboard
    )

async def show_cases(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in users:
        await update.message.reply_text("Сначала начните игру с помощью /start")
        return

    keyboard = [
        [InlineKeyboardButton(f"{case['name']} - {case['price']}$", callback_data=case_id)]
        for case_id, case in cases.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎲 Выберите кейс:", reply_markup=reply_markup)

async def case_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    case_id = query.data
    if case_id not in cases:
        await query.edit_message_text("Ошибка: кейс не найден.")
        return

    case = cases[case_id]
    if users[user_id]["balance"] >= case["price"]:
        users[user_id]["balance"] -= case["price"]
        skin = random.choice(case["skins"])
        users[user_id]["skins"].append(skin)
        await query.edit_message_text(
            f"🎉 Вы открыли {case['name']} и получили:\n"
            f"🔫 {skin['name']} ({skin['rarity']})\n"
            f"💵 Цена продажи: {skin['price']}$\n"
            f"💰 Ваш баланс: {users[user_id]['balance']}$"
        )
    else:
        await query.edit_message_text("❌ Недостаточно средств для открытия этого кейса.")

async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in users:
        await update.message.reply_text("Сначала начните игру с помощью /start")
        return

    if not users[user_id]["skins"]:
        await update.message.reply_text("🎒 Ваш инвентарь пуст.")
        return

    skins_list = "\n".join(
        f"{i + 1}. {skin['name']} ({skin['rarity']}) - 💵 {skin['price']}$"
        for i, skin in enumerate(users[user_id]["skins"])
    )

    await update.message.reply_text(
        f"🎒 Ваши скины:\n{skins_list}\n\n"
        "Чтобы продать скин, введите /sell [номер]",
        reply_markup=main_keyboard
    )

async def sell_skin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in users:
        await update.message.reply_text("Сначала начните игру с помощью /start")
        return

    if not context.args:
        await update.message.reply_text("Использование: /sell [номер скина]")
        return

    try:
        skin_index = int(context.args[0]) - 1
        if 0 <= skin_index < len(users[user_id]["skins"]):
            skin = users[user_id]["skins"].pop(skin_index)
            users[user_id]["balance"] += skin["price"]
            await update.message.reply_text(
                f"✅ Вы продали {skin['name']} за {skin['price']}$.\n"
                f"💰 Ваш баланс: {users[user_id]['balance']}$",
                reply_markup=main_keyboard
            )
        else:
            await update.message.reply_text("❌ Неверный номер скина.")
    except ValueError:
        await update.message.reply_text("❌ Номер скина должен быть числом.")

async def activate_promo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    promo_code = update.message.text.upper()

    if user_id not in users:
        await update.message.reply_text("Сначала начните игру с помощью /start")
        return

    if promo_code in used_promo_codes:
        await update.message.reply_text("❌ Этот промокод уже был использован!")
        return

    if promo_code in promo_codes:
        reward = promo_codes[promo_code]
        users[user_id]["balance"] += reward
        used_promo_codes.add(promo_code)
        await update.message.reply_text(
            f"🎉 Промокод активирован! Вы получили {reward}$\n"
            f"💰 Ваш баланс: {users[user_id]['balance']}$",
            reply_markup=main_keyboard
        )
    else:
        await update.message.reply_text("❌ Неверный промокод!")

async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not users:
        await update.message.reply_text("Пока нет игроков в таблице лидеров.")
        return

    sorted_users = sorted(users.items(), key=lambda x: x[1]["balance"], reverse=True)

    leaderboard_text = "🏆 Топ игроков:\n\n"
    for i, (user_id, data) in enumerate(sorted_users[:10], 1):
        nick = nicknames.get(user_id, f"ID:{user_id}")
        leaderboard_text += f"{i}. {nick} - 💰 {data['balance']}$\n"

    await update.message.reply_text(leaderboard_text, reply_markup=main_keyboard)

async def show_admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not users:
        await update.message.reply_text("Нет зарегистрированных игроков.")
        return

    total_players = len(users)
    total_skins = sum(len(user["skins"]) for user in users.values())
    total_balance = sum(user["balance"] for user in users.values())

    stats_text = (
        "📊 Статистика сервера:\n\n"
        f"👥 Игроков: {total_players}\n"
        f"🎒 Всего скинов: {total_skins}\n"
        f"💰 Общий баланс: {total_balance}$\n"
        f"🔨 Забанено: {len(banned_users)}\n"
        f"🤝 Активных трейдов: {len(trades)}"
    )

    await update.message.reply_text(stats_text, reply_markup=admin_keyboard)

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args and context.args[0] == ADMIN_PASSWORD:
        user_id = update.message.from_user.id
        if user_id not in users:
            users[user_id] = {"balance": float("inf"), "skins": []}
            nicknames[user_id] = f"Админ_{user_id % 1000:03d}"
            reverse_nicknames[nicknames[user_id].lower()] = user_id
        else:
            users[user_id]["balance"] = float("inf")

        await update.message.reply_text(
            "🔑 Режим администратора активирован!\n"
            "💰 У вас теперь бесконечные деньги.",
            reply_markup=admin_keyboard
        )
    else:
        await update.message.reply_text("❌ Неверный пароль!")

def main() -> None:
    application = Application.builder().token("8165670310:AAGeisjMnyf-BHwJxibiJvBHjoOXPOtK9jc").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("sell", sell_skin))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.add_handler(CallbackQueryHandler(case_selected))
    application.add_handler(CallbackQueryHandler(process_trade_confirmation, pattern="^trade_(accept|decline)_"))

    application.run_polling()

if __name__ == "__main__":
    main()
