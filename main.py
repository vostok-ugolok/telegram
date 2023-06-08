from telebot import *
from associations import *
import os
from threading import Thread
import requests
import json
import socketio
import socketio.exceptions

host = "185.246.64.64:4999"
client_bot = TeleBot(token=os.environ["VOSTOK_UGOLOK_TOKEN"])
client_bot.parse_mode = 'html'

order_to_user = Associations()
sio = socketio.Client()
owner = '399445674'

try:
    sio.connect('ws://' + host)

except socketio.exceptions.ConnectionError:
    client_bot.send_message(owner, '🔥  Не удаётся подключиться к серверу! Бот отключён')
    exit()

@client_bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()[1:]
    if args != []:
        order_id = args[0]

        order = requests.get('http://' + host + f'/order/get?id={order_id}').json()[0]

        name = order['name']
        phone = order['phone']
        adress = order['adress']
        creation_time = order['creation_time']

        if adress in ('', 'cass', 'inside'):
            order_to_user.assoc_add(order, message.from_user.id)
            order_to_user.save()

            client_bot.send_message(message.from_user.id, f"""<b>Добрый день!</b>
                             
📍  Выбран заказ номер <b>{order_id}</b>

👨🏻  Имя: <b>{name}</b>

📞  Номер телефона: <b>{phone}</b>

⚡  Заказ был отправлен в кафе в <b>{''.join(creation_time.split()[1][:-3])}</b>
Мы отправим уведомление, когда он будет готов""")
            
        else:
            client_bot.send_message(message.from_user.id, f"""Добрый день!
Выбранный Вами заказ под номером {order_id} доставляется через сервис Яндекс.Еда
Для отслеживания заказа используйте соответствующее приложение""")

@sio.on('ORDER STATE CHANGED')
def on_order_ready(id_state: list):
    order_id = id_state[0]
    order_state = id_state[1]
    order_addinfo = None

    if (len(id_state) > 2):
        order_addinfo = id_state[2]

    if order_state == 'READY':
        for uid in order_to_user.data[order_id]:
            client_bot.send_message(uid, f'🕒 Ваш заказ готов!\n \nНомер заказа: <b>{order_id}</b>')
    
    elif order_addinfo != None:
        for uid in order_to_user.data[order_id]:
            client_bot.send_message(uid, f'⚠ Новая информация по Вашему заказу\n \nНомер заказа: <b>{order_id}</b>\n\n{order_addinfo}')

@sio.on('connection')
def connected():
    client_bot.send_message(owner, '✅  Подключение к серверу восстановлено')

if __name__ == '__main__':
    print('⚡  Бот-клиент запустился')
    
    client_bot.infinity_polling()