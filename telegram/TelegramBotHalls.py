import telebot
from telegramtokens import telegramtoken_venthalls, botHalls_users
from telebot import types
import requests
import time
from headers import header, header_alarm_A, sauter_cookie
from plants import alarms_A, alarms_BC
from helpmsg import helpmsg_halls

bot = telebot.TeleBot(telegramtoken_venthalls)

places = {"Игровой зал": "ПВ-2.7, ПВ-2.8",
          "Раздевалки игрового зала": "ПВ-2.4",
          "Зал хореографии 2015": "ПВ-2.5",
          "Зал хореографии 2041": "ПВ-2.6"}

all_plants = {"ПВ-2.4": "8388808&did=33561432",
              "ПВ-2.5": "8388778&did=33560432",
              "ПВ-2.6": "8388770&did=33560432",
              "ПВ-2.7": "8388835&did=33561432",
              "ПВ-2.8": "8388827&did=33561432",
              }

states = {"2": "работает на высокой скорости",
          "1": "работает на низкой скорости",
          "0":  "остановлена"}

starts = ["Запуск  " + x for x in places.values()]
stops = ["Останов  " + x for x in places.values()]
curstates = ["Состояние  " + x for x in places.values()]
scheds = ["Расписание  " + x for x in places.values()]

rev_alarms_BC = {v[:6]: k for k, v in alarms_BC.items() if v[:6] in all_plants.keys()}
rev_alarms_A = {v[:6]: k for k, v in alarms_A.items() if v[:6] in all_plants.keys()}


@bot.message_handler(commands=['help'])
def start(message):
    m = message.chat.id
    if root(m):
        sms(m, helpmsg_halls)
    else:
        no_root(m)


@bot.message_handler(commands=['start'])
def start(message):
    m = message.chat.id
    if root(m):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Игровой зал")
        btn2 = types.KeyboardButton("Раздевалки игрового зала")
        btn3 = types.KeyboardButton("Зал хореографии 2015")
        btn4 = types.KeyboardButton("Зал хореографии 2041")
        markup.add(btn3, btn4)
        markup.add(btn2)
        markup.add(btn1)
        bot.send_message(m, "Выберите помещение", reply_markup=markup)
    else:
        no_root(m)


@bot.callback_query_handler(func=lambda callback: callback.data in ['1', '2'])
def check_speed(callback):
    m = callback.message.chat.id
    if root(m):
        tex = callback.message.text.replace("Выберите скорость работы", "Запуск ")
        sms(m,  "Стартуем.... ", 4)
        switch_plant(callback.message, tex, callback.data, "Запуск")
    else:
        no_root(m)


@bot.message_handler(content_types=['text'])
def func(message):
    m = message.chat.id
    if root(m):
        msg = message.text
        if msg == "Главное меню":
            start(message)

        # Информация
        elif msg in places.keys():
            vor = "обслуживает вентустановка"
            if "Игровой" in msg:
                vor = "обслуживают вентустановки"
            sms(m, f"{msg}\n{vor}  {places[msg]}", 1)
            reply(message, msg)

        # Расписание
        elif msg in scheds:
            sms(m, f"Ждите, сейчас узнаем ...", 4)
            fil = open("../logging/readlogs.txt", "r")
            sts = []
            for i in fil.read().split("\n"):
                if msg[-6:] in i:
                    sts.append(i.replace(f"{msg[-6:]}    ", ""))
            prn = "\n".join(sts).replace("\n", "\n\n").replace("0   ", "0\n")
            if prn == "":
                prn = "не задано"
            sms(m, f'{msg}\nна эти дни:\n\n{prn}', 1)
            sms(m)

        # Состояние
        elif msg in curstates:
            sms(m, f"Ждите, идет опрос ...", 2)
            sms(m, f"В текущий момент установка"
                   f" {msg[-6:]} {get_state(msg[-6:])}. "
                   f"{get_alarm(msg[-6:], rev_alarms_BC, 'Авария класса ВС')}"
                   f"{get_alarm(msg[-6:], rev_alarms_A,  'Авария класса А')}", 2)
            if "ПВ-2.7" in msg:
                sms(m, f"Установка {msg[-14:-8]} {get_state(msg[-14:-8])}."
                       f"{get_alarm(msg[-14:-8], rev_alarms_BC, 'Авария класса ВС')}"
                       f"{get_alarm(msg[-14:-8], rev_alarms_A,  'Авария класса А')}", 2)
            sms(m)

        # Запуск
        elif msg in starts:
            markup = types.InlineKeyboardMarkup()
            button2 = types.InlineKeyboardButton("Низкая", callback_data="1")
            button1 = types.InlineKeyboardButton("Высокая", callback_data="2")
            markup.add(button2, button1)
            mes = "Выберите скорость работы"
            if "ПВ-2.7" in msg:
                bot.send_message(message.chat.id, f"{mes} {msg[-14:]}", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, f"{mes} {msg[-6:]}", reply_markup=markup)

        # Останов
        elif msg in stops:
            p = "0"
            sms(m, "Останавливаемся....", 3)
            switch_plant(message, msg, p, "Останов")

        # Иное
        else:
            sms(m, "Что за команда, не понял?", 3)
            sms(m, "Чувак, здесь не надо набирать текст \nПросто жмем кнопки", 3)
            sms(m, "Идем на главную")
            start(message)
    else:
        no_root(m)


