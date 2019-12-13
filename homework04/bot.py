import datetime
from typing import List, Tuple

import config
import requests
import telebot
from bs4 import BeautifulSoup


# Создание бота с указанным токеном доступа
bot = telebot.TeleBot(config.API_TOKEN)


def get_page(group: str, week: str = '') -> str:
    if week:
        week = str(week) + '/'
    if week == '0/':
        url = f'{config.domain}/{group}/schedule.htm'
    else:
        url = f'{config.domain}/{group}/{week}raspisanie_zanyatiy_{group}.htm'
    response = requests.get(url)
    web_page = response.text
    return web_page


def get_today() -> Tuple[int, int]:
    soup = BeautifulSoup(get_page('M3136', '0'), 'html5lib')
    week_string = soup.find("h2", attrs={"class": "schedule-week"}).find("strong").text
    week_num = 2 if week_string == "Нечетная" else 1
    return week_num, datetime.datetime.now().weekday() + 1


def get_schedule(web_page: str, n: str) -> Tuple[List[str], List[str], List[str]]:
    soup = BeautifulSoup(web_page, "html5lib")
    times_list, locations_list, lessons_list = ['Расписание пар на этот день я'], ['к сожалению'], ['не нашел']
    schedule_table = soup.find("table", attrs={"id": n + "day"})

    if schedule_table:
        # Время проведения занятий
        times_list = schedule_table.find_all("td", attrs={"class": "time"})
        times_list = [time.span.text for time in times_list]

        # Место проведения занятий
        locations_list = schedule_table.find_all("td", attrs={"class": "room"})
        locations_list = [room.span.text for room in locations_list]

        # Название дисциплин и имена преподавателей
        lessons_list = schedule_table.find_all("td", attrs={"class": "lesson"})
        lessons_list = [lesson.text.split('\n\n') for lesson in lessons_list]
        lessons_list = [', '.join([info for info in lesson_info if info]) for lesson_info in lessons_list]

    return times_list, locations_list, lessons_list


@bot.message_handler(commands=['near_lesson'])
def get_near_lesson(message: str) -> None:
    try:
        _, group = message.text.split()
    except ValueError:
        bot.send_message(message.chat.id, "Enter your group", parse_mode='HTML')
        return
    group = group.upper()

    (w, n), time = get_today(), datetime.datetime.now().time()
    web_page = get_page(group, str(w))
    times_lst, locations_lst, lessons_lst = get_schedule(web_page, str(n))
    today_im_done = times_lst[0] == 'Расписание пар на этот день я'
    if not today_im_done:
        for i in range(len(times_lst)):
            fin_time = datetime.datetime.combine(datetime.date.today(), datetime.datetime.strptime(times_lst[i][6:], "%H:%M").time())
            if fin_time > datetime.datetime.now() and i + 1 != len(times_lst):
                resp = '<i>Сегодня</i>\n\n<b>{}</b>, {}, {}\n'.format(times_lst[i], locations_lst[i], lessons_lst[i])
                bot.send_message(message.chat.id, resp, parse_mode='HTML')
            else:
                today_im_done = True
    if today_im_done:
        n += 1
        if n == 7 and w == 1:
            w, n = 2, 1
        elif n == 7 and w == 2:
            w, n = 1, 1
        web_page = get_page(group, str(w))
        times_lst, locations_lst, lessons_lst = get_schedule(web_page, str(n))
        while times_lst[-1] == 'Расписание пар на этот день я':
            n += 1
            if n == 7 and w == 1:
                w, n = 2, 1
            elif n == 7 and w == 2:
                w, n = 1, 1
            web_page = get_page(group, str(w))
            times_lst, locations_lst, lessons_lst = get_schedule(web_page, str(n))
        resp = '<i>%s</i>\n\n' % (['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'][n - 1])
        resp += '<b>{}</b>, {}, {}\n'.format(times_lst[0], locations_lst[0], lessons_lst[0])

        bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['tomorrow'])
def get_2morrow(message: str) -> None:

    try:
        _, group = message.text.split()
    except ValueError:
        bot.send_message(message.chat.id, "Enter your group", parse_mode='HTML')
        return
    group = group.upper()
    w, n = get_today()
    if n == 7 and w == 1:
        w, n = 2, 1
    elif n == 7 and w == 2:
        w, n = 1, 1
    else:
        n += 1
    web_page = get_page(group, str(w))
    times_lst, locations_lst, lessons_lst = get_schedule(web_page, str(n))
    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)
    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['all'])
