import telebot
import random
import dw
import random
import math
from threading import Thread
import sqlite3 as sq
from time import sleep
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import pickaxe as pic
from datetime import time, date, datetime
import text_work as tw

# Один кусок мяса восстанавливает 10 единиц голода


def initialize_meat_grid():
    meat_grid = [[random.randint(1, 10) for _ in range(3)] for _ in range(3)]
    return meat_grid


def random_meat():
    a = random.randint(1, 100)
    if 1 <= a <= 10:
        return 0
    if 10 < a <= 30:
        return random.randint(1, 3)
    if 30 < a <= 70:
        return random.randint(3, 7)
    if 70 < a <= 95:
        return random.randint(6, 15)
    if 95 < a <= 100:
        return random.randint(15, 20)


with sq.connect("gnomes.db") as con:
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users_gnomes (
            user_id INTEGER,
            gnome_name TEXT,
            hunger_level INTEGER,
            meat INTEGER,
            thirst_level INTEGER,
            beer INTEGER, 
            tickets_to_expedition INTEGER,
            gold INTEGER,
            pickaxe_level INTEGER,
            pickaxe_durability INTEGER,
            pickaxe_gold_per_strike INTEGER, 
            new_pickaxe_level INTEGER,
            shop_meat INTEGER,
            shop_beer INTEGER,
            birth_date TEXT,
            is_dead INTEGER
            
    )
                """)


bot = telebot.TeleBot("6370080307:AAEm_cm-4O06Ond8OzUA0ht4Koo3OOljsZY")


def create_gnome(user_id, gnome_name):
    with sq.connect("gnomes.db") as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM users_gnomes WHERE user_id=? AND is_dead!=1", (user_id,))
        num_gnomes = cursor.fetchone()[0]

        if num_gnomes > 0:
            return None
        current_date = str(datetime.now().date())
        gnome = dw.Dwarf(gnome_name)
        gnome.feed(100)
        gnome.drink(100)
        cursor.execute("""INSERT INTO users_gnomes (
                       user_id, 
                       gnome_name, 
                       hunger_level, 
                       meat, 
                       thirst_level, 
                       beer,  
                       tickets_to_expedition,
                       gold,
                       pickaxe_level,
                       pickaxe_durability,
                       pickaxe_gold_per_strike,
                       new_pickaxe_level,
                       shop_meat,
                       shop_beer,
                       birth_date,
                       is_dead) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?,?)""",
                       (user_id, gnome_name, 100, 10, 100, 10, 3, 0, 0, 0, 0, 0, 5, 5, current_date, 0))

    return gnome


def random_pickaxe():
    a = random.randint(1000, 10300)
    return (a//1000)


def repair_pickaxe(level):
    return level*2


def get_gnome(user_id):
    with sq.connect("gnomes.db") as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT gnome_name, hunger_level, thirst_level FROM users_gnomes WHERE user_id=? AND is_dead!=1", (user_id,))
        row = cursor.fetchone()
        if row:
            gnome_name, hunger_level, thirst_level = row[:3]
            gnome = dw.Dwarf(gnome_name)
            gnome.feed(hunger_level)
            gnome.drink(thirst_level)

            return gnome
        else:
            return None


def get_pickaxe(user_id):
    with sq.connect("gnomes.db") as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT pickaxe_level, pickaxe_durability, pickaxe_gold_per_strike FROM users_gnomes WHERE user_id=? AND is_dead!=1", (user_id,))
        row = cursor.fetchone()
        if row:
            pickaxe_level, pickaxe_durability, pickaxe_gold_per_strike = row[:3]
            tool = pic.Pickaxe(pickaxe_level, pickaxe_durability)
            return tool
        else:
            return None


def show_gold(user_id):
    with sq.connect("gnomes.db") as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT gold FROM users_gnomes WHERE user_id = ? AND is_dead!=1", (user_id, ))
        row = cursor.fetchone()
        if row:
            return row[0]


def get_all_gnomes_names(user_id):
    with sq.connect("gnomes.db") as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT gnome_name, birth_date, hunger_level, thirst_level, is_dead FROM users_gnomes WHERE user_id=?", (user_id,))
        rows = cursor.fetchall()
        return rows


def chat_show_my_gnomes(message, user_id):
    rows = get_all_gnomes_names(user_id)
    response = "Ваши гномы: \n"
    if rows:
        for row in rows:
            date_from_string = datetime.strptime(row[1], "%Y-%m-%d").date()
            current_date = datetime.now().date()
            date_difference = current_date - date_from_string
            if row[-1]:
                response += f"{row[0]} прожил с вами {date_difference.days}.\n"
            else:
                response += f"{row[0]} живет с вами {date_difference.days} дней.\nУровень насыщенения: " + \
                    "🍖" * \
                    dw.level_of_hunger(
                        row[2])+"\nУровень жажды: " + "🍺"*dw.level_of_thirst(row[3])
    else:
        response = "У вас еще нет гномов. Используйте команду /start, чтобы создать своего первого гнома."
    bot.reply_to(message, response)


def decrease_hunger_level(user_id):
    gnome = get_gnome(user_id)
    if gnome:
        with sq.connect("gnomes.db") as con:
            gnome.starve(10)
            hunger = gnome.get_hunger_level()
            cursor = con.cursor()
            cursor.execute(
                "UPDATE users_gnomes SET hunger_level=? WHERE user_id=? AND is_dead!=1", (hunger, user_id))
            if hunger < 30:
                bot.send_message(
                    user_id, f"{gnome.name} адски {tw.detect_gender(gnome.name, 'голоден', 'голодна')}!")
            elif hunger == 0:
                cursor.execute(
                    "UPDATE users_gnomes SET is_dead=? WHERE user_id=?", (1, user_id))
                bot.send_message(
                    user_id, f"К сожалению, {gnome.name} не {tw.detect_gender(gnome.name, 'смог', 'смогла')} вынести такой голодовки и ушел в лес.")


def decrease_thirst_level(user_id):
    gnome = get_gnome(user_id)
    if gnome:
        with sq.connect("gnomes.db") as con:
            gnome.crave(10)
            thirst = gnome.get_thirst_level()

            cursor = con.cursor()
            cursor.execute(
                "UPDATE users_gnomes SET thirst_level=? WHERE user_id=? AND is_dead!=1", (thirst, user_id))
            if thirst < 30:
                bot.send_message(
                    user_id, f"{gnome.name} уже забывает вкус пива!")
            elif thirst == 0:
                cursor.execute(
                    "UPDATE users_gnomes SET is_dead=? WHERE user_id=?", (1, user_id))
                bot.send_message(
                    user_id, f"К сожалению, {gnome.name} не {tw.detect_gender(gnome.name, 'смог', 'смогла')} вынести такой грустной жизни и ушел в лес.")


def increase_tickets(user_id):
    gnome = get_gnome(user_id)
    if gnome:
        with sq.connect("gnomes.db") as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT tickets_to_expedition FROM users_gnomes WHERE user_id=? AND is_dead!=1", (user_id,))
            row = cursor.fetchone()
            amount = min(3, row[0]+1)
            cursor.execute(
                "UPDATE users_gnomes SET tickets_to_expedition=? WHERE user_id=? AND is_dead!=1", (amount, user_id))
            if amount == 3:
                bot.send_message(
                    user_id, f"{gnome.name} вновь {tw.detect_gender(gnome.name, 'полон', 'полна')} сил для вылазок!")


def increase_shop(user_id):
    gnome = get_gnome(user_id)
    if gnome:
        with sq.connect("gnomes.db") as con:
            cursor = con.cursor()
            amount = 5
            cursor.execute(
                "UPDATE users_gnomes SET meat=?, beer = ? WHERE user_id=? AND is_dead!=1", (amount, amount, user_id))
            bot.send_message(
                user_id, f"Магазин восполнил свои запасы!")


def buy_meat(user_id):
    gnome = get_gnome(user_id)
    if gnome:
        with sq.connect("gnomes.db") as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT gold, meat FROM users_gnomes WHERE user_id = ? AND is_dead!=1", (user_id,))
            row = cursor.fetchone()
            if row:
                amount_of_gold, amount_of_meat = row
                if amount_of_gold >= 5:
                    amount_of_gold -= 5
                    amount_of_meat += 1
                    cursor.execute("UPDATE users_gnomes SET gold=?, meat=? WHERE user_id=? AND is_dead!=1", (
                        amount_of_gold, amount_of_meat, user_id,))
                    return True
                else:
                    return False


def buy_beer(user_id):
    gnome = get_gnome(user_id)
    if gnome:
        with sq.connect("gnomes.db") as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT gold, beer FROM users_gnomes WHERE user_id = ? AND is_dead!=1", (user_id,))
            row = cursor.fetchone()
            if row:
                amount_of_gold, amount_of_beer = row
                if amount_of_gold >= 5:
                    amount_of_gold -= 5
                    amount_of_beer += 1
                    cursor.execute("UPDATE users_gnomes SET gold=?, beer=? WHERE user_id=? AND is_dead!=1", (
                        amount_of_gold, amount_of_beer, user_id,))
                    return True
                else:
                    return False


def buy_pickaxe_upgrade(user_id):
    gnome = get_gnome(user_id)
    if gnome:
        with sq.connect("gnomes.db") as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT gold, pickaxe_level FROM users_gnomes WHERE user_id = ? AND is_dead!=1", (user_id,))
            row = cursor.fetchone()
            if row:
                amount_of_gold, pickaxe_level = row
                if amount_of_gold >= 100:
                    amount_of_gold -= 100
                    pickaxe_level += 1
                    if pickaxe_level<11:
                        tool = pic.Pickaxe(pickaxe_level, 500)
                        tool.durability

                        cursor.execute("""UPDATE users_gnomes 
                                    SET gold=?, 
                                    pickaxe_level=?, 
                                    pickaxe_durability=?
                                    WHERE user_id=? AND is_dead!=1""", (
                            amount_of_gold, tool.level, tool.durability, user_id,))
                        return 1
                    else:
                        return -1
                else:
                    return 0


def mine_gold_task(user_id):
    tool = get_pickaxe(user_id)
    if tool:
        with sq.connect("gnomes.db") as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT pickaxe_level, pickaxe_durability FROM users_gnomes WHERE user_id=? AND is_dead!=1", (user_id,))
            row = cursor.fetchone()
            tool = pic.Pickaxe(row[0], row[1])
            amount_of_gold = show_gold(user_id)
            print(tool.durability, row[1])
            cursor.execute(
                """UPDATE users_gnomes 
                SET gold=?, 
                pickaxe_durability=? 
                WHERE user_id=? AND is_dead!=1""", (amount_of_gold + tool.mine_gold(), tool.durability, user_id))
            print(tool.durability, row[1])


def show_meat(user_id):
    with sq.connect("gnomes.db") as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT meat FROM users_gnomes WHERE user_id=? AND is_dead!=1", (user_id,))
        row = cursor.fetchone()
        return row[0]


def show_beer(user_id):
    with sq.connect("gnomes.db") as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT beer FROM users_gnomes WHERE user_id=? AND is_dead!=1", (user_id,))
        row = cursor.fetchone()
        return row[0]


def count_piece_of_meat_to_feed(hunger):
    if hunger >= 85:
        return 0
    necessity = int(math.ceil((100 - hunger)/10))
    return necessity


def count_beer_to_drink(hunger):
    if hunger >= 65:
        return 0
    necessity = int(math.ceil((100 - hunger)/10))
    return necessity


def increase_hunger_level(user_id):
    gnome = get_gnome(user_id)
    if gnome:
        with sq.connect("gnomes.db") as con:
            hunger = gnome.get_hunger_level()
            meat = show_meat(user_id)
            necessity = count_piece_of_meat_to_feed(hunger)
            if meat == 0:
                return None
            if meat >= necessity:
                gnome.feed(necessity*10)
                hunger = gnome.get_hunger_level()

                meat -= necessity
                cursor = con.cursor()
                cursor.execute(
                    "UPDATE users_gnomes SET hunger_level=? WHERE user_id=?", (hunger, user_id))
                cursor.execute(
                    "UPDATE users_gnomes SET meat=? WHERE user_id=?", (meat, user_id))
                return 1
            else:
                gnome.feed(meat*10)
                meat = 0
                cursor = con.cursor()
                cursor.execute(
                    "UPDATE users_gnomes SET hunger_level=? WHERE user_id=?", (hunger, user_id))
                cursor.execute(
                    "UPDATE users_gnomes SET meat=? WHERE user_id=?", (meat, user_id))
                return 1


def increase_thirst_level(user_id):
    gnome = get_gnome(user_id)
    if gnome:
        with sq.connect("gnomes.db") as con:
            thirst = gnome.get_thirst_level()
            beer = show_beer(user_id)
            necessity = count_beer_to_drink(thirst)
            if beer == 0:
                return None
            if beer >= necessity:
                gnome.drink(necessity*10)
                thirst = gnome.get_thirst_level()

                beer -= necessity
                cursor = con.cursor()
                cursor.execute(
                    "UPDATE users_gnomes SET thirst_level=? WHERE user_id=?", (thirst, user_id))
                cursor.execute(
                    "UPDATE users_gnomes SET beer=? WHERE user_id=?", (beer, user_id))
                return 1
            else:
                gnome.drink(beer*10)
                beer = 0
                thirst = gnome.get_thirst_level()
                cursor = con.cursor()
                cursor.execute(
                    "UPDATE users_gnomes SET thirst_level=? WHERE user_id=?", (thirst, user_id))
                cursor.execute(
                    "UPDATE users_gnomes SET beer=? WHERE user_id=?", (beer, user_id))
                return 1


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    markup_inline = InlineKeyboardMarkup()
    markup_inline.row_width = 2
    markup_inline.add(
        InlineKeyboardButton("Создать гнома", callback_data="create_gnome"),
        InlineKeyboardButton("Мои гномы", callback_data="my_gnomes"),
        InlineKeyboardButton("Покормить гнома", callback_data="feed_gnome"),
        InlineKeyboardButton("Налить гному пива", callback_data="drink_gnome"),
        InlineKeyboardButton("Проверить запасы", callback_data="show_meat"),
        InlineKeyboardButton("Отправится на вылазку",
                             callback_data="go_on_expedition"),
        InlineKeyboardButton("Кирка",
                             callback_data="pickaxe_info"),
        InlineKeyboardButton("Магазин",
                             callback_data="shop")
    )
    markup_reply = ReplyKeyboardMarkup(resize_keyboard=True)
    reply_button = KeyboardButton("Меню")
    markup_reply.add(reply_button)

    bot.send_message(user_id, "Выберите действие:", reply_markup=markup_inline)
    bot.send_message(
        user_id, "Используйте кнопку 'Меню', чтобы открыть основное меню.", reply_markup=markup_reply)


@bot.message_handler(func=lambda message: message.text == "Меню")
def handle_reply(message):
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Создать гнома", callback_data="create_gnome"),
        InlineKeyboardButton("Мои гномы", callback_data="my_gnomes"),
        InlineKeyboardButton("Покормить гнома", callback_data="feed_gnome"),
        InlineKeyboardButton("Налить гному пива", callback_data="drink_gnome"),
        InlineKeyboardButton("Проверить запасы", callback_data="show_meat"),
        InlineKeyboardButton("Отправится на вылазку",
                             callback_data="go_on_expedition"),
        InlineKeyboardButton("Кирка",
                             callback_data="pickaxe_info"),
        InlineKeyboardButton("Магазин",
                             callback_data="shop")
    )
    bot.send_message(user_id, "Основное меню:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    data = call.data
    if data == "create_gnome":
        handle_create_gnome(call.message, user_id)
        bot.answer_callback_query(call.id)

    elif data == "my_gnomes":
        chat_show_my_gnomes(call.message, user_id)

    elif data == "hunger_level":
        chat_get_hunger_level(call.message, user_id)

    elif data == "feed_gnome":
        handle_feed_gnome(call.message, user_id)

    elif data == "show_meat":
        handle_show_meat(call.message, user_id)

    elif data == "drink_gnome":
        handle_drink_gnome(call.message, user_id)

    elif data == "go_on_expedition":
        handle_go_on_expedition(call.message, user_id)
    elif data == "pickaxe_info":
        pickaxe_info(call.message, user_id)

    elif data == "shop":
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(
            InlineKeyboardButton(
                "Купить 🍖 (5💰)", callback_data="buy_meat_in_shop"),
            InlineKeyboardButton(
                "Купить 🍺 (5💰)", callback_data="buy_beer_in_shop"),
            InlineKeyboardButton(
                "Улучшить кирку (100💰)", callback_data="upgrade_pickaxe_in_shop"),
        )
        bot.send_message(
            user_id, f"Добро пожаловать в магазин! Что бы вы хотели?", reply_markup=markup)
    elif data.startswith("cell_"):
        gnome = get_gnome(user_id)
        if gnome:
            _, row, col = data.split('_')
            with sq.connect("gnomes.db") as con:
                cursor = con.cursor()
                cursor.execute(
                    "SELECT tickets_to_expedition FROM users_gnomes WHERE user_id=? AND is_dead!=1", (user_id,))
                row = cursor.fetchone()
                if row[0] != 0:
                    a = random.randint(1, 125)
                    if a >= 58 and a <= 116:
                        output = random_meat()
                        cursor.execute("UPDATE users_gnomes SET meat=? WHERE user_id=? AND is_dead!=1",
                                       (output+show_meat(user_id), user_id))
                        cursor.execute("UPDATE users_gnomes SET tickets_to_expedition=? WHERE user_id=? AND is_dead!=1",
                                       (row[0]-1, user_id))
                        if output != 0:
                            bot.answer_callback_query(
                                call.id, text=f"Вы нашли {output} 🍖!")
                        elif output == 0:
                            bot.answer_callback_query(
                                call.id, text=f"К сожалению вы ничего не нашли.")
                    elif a < 58:
                        output = random_meat()
                        cursor.execute("UPDATE users_gnomes SET beer=? WHERE user_id=? AND is_dead!=1",
                                       (output+show_beer(user_id), user_id))
                        cursor.execute("UPDATE users_gnomes SET tickets_to_expedition=? WHERE user_id=? AND is_dead!=1",
                                       (row[0]-1, user_id))
                        if output != 0:
                            bot.answer_callback_query(
                                call.id, text=f"Вы нашли {output} 🍺!")
                        elif output == 0:
                            bot.answer_callback_query(
                                call.id, text=f"К сожалению вы ничего не нашли.")
                    else:
                        level = random_pickaxe()
                        tool = pic.Pickaxe(level, 500)
                        cursor.execute(
                            "SELECT pickaxe_level FROM users_gnomes WHERE user_id=? AND is_dead!=1", (user_id,))
                        current_pickaxe_level = cursor.fetchone()[0]
                        if current_pickaxe_level == 0:
                            cursor.execute("""UPDATE users_gnomes SET 
                                    pickaxe_level=?,
                                    pickaxe_durability=?,
                                    pickaxe_gold_per_strike=? WHERE user_id = ? and is_dead!=1""",
                                           (tool.level, tool.durability, tool.gold_per_strike, user_id,))
                            bot.answer_callback_query(
                                call.id, text=f"""Вы нашли ⛏ {level} уровня! """)
                        else:
                            if level > current_pickaxe_level:
                                cursor.execute("""UPDATE users_gnomes SET 
                                    new_pickaxe_level=? WHERE user_id = ? and is_dead!=1""",
                                               (level, user_id,))

                                markup = InlineKeyboardMarkup()
                                markup.row_width = 2
                                markup.add(
                                    InlineKeyboardButton(
                                        "Обновить ⛏", callback_data="update_pickaxe"),
                                    InlineKeyboardButton(
                                        "Не обновлять ⛏", callback_data="keep_pickaxe"),
                                )
                                bot.send_message(
                                    user_id, f"Вы нашли ⛏ {level} уровня! Хотите обновить ⛏?", reply_markup=markup)

                            else:
                                if current_pickaxe_level < level:
                                    bot.answer_callback_query(
                                        call.id, text=f"""Вы нашли ⛏ {level} уровня! Так как текущая кирка лучше, {gnome.name} {tw.detect_gender(gnome.name, 'использовал', 'использовала')}  ⛏ для ремонта своей.""")
                                if current_pickaxe_level == level:
                                    bot.answer_callback_query(
                                        call.id, text=f"""Вы нашли ⛏ {level} уровня! Так как текущая кирка такая же, {gnome.name} {tw.detect_gender(gnome.name, 'использовал', 'использовала')} ⛏ для ремонта своей.""")
                                cursor.execute("""UPDATE users_gnomes SET 
                                pickaxe_durability=? WHERE user_id = ? and is_dead!=1""",
                                               (tool.durability + repair_pickaxe(level), user_id,))

                if row[0] == 0:
                    bot.answer_callback_query(
                        call.id, text=f"{gnome.name} слишком {tw.detect_gender(gnome.name, 'устал', 'устала')}, чтобы куда то идти!")

    elif data == "update_pickaxe":
        with sq.connect("gnomes.db") as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT new_pickaxe_level FROM users_gnomes WHERE user_id=? AND is_dead!=1", (user_id,))
            new_pickaxe_level = cursor.fetchone()[0]
            cursor.execute("""UPDATE users_gnomes SET 
                           pickaxe_level=? WHERE user_id = ? and is_dead!=1""",
                           (new_pickaxe_level, user_id,))
            bot.answer_callback_query(
                call.id, text=f"⛏Кирка⛏ успешно обновлена до {new_pickaxe_level} уровня!")

    elif data == "keep_pickaxe":
        bot.answer_callback_query(
            call.id, text="Вы решили не обновлять ⛏кирку⛏.")
    elif data == "buy_meat_in_shop":
        if buy_meat(user_id):
            bot.answer_callback_query(
                call.id, text="Вы купили 🍖!")
        else:
            bot.answer_callback_query(
                call.id, text="К сожалению, у вас не хватает средств.")

    elif data == "buy_beer_in_shop":
        if buy_beer(user_id):
            bot.answer_callback_query(
                call.id, text="Вы купили 🍺!")
        else:
            bot.answer_callback_query(
                call.id, text="К сожалению, у вас не хватает средств.")

    elif data == "upgrade_pickaxe_in_shop":
        res = buy_pickaxe_upgrade(user_id)
        if res == 1:
            bot.answer_callback_query(
                call.id, text="Вы улучшили свою ⛏ до следующего уровня!")
        elif res == 0:
            bot.answer_callback_query(
                call.id, text="К сожалению, у вас не хватает средств.")
        elif res == -1:
            bot.answer_callback_query(
                call.id, text="Ваша кирка уже максимального уровня!")

def handle_go_on_expedition(message, user_id):
    gnome = get_gnome(user_id)
    if gnome:
        markup = InlineKeyboardMarkup()
        for row in range(3):
            row_buttons = []
            for col in range(3):
                row_buttons.append(InlineKeyboardButton(
                    "✅", callback_data=f"cell_{row}_{col}"))
            markup.add(*row_buttons)
        bot.send_message(
            user_id, "Выберите клетку для изучения:", reply_markup=markup)
    else:
        bot.reply_to(
            message, "У вас еще нет гнома. Используйте команду /start, чтобы создать его.")


def handle_my_gnomes(message, user_id):
    chat_show_my_gnomes(message, user_id)


def handle_show_meat(message, user_id):
    gnome = get_gnome(user_id)
    if gnome:
        amount_of_meat = show_meat(user_id)
        amount_of_beer = show_beer(user_id)
        amount_of_gold = show_gold(user_id)
        bot.send_message(
            user_id, f"В ваших запасах есть:\n{amount_of_meat}🍖 и {amount_of_beer}🍺\nКазна содержит {amount_of_gold}💰!")
    else:
        bot.reply_to(
            message, "У вас еще нет гнома. Используйте команду /start, чтобы создать его.")


def handle_create_gnome(message, user_id):
    gnome = get_gnome(user_id)
    if gnome:
        bot.send_message(
            user_id, "У вас уже есть гном. Вы не можете создать больше.")
    else:
        bot.reply_to(message, "Введите имя вашего гнома:")
        bot.register_next_step_handler(
            message, lambda m: create_gnome_and_notify(user_id, m.text))


def create_gnome_and_notify(user_id, gnome_name):
    gnome = create_gnome(user_id, gnome_name)
    if gnome:
        bot.send_message(
            user_id, f"{gnome_name} {tw.detect_gender(gnome.name, 'выбрался', 'выбралась')} из темной пещеры!")
    else:
        bot.send_message(
            user_id, "Не удалось создать гнома. Попробуйте еще раз или обратитесь за помощью.")


def chat_get_hunger_level(message, user_id):

    gnome = get_gnome(user_id)
    if gnome:
        hunger = gnome.get_hunger_level()
        thirst = gnome.get_thirst_level()

        bot.reply_to(
            message, f"Ваш гном {dw.level_of_hunger(hunger)} и {dw.level_of_thirst(thirst)}")

    else:
        bot.reply_to(
            message, "У вас еще нет гнома. Используйте команду /start, чтобы создать его.")


def handle_feed_gnome(message, user_id):
    gnome = get_gnome(user_id)
    if gnome:
        if increase_hunger_level(user_id):
            gnome = get_gnome(user_id)
            if show_meat(user_id) != 0:
                bot.reply_to(
                    message, f"Вы покормили {tw.inflect_to_accusative(gnome.name)}!\nУровень насыщенения: " + dw.level_of_hunger(gnome.get_hunger_level())*"🍖")
            else:
                bot.reply_to(
                    message, f"Вы покормили {tw.inflect_to_accusative(gnome.name) }!\nУровень насыщенения: " + dw.level_of_hunger(gnome.get_hunger_level())*"🍖"+"\nЗапасы мяса иссякли!")
        else:
            bot.reply_to(
                message, f"Запасы мяса иссякли - скорее отправляйтесь на вылазку!")
    else:
        bot.reply_to(
            message, "У вас еще нет гнома. Используйте команду /start, чтобы создать своего первого гнома.")


def pickaxe_info(message, user_id):
    gnome = get_gnome(user_id)
    pickaxe = get_pickaxe(user_id)
    if gnome:
        if pickaxe.level == 0:
            bot.send_message(
                user_id, f"{gnome.name} {tw.detect_gender(gnome.name, 'потерял', 'потеряла')} свою старую кирку, попробуйте найти новую во время вылазки!")
        elif pickaxe.level != 0 and pickaxe.durability == 0:
            bot.send_message(
                user_id, f"Кирка {tw.inflect_to_dative(gnome.name)} превратилась в пыль от времени, попробуйте найти новую во время вылазки!")
        else:
            bot.send_message(
                user_id, f"{gnome.name} является {tw.detect_gender(gnome.name, 'счастливым', 'счатливой')} {tw.detect_gender(gnome.name, 'обладателем', 'обладательницей')} кирки {pickaxe.level} уровня. Прочность кирки составляет {pickaxe.durability//5}%.")
    else:
        bot.reply_to(
            message, "У вас еще нет гнома. Используйте команду /start, чтобы создать своего первого гнома.")


def handle_drink_gnome(message, user_id):
    gnome = get_gnome(user_id)
    if gnome:
        if increase_thirst_level(user_id):
            gnome = get_gnome(user_id)
            if show_beer(user_id) != 0:
                bot.reply_to(
                    message, f"Вы угостили {tw.inflect_to_accusative(gnome.name)} пивом!\nУровень жажды: " + "🍺"*dw.level_of_thirst(gnome.get_thirst_level()))
            else:
                bot.reply_to(
                    message, f"Вы угостили {tw.inflect_to_accusative(gnome.name)} пивом!\nУровень жажды: " + "🍺"*dw.level_of_thirst(gnome.get_thirst_level())+"\nЗапасы пива иссякли!")
        else:
            bot.reply_to(
                message, f"Запасы пива иссякли - скорее отправляйтесь на поиски!")
    else:
        bot.reply_to(
            message, "У вас еще нет гнома. Используйте команду /start, чтобы создать своего первого гнома.")


def schedule_checker_hunger():
    while True:
        with sq.connect("gnomes.db") as con:
            sleep(4000)
            cursor = con.cursor()
            cursor.execute("SELECT user_id FROM users_gnomes")
            user_ids = cursor.fetchall()
            for user_id in user_ids:
                decrease_hunger_level(user_id[0])


def schedule_checker_thirst():
    while True:
        with sq.connect("gnomes.db") as con:
            sleep(4500)
            cursor = con.cursor()
            cursor.execute("SELECT user_id FROM users_gnomes WHERE is_dead!=1")
            user_ids = cursor.fetchall()
            for user_id in user_ids:
                decrease_thirst_level(user_id[0])


def schedule_checker_tickets():
    while True:
        with sq.connect("gnomes.db") as con:
            sleep(60*60)
            cursor = con.cursor()
            cursor.execute("SELECT user_id FROM users_gnomes WHERE is_dead!=1")
            user_ids = cursor.fetchall()
            for user_id in user_ids:
                increase_tickets(user_id[0])


def schedule_checker_mining():
    while True:
        with sq.connect("gnomes.db") as con:
            sleep(60*60)
            cursor = con.cursor()
            cursor.execute(
                "SELECT user_id FROM users_gnomes WHERE pickaxe_level!=0 AND pickaxe_durability!=0 AND is_dead!=1")
            user_ids = cursor.fetchall()
            for user_id in user_ids:
                mine_gold_task(user_id[0])


def schedule_checker_shop():
    while True:
        with sq.connect("gnomes.db") as con:
            sleep(24*60*60)
            cursor = con.cursor()
            cursor.execute("SELECT user_id FROM users_gnomes WHERE is_dead!=1")
            user_ids = cursor.fetchall()
            for user_id in user_ids:
                increase_shop(user_id[0])


def main():
    initialize_meat_grid()
    Thread(target=schedule_checker_hunger).start()
    Thread(target=schedule_checker_thirst).start()
    Thread(target=schedule_checker_tickets).start()
    Thread(target=schedule_checker_mining).start()
    Thread(target=schedule_checker_shop).start()
    bot.infinity_polling()


if __name__ == '__main__':
    main()
