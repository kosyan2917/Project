import requests
from PIL import Image
import telebot
import tornado.web
import uuid
import tornado.ioloop
from threading import Thread

token = "437468185:AAG5ewFYO9cV2VVWFIlcLhcedkz1Piv46Mc"
bot = telebot.TeleBot(token)

tasks_base = open('tasks.txt', 'r')
global tasks
tasks = tasks_base.read()
tasks_list = tasks.split('.')
tasks_base.close()
tasks_price = []
for i in range(0,len(tasks_list),2):
    prices = {'name': tasks_list[i], 'price': tasks_list[i+1]}
    tasks_price.append(prices)

@bot.message_handler(commands=['tasks'])
def tasks_handler(message):
    tasks_base = open('tasks.txt', 'r')
    global tasks
    tasks = tasks_base.read()
    tasks_list = tasks.split('.')
    tasks_base.close()
    tasks_price = []
    for i in range(0, len(tasks_list), 2):
        prices = {'name': tasks_list[i], 'price': tasks_list[i + 1]}
        tasks_price.append(prices)
    for i in range(0, len(tasks_price)):
        bot.send_message(message.chat.id, tasks_price[i]['name'] + " - " + tasks_price[i]['price'])
#@bot.message_handler(commands='start')

@bot.message_handler(commands=['task_add'])
def adding_task(message):
    message = bot.send_message(message.chat.id, 'Введите название задания и цену по образцу: "Название задания.цена" . Пример: "Помощь в уборке.100".')
    bot.register_next_step_handler(message,adding_task_to_file)
def adding_task_to_file(message):
    text = message.text
    add_task = text.split('.')
    tasks_base = open('tasks.txt', 'w')
    tasks_base.write('{0}.{1}.{2}GT'.format(tasks, add_task[0],add_task[1]))
    tasks_base.close()
    bot.send_message(user['user'], 'Задание добавилось ( но это не точно )')
@bot.message_handler(commands=['auth'])
def authorising(message):
    message = bot.send_message(message.chat.id, 'Введите токен:' )
    bot.register_next_step_handler(message, make_auth)
def make_auth(message):
    text = message.text
    print(text)
    response = requests.get("https://6e7a3a7c.ngrok.io/new/api/users/")
    answer = response.json()
    print(answer)
    print(response.status_code)
    if response.status_code==403:
        global user
        user = {'user': message.chat.id, 'token': text}
        bot.send_message(user['user'], 'Пользователь {0} успешно авторизирован токеном {1}'.format(user['user'],user['token']))
    else:
        bot.send_message(message.chat.id, 'Параша, чувак')


class MainHandler(tornado.web.RequestHandler):
    def get(self):

        token = self.get_argument("token")
        type = self.get_argument("type")
        comment = self.get_argument("comment")
        amount = self.get_argument("amount")

        # TODO: проверить есть ли пользователь среди атворизованных и отправить нормальное уведомление с понятным текстом

        if token == user['token']:
            if type == "add":
                img = open('+.jpg', 'rb')
                img = img.read()
                bot.send_photo(user['user'], img)
                bot.send_message(user['user'], "На ваш счет было начисленно {0} GoToCoin'ов".format(amount))
                self.write('{"result": "OK"}')
            elif type == "buy":
                img = open('-.png', 'rb')
                img = img.read()
                bot.send_photo(user['user'], img)
                bot.send_message(user['user'], "C вашего счета было списано {0} GoToCoin'ов".format(amount))
            else:
                img = open('gear.jpg', 'rb')
                img = img.read()
                bot.send_photo(user['user'], img)
                bot.send_message(user['user'], "Поддержка прислала такой ответ: {0}".format(comment))
        else:
            self.write('{"result": "NOT FOUND"}')

# запуск веб сервера
def start_server():
    routes = [
            (r"/notify", MainHandler),
    ]

    app = tornado.web.Application(routes)
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
def polling():
    bot.polling(none_stop=True)

# в одном потоке телеграм, в другом сервер
server = Thread(target=start_server)
telegram = Thread(target=polling)

server.start()
telegram.start()