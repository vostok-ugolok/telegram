from threading import Thread
from telebot import *
import os
import requests
host = "212.109.193.12:5000"

admin_bot = TeleBot(token=os.environ["VOKSTOK_UGOLOK_TOKEN_ADMIN"])
admin_bot.parse_mode = 'html'

def order_to_string(order):
    return f"""🛒  Номер #{order['order_id']}:

Создан: {order['creation_time']}
Клиент: {order['name']}
{('''Тип заказа: доставка
Адрес: ''' + order['adress']) if order['adress'] != '' else 'Тип заказа: в кафе'}
"""


@admin_bot.callback_query_handler(func=lambda call: call.data.split()[0] == 'order' and call.message)
def orders_navigate(call):
    data = requests.get('http://' + host + f'/order/get').json()

    direction = call.data.split()[1]

    if direction == 'right':
        left = int(call.data.split()[2])
        right = left + min(len(data) - left, 4)
    else:
        left = int(call.data.split()[2]) - min(int(call.data.split()[2]), 4)
        right = left + min(len(data) - left, 4)

    response = f"""📫  Заказы {left} - {right}\n"""
    for order in data[left:right]:
        response += '\n\n' + order_to_string(order)

    go_left_button = types.InlineKeyboardButton(text="<", callback_data=f"order left {left}")
    go_right_button = types.InlineKeyboardButton(text=">", callback_data=f"order right {right}")

    if left > 0 and right < len(data):
        markup = types.InlineKeyboardMarkup().row(go_left_button, go_right_button)

    elif right == len(data):
        markup = types.InlineKeyboardMarkup().row(go_left_button)
    
    elif left == 0:
        markup = types.InlineKeyboardMarkup().row(go_right_button)

    admin_bot.edit_message_text(response, call.message.chat.id, call.message.message_id, reply_markup=markup)


@admin_bot.message_handler(commands=['orders'])
def orders(message):
    data = requests.get('http://' + host + f'/order/get').json()
    left, right = 0, min(4, len(data))
    response = f"""📫  Заказы  {left} - {right}\n"""

    for order in data[left:right]:
        response += '\n\n' + order_to_string(order)

    go_left_button = types.InlineKeyboardButton(text="<", callback_data=f"order left {right}")
    go_right_button = types.InlineKeyboardButton(text=">", callback_data=f"order right {right}")
    
    admin_bot.send_message(message.from_user.id, response, reply_markup=types.InlineKeyboardMarkup().row(go_left_button, go_right_button))

@admin_bot.message_handler(commands=['ready'])
def ready(message):
    admin_bot.register_next_step_handler(message, got_id)
    admin_bot.reply_to(message, '💡  Введите идентификатор заказа')

def got_id(message):
    order_id = int(message.text.replace('#', ''))
    print(requests.post('http://' + host + f'/order/state/update?id={order_id}', json={"new_state" : "READY", 'order_id': order_id}).text)

    admin_bot.reply_to(message, '✅  Информация отправлена')

@admin_bot.message_handler(commands=['notify'])
def notify(message):
    admin_bot.register_next_step_handler(message, got_id_before_message)
    admin_bot.reply_to(message, '💡  Введите идентификатор заказа')

def got_id_before_message(message):
    order_id = int(message.text.replace('#', ''))

    admin_bot.reply_to(message, '📩  Введите сообщение')

    admin_bot.register_next_step_handler(message, got_message, order_id)

def got_message(message, order_id):
    print(requests.post('http://' + host + f'/order/state/update?id={order_id}', json={"new_state" : f"STATE CHANGED AT {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", 'order_id': order_id, 'message': message.text}).text)

    admin_bot.reply_to(message, '✅  Информация отправлена')

def food_to_string(food):
    name = food['name']
    price = food['price']
    image = food['image']
    description = food['description']
    identifier = food['identifier']

    return f"""•  {name}  ( <b>{identifier}</b> )
    Цена: <b>{price} ₽</b>
    Описание: {description}"""

@admin_bot.message_handler(commands=['menu'])
def menu(message):
    result = requests.get('http://' + host + '/food/get').json()

    response = '🎁  Меню'

    for food in result:
        response += '\n\n' + food_to_string(food)

    admin_bot.send_message(message.from_user.id, response)

print('⚡  Бот-админ запустился')
admin_bot.infinity_polling()