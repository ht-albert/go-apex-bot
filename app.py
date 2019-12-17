import os
import random
import telebot


bot = telebot.TeleBot(token=os.getenv('API_TOKEN'))

# telebot.apihelper.proxy = {'https': 'https://141.125.82.106:80'}   # This is need for local debuging

config = {}

because_i_am = {
    'no': ['я лох', 'я говнюк', 'я каблук', 'я каблук', 'я чмо', 'я гей', 'я турок', 'я грузин', 'я азер', 'я иду на квеструм',
           'сиськи дороже пацанов', 'жена не разрешает', 'устал стоять на коленях и просить поиграть'],
    'yes': ['я красава', 'я лев', 'я тигр', 'я Армянин', 'я Осетин', 'я Даг', 'я мужик', 'я ваша единственная надежда на победу',
            'пацаны дороже сисек', 'я Бэтмен', 'русские не сдаются'],
}


@bot.message_handler(commands=['reset'])
def reset_apex(message):
    chat_id = message.chat.id
    poll = config.pop(chat_id, None)
    if poll:
        bot.delete_message(chat_id, poll['message'])


@bot.message_handler(commands=['apex'])
def send_apex_request(message):
    t_param = '-t'
    chat_id = message.chat.id
    active_poll = config.pop(chat_id, None)

    if active_poll:
        bot.delete_message(chat_id, active_poll.get('message'))

    time = __get_time(message.text, t_param) if t_param in message.text else ''

    mess = bot.send_message(
        chat_id,
        f"Ну что, кто готов сыграть в APEX {time}?",
        reply_markup=get_markup(),
    )

    config[chat_id] = {
        'message': mess.message_id,
        'users': []
    }


@bot.callback_query_handler(func=lambda call: call.data in ['yes', 'no'])
def apex_poll_call(call):
    chat_id = call.message.chat.id
    is_exists, is_all = check_press_button_user(call)

    if is_exists is False:
        bot.delete_message(chat_id, config[chat_id]['message'])
        mess = bot.send_message(
            chat_id, update_text(call), reply_markup=None if is_all else get_markup(),
        )
        config[chat_id]['message'] = mess.message_id

    if is_all:
        config.pop(chat_id)

    bot.answer_callback_query(call.id, text="")


def check_press_button_user(call):
    chat_id = call.message.chat.id

    try:
        press_users = config[chat_id]['users']
    except KeyError:
        bot.delete_message(chat_id, call.message.message_id)
        return None, None

    if call.from_user.username in press_users:
        return True, False

    press_users.append(call.from_user.username)
    is_all = len(press_users) == bot.get_chat_members_count(chat_id) - 1

    return False, is_all


def get_markup():
    markup = telebot.types.InlineKeyboardMarkup()

    row = [
        telebot.types.InlineKeyboardButton('Да', callback_data='yes'),
        telebot.types.InlineKeyboardButton('Нет', callback_data='no'),
    ]

    markup.row(*row)
    return markup


def update_text(call):
    text = call.message.text + '\n\n'
    user = call.from_user.first_name or "@" + call.from_user.username
    because = random.choice(because_i_am[call.data])

    return text + f"{user}: Я {'пас' if call.data == 'no' else 'за'}, потому что {because}"


def __get_time(text, param):
    command = text.replace('=', '')
    time = command.split(param)[1]

    try:
        assert time and ':' in time and int(time.split(':')[0]) <= 24 and int(time.split(':')[1]) <= 60
    except AssertionError:
        time = ''

    return time


if __name__ == "__main__":
    bot.polling()
