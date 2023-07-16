import telebot
import schedule
import dw
from threading import Thread
from time import sleep

bot = telebot.TeleBot("6370080307:AAEm_cm-4O06Ond8OzUA0ht4Koo3OOljsZY")

gnome = dw.Dwarf()

def decrease_hunger_level():
    gnome.starve(10)

@bot.message_handler(commands=['hunger_level'])
def get_hunger_level(message):
    hunger = gnome.get_hunger_level()
    bot.reply_to(message, f"Сыстость гнома составляет {hunger}%")

def schedule_checker():
    while True:
        decrease_hunger_level()
        sleep(15*60)

def main():

    Thread(target=schedule_checker).start() 

    # And then of course, start your server.
    
    bot.infinity_polling()
    


if __name__ == '__main__':
    main()
    
    
