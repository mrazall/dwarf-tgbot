import telebot
import schedule
import dw
import time

bot = telebot.TeleBot("6370080307:AAEm_cm-4O06Ond8OzUA0ht4Koo3OOljsZY")

gnome = dw.Dwarf()

def decrease_hunger_level():
    gnome.starve(10)

@bot.message_handler(commands=['hunger_level'])
def get_hunger_level(message):
    hunger = gnome.get_hunger_level()
    bot.reply_to(message, f"Сыстость гнома составляет {hunger}%")



def main():
    schedule.every(5).seconds.do(decrease_hunger_level)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
        print(gnome.get_hunger_level())
    


if __name__ == '__main__':
    main()
    
    