def get_all(message: str) -> None:

    try:
        _, week, group = message.text.split()
    except ValueError:
        bot.send_message(message.chat.id, "Enter week and your group", parse_mode='HTML')
        return
    try:
        week = int(week)
    except ValueError:
        bot.send_message(message.chat.id, 'Enter valid week number')
        return
    group = group.upper()

    if week > 0:
        week = 2 if week % 2 == 0 else 1
    web_page = get_page(group, str(week))
    for i in range(1, 7):
        resp = '<i>%s</i>\n\n' % (['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'][i - 1])
        times_lst, locations_lst, lessons_lst = get_schedule(web_page, str(i))

        for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
            resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)
        bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['monday'])
def get_monday(message: str) -> None:

    try:
        _, week, group = message.text.split()
    except ValueError:
        bot.send_message(message.chat.id, "Enter week and your group", parse_mode='HTML')
        return
    try:
        week = int(week)
    except ValueError:
        bot.send_message(message.chat.id, 'Enter valid week number')
        return
    group = group.upper()

    if week > 0:
        week = 2 if week % 2 == 0 else 1
    web_page = get_page(group, str(week))
    times_lst, locations_lst, lessons_lst = get_schedule(web_page, '1')

    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)

    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['tuesday'])
def get_tuesday(message: str) -> None:

    try:
        _, week, group = message.text.split()
    except ValueError:
        bot.send_message(message.chat.id, "Enter week and your group", parse_mode='HTML')
        return
    try:
        week = int(week)
    except ValueError:
        bot.send_message(message.chat.id, 'Enter valid week number')
        return
    group = group.upper()

    if week > 0:
        week = 2 if week % 2 == 0 else 1
    web_page = get_page(group, str(week))
    times_lst, locations_lst, lessons_lst = get_schedule(web_page, '2')

    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)

    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['wednesday'])
def get_wednesday(message: str) -> None:

    try:
        _, week, group = message.text.split()
    except ValueError:
        bot.send_message(message.chat.id, "Enter week and your group", parse_mode='HTML')
        return
    try:
        week = int(week)
    except ValueError:
        bot.send_message(message.chat.id, 'Enter valid week number')
        return
    group = group.upper()

    if week > 0:
        week = 2 if week % 2 == 0 else 1
    web_page = get_page(group, str(week))
    times_lst, locations_lst, lessons_lst = get_schedule(web_page, '3')

    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)

    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['thursday'])
def get_thursday(message: str) -> None:

    try:
        _, week, group = message.text.split()
    except ValueError:
        bot.send_message(message.chat.id, "Enter week and your group", parse_mode='HTML')
        return
    try:
        week = int(week)
    except ValueError:
        bot.send_message(message.chat.id, 'Enter valid week number')
        return
    group = group.upper()

    if week > 0:
        week = 2 if week % 2 == 0 else 1
    web_page = get_page(group, str(week))
    times_lst, locations_lst, lessons_lst = get_schedule(web_page, '4')

    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)

    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['friday'])
def get_friday(message: str) -> None:

    try:
        _, week, group = message.text.split()
    except ValueError:
        bot.send_message(message.chat.id, "Enter week and your group", parse_mode='HTML')
        return
    try:
        week = int(week)
    except ValueError:
        bot.send_message(message.chat.id, 'Enter valid week number')
        return
    group = group.upper()

    if week > 0:
        week = 2 if week % 2 == 0 else 1
    web_page = get_page(group, str(week))
    times_lst, locations_lst, lessons_lst = get_schedule(web_page, '5')

    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)

    bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['saturday'])
def get_saturday(message: str) -> None:

    try:
        _, week, group = message.text.split()
    except ValueError:
        bot.send_message(message.chat.id, "Enter week and your group", parse_mode='HTML')
        return
    try:
        week = int(week)
    except ValueError:
        bot.send_message(message.chat.id, 'Enter valid week number')
        return
    group = group.upper()

    if week > 0:
        week = 2 if week % 2 == 0 else 1
    web_page = get_page(group, str(week))
    times_lst, locations_lst, lessons_lst = get_schedule(web_page, '6')

    resp = ''
    for time, location, lession in zip(times_lst, locations_lst, lessons_lst):
        resp += '<b>{}</b>, {}, {}\n'.format(time, location, lession)

    bot.send_message(message.chat.id, resp, parse_mode='HTML')


if __name__ == '__main__':
    bot.polling()
