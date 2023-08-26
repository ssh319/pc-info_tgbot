import os
from telebot import TeleBot
from input_handler import userInput


API_TOKEN = os.environ.get("*token*")

bot = TeleBot(API_TOKEN)

@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "Введите линейку устройства и его модель."
    )


@bot.message_handler(content_types=["text"])
def get_data(message):

    request = userInput(message.text)
    app = request.get_requested_component()

    if app is not None:
        bot.send_message(message.chat.id, app.get_response())
        return

    # Respond with error message
    bot.send_message(message.chat.id, "Название устройства не найдено.")


if __name__ == "__main__":
    bot.infinity_polling()
