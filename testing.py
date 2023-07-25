import telebot
import schedule
import dwtesting
import random
import math
from threading import Thread
import sqlite3 as sq
from time import sleep
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# Один кусок мяс восстанавливает 10 единиц голода
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

        gnome = dwtesting.Dwarf(gnome_name)
        gnome.feed(100)
        gnome.drink(100)
        cursor.execute("INSERT INTO users_gnomes (user_id, gnome_name, hunger_level, meat, thirst_level, beer,  tickets_to_expedition, is_dead) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (user_id, gnome_name, 100, 10, 100, 10, 3, 0))
    return gnome


def get_gnome(user_id):
    with sq.connect("gnomes.db") as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT gnome_name, hunger_level, thirst_level FROM users_gnomes WHERE user_id=? AND is_dead!=1", (user_id,))
        row = cursor.fetchone()
        if row:
            gnome_name, hunger_level, thirst_level = row[:3]
            gnome = dwtesting.Dwarf(gnome_name)
            gnome.feed(hunger_level)
            gnome.drink(thirst_level)

            return gnome
        else:
            return None


def get_all_gnomes_names(user_id):
    with sq.connect("gnomes.db") as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT gnome_name FROM users_gnomes WHERE user_id=?", (user_id,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]


def chat_show_my_gnomes(message, user_id):
    gnome_names = get_all_gnomes_names(user_id)
    if gnome_names:
        response = "Ваши гномы:\n" + "\n".join(gnome_names)
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
                    user_id, f"{gnome.name} адски голоден!")
            elif hunger == 0:
                cursor.execute(
                    "UPDATE users_gnomes SET is_dead=? WHERE user_id=?", (1, user_id))
                bot.send_message(
                    user_id, f"К сожалению, {gnome.name} не смог вынести такой голодовки и ушел в лес.")


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
                    user_id, f"К сожалению, {gnome.name} не смог вынести такой грустной жизни и ушел в лес.")


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
                    user_id, f"{gnome.name} вновь полон сил для охоты!")


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
        InlineKeyboardButton("Посмотреть уровень голода и жажды",
                             callback_data="hunger_level"),
        InlineKeyboardButton("Покормить гнома", callback_data="feed_gnome"),
        InlineKeyboardButton("Налить гному пива", callback_data="drink_gnome"),
        InlineKeyboardButton("Проверить запасы", callback_data="show_meat"),
        InlineKeyboardButton("Отправится на охоту",
                             callback_data="go_on_expedition")
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
        InlineKeyboardButton("Посмотреть уровень голода и жажды",
                             callback_data="hunger_level"),
        InlineKeyboardButton("Покормить гнома", callback_data="feed_gnome"),
        InlineKeyboardButton("Налить гному пива", callback_data="drink_gnome"),
        InlineKeyboardButton("Проверить запасы", callback_data="show_meat"),
        InlineKeyboardButton("Отправится на охоту",
                             callback_data="go_on_expedition")
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

    elif data.startswith("cell_"):
        _, row, col = data.split('_')
        with sq.connect("gnomes.db") as con:
            cursor = con.cursor()
            cursor.execute(
                "SELECT tickets_to_expedition FROM users_gnomes WHERE user_id=? AND is_dead!=1", (user_id,))
            row = cursor.fetchone()

            if row[0] != 0:
                output = random_meat()
                a = random.randint(1, 100)
                if a >= 50:
                    cursor.execute("UPDATE users_gnomes SET meat=? WHERE user_id=? AND is_dead!=1",
                                   (output+show_meat(user_id), user_id))
                    cursor.execute("UPDATE users_gnomes SET tickets_to_expedition=? WHERE user_id=? AND is_dead!=1",
                                   (row[0]-1, user_id))
                    bot.send_message(
                        user_id, f"Вы сходили на вылазку и получили {output} кусков мяса!")
                    bot.answer_callback_query(call.id)
                else:
                    cursor.execute("UPDATE users_gnomes SET beer=? WHERE user_id=? AND is_dead!=1",
                                   (output+show_beer(user_id), user_id))
                    cursor.execute("UPDATE users_gnomes SET tickets_to_expedition=? WHERE user_id=? AND is_dead!=1",
                                   (row[0]-1, user_id))
                    bot.send_message(
                        user_id, f"Вы сходили на вылазку и нашли {output} кружек пива!")
                    bot.answer_callback_query(call.id)
            if row[0] == 0:
                bot.send_message(
                    user_id, f"Гном слишком устал, чтобы куда то идти!")


