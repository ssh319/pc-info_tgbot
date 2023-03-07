import os
from _data import search, _series
from telebot import TeleBot
from background import non_stop


API_TOKEN = os.environ.get('*token*')

bot = TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        'Введите линейку устройства и его модель через \"-\" (дефис)'
    )


@bot.message_handler(content_types=['text'])
def get_data(message):
    message.text = message.text.split('-', 1)
    if len(message.text) == 2:
        inp_series = message.text[0].strip().lower().replace(' ', '_')
        inp_model = message.text[1].strip().lower().replace(' ', '_')

        app = None

        for pattern in _series:
            if search(pattern[3:], inp_series):

                if pattern.startswith("CPU"):
                    from _data import CPU

                    inp_series = _series[pattern] if pattern == 'CPUryzen_tr' else _series[pattern] % inp_series
                    
                    if inp_model in ('gold_g6400',):
                        inp_model += '_'

                    app = CPU(series=inp_series, model=inp_model)
                    break

                elif pattern.startswith("GPU"):
                    from _data import GPU

                    inp_series = _series[pattern] % inp_series
                    
                    if inp_model == "1060":
                        inp_model += "_6gb"

                    app = GPU(series=inp_series, model=inp_model)
                    break
        if app:
            bot.send_message(message.chat.id, app.get_params())


if __name__ == '__main__':
    non_stop()
    bot.infinity_polling()
