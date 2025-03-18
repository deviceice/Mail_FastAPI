from config import Settings


class SettingsServer:
    settings = Settings()
    settings.open_conf()
    config = settings.get_conf()
    SMTP_IP = config['HOST_MAIL']['smtp_host']
    SMTP_PORT = int(config['HOST_MAIL']['smtp_port'])
    IMAP_IP = config['HOST_MAIL']['imap_host']
    IMAP_PORT = int(config['HOST_MAIL']['imap_port'])
