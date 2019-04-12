import logging
import smtplib
import ssl
import string
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

import os
import re
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials

from config.config import Config as config

PRINTABLE_CHARS = set(string.printable)

formatter = logging.Formatter(config.LOG_FORMAT)
handler = logging.FileHandler(config.LOG_FILE)
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def download_file():
    credentials = Credentials.from_service_account_file(config.CREDENTIALS_FILE).with_scopes([config.SCOPE])
    session = AuthorizedSession(credentials)
    response = session.get(config.DOCUMENT_URL)
    raw_text = response.content.decode(response.encoding)
    doc_body = ''.join(re.findall(r'"s":"(.*?)"', raw_text)).strip()
    doc_body = doc_body.encode().decode('unicode_escape')
    doc_content = "".join(filter(lambda char: char in PRINTABLE_CHARS, doc_body))
    if not doc_content:
        raise ConnectionError(raw_text)

    time_str = datetime.now().strftime(config.DATE_FORMAT)
    new_file_name = config.TMP_DIR / f'{time_str}.txt'
    with open(new_file_name, 'w+') as file:
        file.write(doc_content)

    return new_file_name


def remove_stale_files(tmp_files):
    latest_file_name = get_latest_prev_file(tmp_files).name
    for file_name in filter(lambda name: not name == latest_file_name, tmp_files):
        os.remove(config.TMP_DIR / file_name)


def extract_date(file_name):
    """file name should be in a format: 05_04_2019_00_17_50.txt"""
    date_str = file_name[0: file_name.find('.')]
    return datetime.strptime(date_str, config.DATE_FORMAT)


def get_latest_prev_file(file_names):
    if not file_names:
        return None

    date_file_name_dict = dict((extract_date(name), name) for name in file_names)
    file_name = date_file_name_dict.get(max(date_file_name_dict.keys()))
    if file_name:
        return config.TMP_DIR / file_name

    return None


def parse_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        return re.findall(r'(LDN.*?\n{2})', content, flags=re.MULTILINE | re.DOTALL)


def get_tasks_diff(prev_file_path, new_file_path):
    prev_tasks = parse_file(prev_file_path)
    new_tasks = parse_file(new_file_path)
    return [new_task for new_task in new_tasks if new_task not in prev_tasks]


def send_notification(text):
    message = EmailMessage()
    message['From'] = config.EMAIL_SENDER
    message['To'] = config.EMAIL_RECEIVER
    message['Subject'] = config.EMAIL_SUBJECT
    message.set_content(text)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT, context=context) as server:
        server.login(config.EMAIL_SENDER, config.EMAIL_PASSWORD)
        server.sendmail(config.EMAIL_SENDER, config.EMAIL_RECEIVER, message.as_string())


def main():
    # noinspection PyBroadException
    try:
        tmp_dir = Path(config.TMP_DIR)
        if not tmp_dir.exists():
            os.mkdir(tmp_dir)

        tmp_files_names = os.listdir(tmp_dir)
        if len(tmp_files_names) > config.TMP_FILES_NUMBER_LIMIT:
            remove_stale_files(tmp_files_names)

        prev_file_path = get_latest_prev_file(tmp_files_names)
        new_file_path = download_file()

        if not prev_file_path or not new_file_path:
            return

        diff_tasks = get_tasks_diff(prev_file_path, new_file_path)
        if diff_tasks:
            email_text = f'{config.DOCUMENT_URL}\n\n'
            email_text += ''.join(diff_tasks)
            send_notification(email_text)
        else:
            os.remove(new_file_path)

    except Exception as e:
        print(str(e))
        logger.exception(f'Error: {str(e)}')


if __name__ == '__main__':
    main()
