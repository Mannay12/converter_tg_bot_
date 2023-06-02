import requests
from bs4 import BeautifulSoup
import re
import telebot
from telebot import types

TOKEN = '5911937230:AAG-YqJGOYGS-dWcxome'
bot = telebot.TeleBot(TOKEN)

req = requests.get('https://cbr.ru/')
soup = BeautifulSoup(req.text, 'html.parser')
allNews = soup.findAll('div', class_='main-indicator_rates-table')
data = soup.findAll('div', class_='col-md-2 col-xs-9 _right mono-num')
usd, eur, cny = [
    float(re.search(r'(\d+,?\d*)\s*₽', str(data[i * 2])).group(1).replace(',', '.'))
    for i in range(3)
]


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/start":

        keyboard = types.InlineKeyboardMarkup()
        key_yes = types.InlineKeyboardButton(text='Доллар', callback_data='usd')
        keyboard.add(key_yes)
        key_no = types.InlineKeyboardButton(text='Евро', callback_data='eur')
        keyboard.add(key_no)
        key_no = types.InlineKeyboardButton(text='Юань', callback_data='cny')
        keyboard.add(key_no)
        bot.send_message(message.from_user.id,
                         "Вас приветствует бот, который поможет вам в конвертации валют!\nВыберите валюту!",
                         reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /start.")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data not in ('usd', 'eur', 'cny'):
        bot.send_message(call.message.chat.id, 'Не удалось обработать валюту!')
    req = requests.get('https://cbr.ru/')
    soup = BeautifulSoup(req.text, "html.parser")
    data = soup.findAll('div', class_='col-md-2 col-xs-9 _right mono-num')
    if len(data) != 6:
        bot.send_message(call.message.chat.id, 'Не удалось обработать команду!')
    helper = {'usd': [0, "доллар", 1], 'eur': [2, "евро", 1], 'cny': [4, "юань", 1]}[call.data]
    info = str(data[helper[0]])

    value = float(re.search(r'(\d+,?\d*)\s*₽', info).group(1).replace(',', '.')) / helper[2]
    bot.send_message(call.message.chat.id, f'Сегодня один {helper[1]} стоит {value} рублей.')


bot.polling(none_stop=True, interval=0)
