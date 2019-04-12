from pathlib import Path


class Config:
    APP_DIR = Path(__file__).resolve().parent.parent
    CONFIG_DIR = APP_DIR / 'config'
    TMP_DIR = APP_DIR / 'tmp'

    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = APP_DIR / 'scraper.log'

    CREDENTIALS_FILE = CONFIG_DIR / 'credentials.json'
    SCOPE = 'https://www.googleapis.com/auth/documents.readonly'
    DOCUMENT_ID = ''
    DOCUMENT_URL = f'https://docs.google.com/document/d/{DOCUMENT_ID}/preview'

    DATE_FORMAT = '%d_%m_%Y_%H_%M_%S'

    CHECK_TIMEOUT = 60
    TMP_FILES_NUMBER_LIMIT = 10

    EMAIL_SUBJECT = 'New updates on IKEA tasks page.'
    EMAIL_RECEIVER = ''

    EMAIL_SENDER = ''
    EMAIL_PASSWORD = ''
    SMTP_SERVER = 'smtp.gmail.com'

    SMTP_PORT = '465'