def handle_go_on_expedition(message, user_id):
    markup = InlineKeyboardMarkup()
    for row in range(3):
        row_buttons = []
        for col in range(3):
            row_buttons.append(InlineKeyboardButton(
                "✅", callback_data=f"cell_{row}_{col}"))
        markup.add(*row_buttons)
    bot.send_message(
        user_id, "Выберите клетку для изучения:", reply_markup=markup)


def handle_my_gnomes(message, user_id):
    chat_show_my_gnomes(message, user_id)


def handle_show_meat(message, user_id):
    amount_of_meat = show_meat(user_id)
    amount_of_beer = show_beer(user_id)
    bot.send_message(
        user_id, f"В ваших запасах есть {amount_of_meat} кусков мяса и {amount_of_beer} кружек пива")


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
        bot.send_message(user_id, f"{gnome_name} выбрался из темной пещеры!")
    else:
        bot.send_message(
            user_id, "Не удалось создать гнома. Попробуйте еще раз или обратитесь за помощью.")


def chat_get_hunger_level(message, user_id):

    gnome = get_gnome(user_id)
    if gnome:
        hunger = gnome.get_hunger_level()
        thirst = gnome.get_thirst_level()

        bot.reply_to(
            message, f"Ваш гном {dwtesting.level_of_hunger(hunger)} и {dwtesting.level_of_thirst(thirst)}")

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
                    message, f"Вы покормили {gnome.name}! Теперь он {dwtesting.level_of_hunger(gnome.get_hunger_level())}")
            else:
                bot.reply_to(
                    message, f"Вы покормили {gnome.name}! Теперь он {dwtesting.level_of_hunger(gnome.get_hunger_level())}. Запасы мяса иссякли!")
        else:
            bot.reply_to(
                message, f"Запасы мяса иссякли - скорее отправляйтесь на охоту!")
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
                    message, f"Вы угостили {gnome.name} пивом! Теперь он {dwtesting.level_of_thirst(gnome.get_thirst_level())}")
            else:
                bot.reply_to(
                    message, f"Вы угостили {gnome.name} пивом! Теперь он {dwtesting.level_of_thirst(gnome.get_thirst_level())}. Запасы пива иссякли!")
        else:
            bot.reply_to(
                message, f"Запасы пива иссякли - скорее отправляйтесь на поиски!")
    else:
        bot.reply_to(
            message, "У вас еще нет гнома. Используйте команду /start, чтобы создать своего первого гнома.")


def schedule_checker_hunger():
    while True:
        with sq.connect("gnomes.db") as con:
            cursor = con.cursor()
            cursor.execute("SELECT user_id FROM users_gnomes")
            user_ids = cursor.fetchall()
            for user_id in user_ids:
                decrease_hunger_level(user_id[0])
            sleep(500)


def schedule_checker_thirst():
    while True:
        with sq.connect("gnomes.db") as con:
            cursor = con.cursor()
            cursor.execute("SELECT user_id FROM users_gnomes")
            user_ids = cursor.fetchall()
            for user_id in user_ids:
                decrease_thirst_level(user_id[0])
            sleep(700)


def schedule_checker_tickets():
    while True:
        with sq.connect("gnomes.db") as con:
            cursor = con.cursor()
            cursor.execute("SELECT user_id FROM users_gnomes")
            user_ids = cursor.fetchall()
            for user_id in user_ids:
                increase_tickets(user_id[0])
            sleep(700)


def main():
    initialize_meat_grid()
    Thread(target=schedule_checker_hunger).start()
    Thread(target=schedule_checker_thirst).start()
    Thread(target=schedule_checker_tickets).start()
    bot.infinity_polling()


if __name__ == '__main__':
    main()
