from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random

users = {}
banned_users = set()
trades = {}
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
            {"name": "Нож | Адский пламень", "rarity": "Мифический", "price": 3000000},
            {"name": "Перчатки | Ледяной король", "rarity": "Мифический", "price": 3500000},
            {"name": "AWP | Вечный лед", "rarity": "Мифический", "price": 4000000},
            {"name": "Karambit | Огненный демон", "rarity": "Мифический", "price": 4500000},
            {"name": "M9 Bayonet | Лунный призрак", "rarity": "Мифический", "price": 5000000},
        ],
    },
}
leaderboard = {}
ADMIN_PASSWORD = "vadimka"

def is_banned(user_id: int) -> bool:
    return user_id in banned_users

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if is_banned(user_id):
        await update.message.reply_text("Вы забанены и не можете использовать бота.")
        return
    if user_id not in users:
        users[user_id] = {"balance": 1000, "skins": []}

    commands = (
        "/start - Начать игру\n"
        "/cases - Открыть кейсы\n"
        "/inventory - Показать инвентарь\n"
        "/sell [номер скина] - Продать скин\n"
        "/promo [ключ] - Активировать промокод\n"
        "/trade [user_id] [номер скина] - Предложить обмен\n"
        "/transfer [user_id] [сумма] - Перевести деньги\n"
        "/who - Показать список команд"
    )

    await update.message.reply_text(
        f"Ваш ID: {user_id}\nДобро пожаловать! Ваш баланс: {users[user_id]['balance']}$\n\n"
        f"Доступные команды:\n{commands}\n\n"
        "Используйте /cases чтобы открыть кейсы."
    )

async def who(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands = (
        "/start - Начать игру\n"
        "/cases - Открыть кейсы\n"
        "/inventory - Показать инвентарь\n"
        "/sell [номер скина] - Продать скин\n"
        "/promo [ключ] - Активировать промокод\n"
        "/trade [user_id] [номер скина] - Предложить обмен\n"
        "/transfer [user_id] [сумма] - Перевести деньги\n"
        "/who - Показать список команд"
    )
    await update.message.reply_text(f"Доступные команды:\n{commands}")

async def show_cases(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if is_banned(user_id):
        await update.message.reply_text("Вы забанены и не можете использовать бота.")
        return
    keyboard = [
        [InlineKeyboardButton(case["name"], callback_data=case_id)] for case_id, case in cases.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите кейс:", reply_markup=reply_markup)

async def case_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    if is_banned(user_id):
        await query.edit_message_text("Вы забанены и не можете использовать бота.")
        return

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
            f"Вы открыли {case['name']} и получили: {skin['name']} ({skin['rarity']})\nЦена продажи: {skin['price']}$\nВаш баланс: {users[user_id]['balance']}$"
        )
    else:
        await query.edit_message_text("Недостаточно средств для открытия этого кейса.")

async def inventory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if is_banned(user_id):
        await update.message.reply_text("Вы забанены и не можете использовать бота.")
        return
    if user_id in users:
        if users[user_id]["skins"]:
            skins = "\n".join(
                [f"{i+1}. {skin['name']} ({skin['rarity']}) - Цена продажи: {skin['price']}$"
                 for i, skin in enumerate(users[user_id]["skins"])]
            )
            await update.message.reply_text(
                f"Ваши скины (используйте номер для продажи через /sell [номер]):\n{skins}"
            )
        else:
            await update.message.reply_text("У вас нет скинов.")
    else:
        await update.message.reply_text("Вы еще не начали игру. Используйте /start.")

async def sell_skin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if is_banned(user_id):
        await update.message.reply_text("Вы забанены и не можете использовать бота.")
        return
    if user_id not in users:
        await update.message.reply_text("Вы еще не начали игру. Используйте /start.")
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
                f"Вы продали {skin['name']} за {skin['price']}$.\n"
                f"Ваш баланс: {users[user_id]['balance']}$"
            )
        else:
            await update.message.reply_text("Неверный номер скина.")
    except ValueError:
        await update.message.reply_text("Номер скина должен быть числом.")

async def trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if is_banned(user_id):
        await update.message.reply_text("Вы забанены и не можете использовать бота.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Использование: /trade [user_id] [номер скина]")
        return

    try:
        target_user_id = int(context.args[0])
        skin_index = int(context.args[1]) - 1

        if target_user_id not in users:
            await update.message.reply_text("Пользователь не найден.")
            return

        if skin_index < 0 or skin_index >= len(users[user_id]["skins"]):
            await update.message.reply_text("Неверный номер скина.")
            return

        trades[target_user_id] = {
            "from_user_id": user_id,
            "skin": users[user_id]["skins"][skin_index],
        }

        await update.message.reply_text(
            f"Вы предложили обмен пользователю {target_user_id}.\n"
            f"Скин: {users[user_id]['skins'][skin_index]['name']} ({users[user_id]['skins'][skin_index]['rarity']})"
        )

        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"Пользователь {user_id} предложил вам обмен:\n"
                 f"Скин: {users[user_id]['skins'][skin_index]['name']} ({users[user_id]['skins'][skin_index]['rarity']})\n"
                 f"Используйте /accept_trade чтобы принять или /decline_trade чтобы отклонить."
        )

    except ValueError:
        await update.message.reply_text("Некорректные данные. Убедитесь, что user_id и номер скина введены правильно.")

async def accept_trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in trades:
        await update.message.reply_text("У вас нет активных предложений обмена.")
        return

    trade_data = trades.pop(user_id)
    from_user_id = trade_data["from_user_id"]
    skin = trade_data["skin"]

    users[user_id]["skins"].append(skin)
    users[from_user_id]["skins"].remove(skin)

    await update.message.reply_text(f"Вы приняли обмен. Скин {skin['name']} теперь ваш.")
    await context.bot.send_message(
        chat_id=from_user_id,
        text=f"Пользователь {user_id} принял ваш обмен. Скин {skin['name']} передан."
    )

