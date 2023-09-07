import os
from telebot import TeleBot
from input_handler import UserInput


API_TOKEN = os.environ.get("*token*")

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
    bot.send_message(message.chat.id, "Название устройства не найдено.")


if __name__ == "__main__":
    bot.infinity_polling()
