from config import Settings


class SettingsServer:
    settings = Settings()
    settings.open_conf()
    config = settings.get_conf()
    SMTP_HOST = config['HOST_MAIL']['smtp_host']
    SMTP_PORT = int(config['HOST_MAIL']['smtp_port'])
    IMAP_HOST = config['HOST_MAIL']['imap_host']
    IMAP_PORT = int(config['HOST_MAIL']['imap_port'])
    DOMAIN_DEFAULT = config['HOST_MAIL']['domain_default']

    DB_IP = config['DB_MAIL']['db_ip']
    DB_PORT = int(config['DB_MAIL']['db_port'])
    DB_PASS = config['DB_MAIL']['db_password']
    DB_USER = config['DB_MAIL']['db_user']
    DB_NAME = config['DB_MAIL']['db_name']

    REDIS_IP = config['DB_REDIS']['redis_ip']
    REDIS_PORT = config['DB_REDIS']['redis_port']
    REDIS_PASS = config['DB_REDIS']['redis_password']
    REDIS_MAXCONN = int(config['DB_REDIS']['redis_max_connection'])

