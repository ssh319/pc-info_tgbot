import os

from telebot import TeleBot
from input_handler import UserInput


API_TOKEN = os.environ["TG_TOKEN"]

bot = TeleBot(API_TOKEN)

@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "Введите линейку необходимого устройства и его модель."
    )


@bot.message_handler(content_types=["text"])
def get_data(message):

    user_request = UserInput(message.text)
    requested_component = user_request.get_requested_component()

    if requested_component is not None:
        bot.send_message(message.chat.id, requested_component.get_response())
        return
    
    # Respond with error message
    if hasattr(user_request, "input_family"):
        bot.send_message(message.chat.id, f"Название '{user_request.input_family}' не распознано.")
        return
    
    help_message = (
        "Ввод не содержит разделённых ПРОБЕЛОМ линейки и модели устр-ва.\n\n"
        "Корректные примеры использования:\ni5 9400f\nradeon rx 580\nrtx 2080 ti"
    )

    bot.send_message(message.chat.id, help_message)


if __name__ == "__main__":
    bot.infinity_polling()
