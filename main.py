from telebot import *
from associations import *
import os
import requests
import json
import socketio

bot = TeleBot(token=os.environ["VOSTOK_UGOLOK_TOKEN"])
bot.parse_mode = 'html'
order_to_user = Associations()
sio = socketio.Client()
sio.connect('ws://localhost:5000')

host = "http://localhost:5000"

@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()[1:]
    if args != []:
        order_id = args[0]

        order = requests.get(host + f'/order/get?id={order_id}').json()[0]

        name = order['name']
        phone = order['phone']
        adress = order['adress']
        creation_time = order['creation_time']

        if adress in ('', 'cass', 'inside'):
            order_to_user.assoc(order, message.from_user.id)
            order_to_user.save()

            bot.send_message(message.from_user.id, f"""<b>Добрый день!</b>
                             
📍  Выбран заказ номер <b>{order_id}</b>

👨🏻  Имя: <b>{name}</b>

📞  Номер телефона: <b>{phone}</b>

⚡  Заказ был отправлен в кафе в <b>{''.join(creation_time.split()[1][:-3])}</b>
Мы отправим уведомление, когда он будет готов""")
            
        else:
            bot.send_message(message.from_user.id, f"""Добрый день!
Выбранный Вами заказ под номером {order_id} доставляется через сервис Яндекс.Еда
Для отслеживания заказа используйте соответствующее приложение""")

@sio.on('ORDER IS READY')
def on_order_ready(order_id):
    bot.send_message(order_to_user.data[order_id], f'🕒 Ваш заказ готов!\n\nНомер заказа: <b>{order_id}</b>')

if __name__ == '__main__':
    print('⚡ Бот запущен')
    bot.infinity_polling()