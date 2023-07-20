import telebot
import schedule
import dw
from threading import Thread
import sqlite3 as sq
from time import sleep
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

with sq.connect("gnomes.db") as con:
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users_gnomes (
            user_id INTEGER,
            gnome_name TEXT,
            hunger_level INTEGER
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
        cursor.execute("INSERT INTO users_gnomes (user_id, gnome_name, hunger_level) VALUES (?, ?, ?)",
                       (user_id, gnome_name, 100))
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


@bot.message_handler(commands=['my_gnomes'])
def chat_show_my_gnomes(message):
    user_id = message.from_user.id
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
            print(hunger)
            cursor = con.cursor()
            cursor.execute(
                "UPDATE users_gnomes SET hunger_level=? WHERE user_id=?", (hunger, user_id))


def increase_hunger_level(user_id):
    gnome = get_gnome(user_id)
    if gnome:
        with sq.connect("gnomes.db") as con:
            gnome.feed(15)
            hunger = gnome.get_hunger_level()
            print(hunger)
            cursor = con.cursor()
            cursor.execute(
                "UPDATE users_gnomes SET hunger_level=? WHERE user_id=?", (hunger, user_id))


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    # Create buttons and add them to the message
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    button_create_gnome = KeyboardButton("Создать гнома")
    button_hunger = KeyboardButton("Посмотреть уровень голода")
    button_my_gnomes = KeyboardButton("Мои гномы")
    button_feed_gnome = KeyboardButton("Покормить гнома")
    markup.add(button_create_gnome)
    markup.add(button_hunger)
    markup.add(button_my_gnomes)
    markup.add(button_feed_gnome)

    bot.send_message(user_id, "Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Мои гномы")
def handle_my_gnomes(message):
    chat_show_my_gnomes(message)


@bot.message_handler(func=lambda message: message.text == "Создать гнома")
def handle_create_gnome(message):
    user_id = message.from_user.id
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
        bot.send_message(user_id, f"{gnome_name} выбрался из темной пещеры.")
    else:
        bot.send_message(
            user_id, "Не удалось создать гнома. Попробуйте еще раз или обратитесь за помощью.")


@bot.message_handler(func=lambda message: message.text == "Посмотреть уровень голода")
def handle_hunger_level(message):
    chat_get_hunger_level(message)


@bot.message_handler(func=lambda message: message.text == "Посмотреть всех моих гномов")
def handle_my_gnomes(message):
    chat_show_my_gnomes(message)


@bot.message_handler(commands=['hunger_level'])
def chat_get_hunger_level(message):
    user_id = message.from_user.id
    gnome = get_gnome(user_id)
    if gnome:
        hunger = gnome.get_hunger_level()
        bot.reply_to(message, f"Ваш гном {dw.level_of_hunger(hunger)}")
        print(hunger)
    else:
        bot.reply_to(
            message, "У вас еще нет гнома. Используйте команду /start, чтобы создать его.")


@bot.message_handler(func=lambda message: message.text == "Покормить гнома")
def handle_feed_gnome(message):
    user_id = message.from_user.id
    gnome = get_gnome(user_id)

    if gnome:
        # Call the function to increase hunger level
        increase_hunger_level(user_id)
        hunger = gnome.get_hunger_level()
        bot.send_message(
            user_id, f"Вы покормили {gnome.name}! Теперь он {dw.level_of_hunger(hunger)}")
    else:
        bot.send_message(
            user_id, "У вас еще нет гнома. Используйте команду /start, чтобы создать своего первого гнома.")


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