def sms(m, t="Выберите действие", s=0):
    """
    Отправка текстовых сообщений в бот
    :param m:
    :param t:
    :param s:
    :return:
    """

    bot.send_message(m, t)
    time.sleep(s)


def switch_plant(message, msg, p, action):
    m = message.chat.id
    if "ПВ-2.7, ПВ-2.8" in msg:
        ssg = f"{action}  ПВ-2.7"
        sms(m, ssg)
        g = all_plants[ssg.replace(f"{action}  ", "")]
        sms(m, f"{ssg} {do_switch(g, p, 'ПВ-2.7')}")
        psg = f"{action}  ПВ-2.8"
        sms(m, psg)
        g = all_plants[psg.replace(f"{action}  ", "")]
        sms(m, f"{psg} {do_switch(g, p, 'ПВ-2.8')}")
    else:
        g = all_plants[msg.replace(f"{action}  ", "")]
        bot.send_message(message.chat.id, f"{msg} {do_switch(g, p, msg[-6:])}")


def do_switch(g, p, plt):
    stmsg = "не выполнен.\n"
    url = f"http://192.168.250.50/ajaxjson/bac/setValue?pid=85&oid={g}&vid=17&value={p}"
    if check_alarm(plt):
        stmsg = stmsg + "Авария класса А"
    else:
        r = requests.get(url, headers=header_alarm_A, cookies=sauter_cookie)
        time.sleep(4)
        if '"message":"Value was successfully written"' in r.text:
            stmsg = "выполнен успешно.\n "
    return stmsg


def get_state(pl):
    url = f"http://192.168.250.50/svo/details/?oid={all_plants[pl]}&vid=17&mode=cached"
    resp = requests.get(url, headers=header_alarm_A, cookies=sauter_cookie)
    time.sleep(3)
    r = resp.text
    n = r[r.index('<tr data-pid="85">')+18:]
    e = n[:n.index('</tr>')]
    g = e[e.index("property-value")+16]
    return states[g]


def get_alarm(pl, dic, txt):
    url = f"http://192.168.250.50/svo/details/update?oid={dic[pl]}&vid=17&mode=cached"
    resp = requests.get(url, headers=header, cookies=sauter_cookie)
    time.sleep(3)
    almsg = ""
    if "Alarm: true" in resp.text:
        if 'title="Fault: true"' not in resp.text:
            almsg = txt
    return almsg


def check_alarm(pl):
    """
    check_alarm()  - Проверка отсутствия аварии класса А перед запуском
    :param pl:     -
    :return:
    """
    alm = 'Авария класса А'
    if get_alarm(pl, rev_alarms_A, alm) == alm:
        return True
    return False


def reply(message, place=""):
    answer = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton(f"Состояние  {places[place]}")
    button2 = types.KeyboardButton(f"Расписание  {places[place]}")
    button3 = types.KeyboardButton(f"Запуск  {places[place]}")
    button4 = types.KeyboardButton(f"Останов  {places[place]}")
    button5 = types.KeyboardButton("Главное меню")
    answer.add(button1, button2)
    answer.add(button3, button4)
    answer.add(button5)
    bot.send_message(message.chat.id, "Выберите действие".format(message.from_user), reply_markup=answer)


def root(m):
    return True if str(m) in botHalls_users.values() else False


def no_root(m):
    bot.send_message(m, "У Вас нет прав доступа к этому боту")


try:
    bot.infinity_polling(none_stop=True, timeout=180, long_polling_timeout=180, allowed_updates=['message', 'callback_query'])
except Exception as er:
    time.sleep(3)
    print(er)
    pass
