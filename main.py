import smtplib
import requests
from email.mime.text import MIMEText
import time
import socket
import json

with open("user_data.json", "r", encoding="utf-8") as file:
    data = json.load(file)


# Конфигурация
CHECK_INTERVAL = 300  # Проверять каждые 5 минут (в секундах)
LAST_IP_FILE = 'last_ip.txt'  # Файл для хранения последнего IP
SMTP_SERVER = data["smtp_server"]
SMTP_PORT = 587  # Порт для SMTP (обычно 587 для TLS)
EMAIL_FROM = data["mail_from"]  # Ваша почта
EMAIL_TO = data["mail_to"]  # Почта для уведомлений
EMAIL_PASSWORD = data["mail_pass"]  # Пароль от почты (лучше использовать app-пароль)


def get_current_ip():
    try:
        # Используем внешний сервис для определения IP
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        if response.status_code == 200:
            return response.json()['ip']
    except:
        try:
            # Альтернативный способ, если основной сервис недоступен
            return requests.get('https://ident.me').text
        except:
            # Если вообще ничего не работает, попробуем локальный способ
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
    return None


def load_last_ip():
    try:
        with open(LAST_IP_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None


def save_last_ip(ip):
    with open(LAST_IP_FILE, 'w') as f:
        f.write(ip)


def send_email(new_ip):
    subject = f'Новый IP адрес: {new_ip}'
    body = f'Ваш новый внешний IP адрес: {new_ip}'

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, [EMAIL_TO], msg.as_string())
        print(f'Письмо с новым IP {new_ip} отправлено')
    except Exception as e:
        print(f'Ошибка при отправке письма: {e}')


def main():
    last_ip = load_last_ip()
    print(f'Текущий сохранённый IP: {last_ip}')

    while True:
        current_ip = get_current_ip()
        if current_ip:
            print(f'Текущий внешний IP: {current_ip}')

            if last_ip != current_ip:
                print(f'Обнаружено изменение IP: {last_ip} -> {current_ip}')
                send_email(current_ip)
                save_last_ip(current_ip)
                last_ip = current_ip
            else:
                print('IP не изменился')
        else:
            print('Не удалось определить текущий IP')

        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()