async def decline_trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id not in trades:
        await update.message.reply_text("У вас нет активных предложений обмена.")
        return

    trade_data = trades.pop(user_id)
    from_user_id = trade_data["from_user_id"]
    skin = trade_data["skin"]

    await update.message.reply_text(f"Вы отклонили обмен с пользователем {from_user_id}.")
    await context.bot.send_message(
        chat_id=from_user_id,
        text=f"Пользователь {user_id} отклонил ваш обмен."
    )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args and context.args[0] == ADMIN_PASSWORD:
        user_id = update.message.from_user.id
        users[user_id]["balance"] = float("inf")  # Бесконечные деньги
        await update.message.reply_text(
            "Режим администратора активирован. У вас теперь бесконечные деньги.\n"
            "Используйте /give_skin [user_id] [skin] чтобы выдать скин.\n"
            "Используйте /transfer [user_id] [сумма] чтобы перевести деньги.\n"
            "Используйте /ban [user_id] чтобы забанить пользователя.\n"
            "Используйте /unban [user_id] чтобы разбанить пользователя.\n"
            "Используйте /bankrupt [user_id] чтобы обанкротить пользователя.\n"
            "Используйте /leaderboard чтобы посмотреть таблицу игроков."
        )
    else:
        await update.message.reply_text("Неверный пароль.")

async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if context.args and context.args[0] == ADMIN_PASSWORD:
        if not users:
            await update.message.reply_text("Нет зарегистрированных игроков.")
            return

        leaderboard_text = "Таблица игроков:\n"
        for uid, data in users.items():
            leaderboard_text += (
                f"ID: {uid}\n"
                f"Баланс: {data['balance']}$\n"
                f"Количество скинов: {len(data['skins'])}\n"
                "----------------\n"
            )
        await update.message.reply_text(leaderboard_text)
    else:
        await update.message.reply_text("Неверный пароль.")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Использование: /ban [user_id]")
        return
    try:
        user_id = int(context.args[0])
        banned_users.add(user_id)
        await update.message.reply_text(f"Пользователь {user_id} забанен.")
    except ValueError:
        await update.message.reply_text("Некорректный user_id.")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Использование: /unban [user_id]")
        return
    try:
        user_id = int(context.args[0])
        banned_users.discard(user_id)
        await update.message.reply_text(f"Пользователь {user_id} разбанен.")
    except ValueError:
        await update.message.reply_text("Некорректный user_id.")

async def bankrupt_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Использование: /bankrupt [user_id]")
        return
    try:
        user_id = int(context.args[0])
        if user_id in users:
            users[user_id]["balance"] = 0
            users[user_id]["skins"] = []
            await update.message.reply_text(f"Пользователь {user_id} обанкрочен.")
        else:
            await update.message.reply_text("Пользователь не найден.")
    except ValueError:
        await update.message.reply_text("Некорректный user_id.")

async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if is_banned(user_id):
        await update.message.reply_text("Вы забанены и не можете использовать бота.")
        return
    if context.args and context.args[0] == "key":
        users[user_id]["balance"] += 10000
        await update.message.reply_text(f"Промокод активирован! Ваш баланс: {users[user_id]['balance']}$")
    elif context.args and context.args[0] == "STEPAN":
        users[user_id]["balance"] += 99999
        await update.message.reply_text(f"Промокод активирован! Ваш баланс: {users[user_id]['balance']}$")
    else:
        await update.message.reply_text("Неверный промокод.")

async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if is_banned(user_id):
        await update.message.reply_text("Вы забанены и не можете использовать бота.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Использование: /transfer [user_id] [сумма]")
        return

    try:
        target_user_id = int(context.args[0])
        amount = float(context.args[1])

        if target_user_id not in users:
            await update.message.reply_text("Пользователь не найден.")
            return

        if amount <= 0:
            await update.message.reply_text("Сумма должна быть больше нуля.")
            return

        if users[user_id]["balance"] < amount:
            await update.message.reply_text("Недостаточно средств для перевода.")
            return

        users[user_id]["balance"] -= amount
        users[target_user_id]["balance"] += amount

        await update.message.reply_text(
            f"Вы перевели {amount}$ пользователю {target_user_id}.\n"
            f"Ваш новый баланс: {users[user_id]['balance']}$"
        )

        await context.bot.send_message(
            chat_id=target_user_id,
            text=f"Пользователь {user_id} перевел вам {amount}$.\n"
                    f"Ваш новый баланс: {users[target_user_id]['balance']}$"
        )

    except ValueError:
        await update.message.reply_text("Некорректные данные. Убедитесь, что user_id и сумма введены правильно.")

def main() -> None:
    application = Application.builder().token("7771249533:AAG3hA9pTgbeuCIkHqTdLYu8WSElIu2EIm8").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("who", who))
    application.add_handler(CommandHandler("cases", show_cases))
    application.add_handler(CallbackQueryHandler(case_selected))
    application.add_handler(CommandHandler("inventory", inventory))
    application.add_handler(CommandHandler("sell", sell_skin))
    application.add_handler(CommandHandler("admin", admin))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("bankrupt", bankrupt_user))
    application.add_handler(CommandHandler("promo", promo))
    application.add_handler(CommandHandler("trade", trade))
    application.add_handler(CommandHandler("accept_trade", accept_trade))
    application.add_handler(CommandHandler("decline_trade", decline_trade))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))
    application.add_handler(CommandHandler("transfer", transfer))  # Добавлена команда /transfer

    application.run_polling()

if __name__ == "__main__":
    main()
