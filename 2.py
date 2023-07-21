import telebot
import schedule
import dw
import random
import math
from threading import Thread
import sqlite3 as sq
from time import sleep
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# Один кусок мяс восстанавливает 10 единиц голода

with sq.connect("gnomes.db") as con:
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users_gnomes (
            user_id INTEGER,
            gnome_name TEXT,
            hunger_level INTEGER,
            meat INTEGER
    )
                """)


bot = telebot.TeleBot("6370080307:AAEm_cm-4O06Ond8OzUA0ht4Koo3OOljsZY")


def create_gnome(user_id, gnome_name):
    with sq.connect("gnomes.db") as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM users_gnomes WHERE user_id=?", (user_id,))
        num_gnomes = cursor.fetchone()[0]

        if num_gnomes > 0:
            return None

        gnome = dw.Dwarf(gnome_name)
        gnome.feed(100)
        cursor.execute("INSERT INTO users_gnomes (user_id, gnome_name, hunger_level, meat) VALUES (?, ?, ?, ?)",
                       (user_id, gnome_name, 100, 10))
    return gnome


def get_gnome(user_id):
    with sq.connect("gnomes.db") as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT gnome_name, hunger_level FROM users_gnomes WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        if row:
            gnome_name, hunger_level = row
            gnome = dw.Dwarf(gnome_name)
            gnome.feed(hunger_level)
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
                "UPDATE users_gnomes SET hunger_level=? WHERE user_id=?", (hunger, user_id))


def show_meat(user_id):
    with sq.connect("gnomes.db") as con:
        cursor = con.cursor()
        cursor.execute(
            "SELECT meat FROM users_gnomes WHERE user_id=?", (user_id,))
        row = cursor.fetchone()
        return row[0]


def count_piece_of_meat_to_feed(hunger):
    if hunger >= 85:
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
            else:
                gnome.feed(meat*10)
                meat = 0
                cursor = con.cursor()
                cursor.execute(
                    "UPDATE users_gnomes SET hunger_level=? WHERE user_id=?", (hunger, user_id))
                cursor.execute(
                    "UPDATE users_gnomes SET meat=? WHERE user_id=?", (meat, user_id))


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Создать гнома", callback_data="create_gnome"),
        InlineKeyboardButton("Мои гномы", callback_data="my_gnomes"),
        InlineKeyboardButton("Посмотреть уровень голода",
                             callback_data="hunger_level"),
        InlineKeyboardButton("Покормить гнома", callback_data="feed_gnome"),
        InlineKeyboardButton("Проверить запасы", callback_data="show_meat")
    )
    bot.send_message(user_id, "Выберите действие:", reply_markup=markup)


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


def handle_my_gnomes(message, user_id):
    chat_show_my_gnomes(message, user_id)


def handle_show_meat(message, user_id):
    amount_of_meat = show_meat(user_id)
    bot.send_message(
        user_id, f"В ваших запасах есть {amount_of_meat} кусков мяса")


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


def handle_hunger_level(message, user_id):
    chat_get_hunger_level(message, user_id)


def chat_get_hunger_level(message, user_id):

    gnome = get_gnome(user_id)
    if gnome:
        hunger = gnome.get_hunger_level()
        bot.reply_to(message, f"Ваш гном {dw.level_of_hunger(hunger)}")
        print(hunger)
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
                    message, f"Вы покормили {gnome.name}! Теперь он {dw.level_of_hunger(gnome.get_hunger_level())}")
            else:
                bot.reply_to(
                    message, f"Вы покормили {gnome.name}! Теперь он {dw.level_of_hunger(gnome.get_hunger_level())}. Запасы мяса иссякли!")
        else:
            bot.reply_to(
                message, f"Запасы мяса иссякли - скорее отправляйтесь на охоту!")
    else:
        bot.reply_to(
            message, "У вас еще нет гнома. Используйте команду /start, чтобы создать своего первого гнома.")


def schedule_checker():
    while True:
        with sq.connect("gnomes.db") as con:
            cursor = con.cursor()
            cursor.execute("SELECT user_id FROM users_gnomes")
            user_ids = cursor.fetchall()
            for user_id in user_ids:
                decrease_hunger_level(user_id[0])
            sleep(10)


def main():

    Thread(target=schedule_checker).start()
    bot.infinity_polling()


if __name__ == '__main__':
    main()
