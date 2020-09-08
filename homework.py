import os
import requests
import telegram
import time
from dotenv import load_dotenv

load_dotenv()
url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
proxy_url = os.getenv('proxy_url')
proxy = telegram.utils.request.Request(proxy_url=proxy_url)
bot = telegram.Bot(token=TELEGRAM_TOKEN, request=proxy)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise KeyError('Ошибка в homework_name')
    status = homework.get('status')
    if status is None:
        raise KeyError('Ошибка в status')
    if status not in ("approved", "rejected"):
        raise ValueError('Не найден в списке доступных')
    if status == "rejected":
        verdict = 'К сожалению в работе нашлись ошибки.'
    if status == "approved":
        verdict = ('Ревьюеру всё понравилось, '
                   'можно приступать к следующему уроку.')
    return ('У вас проверили работу '
            f'"{homework_name}"!\n\n {verdict}')


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    if current_timestamp is None:
        current_timestamp = int(time.time())
    params = {'from_date': current_timestamp}
    try:
        return requests.get(url, headers=headers, params=params).json()
    except requests.exceptions.ConnectionError as eee:
        return f'Инвалид {eee}'


def send_message(message):
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0])
                )
            current_timestamp = new_homework.get(
                'current_date')
            time.sleep(900)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
