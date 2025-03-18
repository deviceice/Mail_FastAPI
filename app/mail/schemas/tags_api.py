send_mail = {
    "to": "user@mail.palas",
    "subject": "Присылаю вам файл",
    "body": "Отправляю файл sources.list посмотрите",
    "attachments": [
        {
            "filename": "sources.list",
            "file": ""
        },
        {
            "filename": "sources.list",
            "file": ""
        }]
}

attachment = {
    "status": True,
    "uid": "740",
    "from": "user <user@mail.palas>",
    "subject": "filename",
    "date": "Thu, 13 Feb 2025 15:23:05 +0300",
    "body": "filename",
    "attachments": [
        {
            "filename": "Полезно для быстрого копирования.txt",
            "content_type": "text/plain",
            "size": 3703,
            "data": ""
        },
        {
            "filename": "Настройки config ПОЧТЫ полезные функции.txt",
            "content_type": "text/plain",
            "size": 1484,
            "data": ""
        }
    ]
}

tags_metadata = [
    {
        "name": "mails",
        "description": "Получение почты из папки",
    },
    {
        "name": "send_mail",
        "description": f"Отправить письмо или письма",
    },
    {
        "name": "get_folders",
        "description": "GET запрос на получение названий всех папок у пользователя",
    },
    {
        "name": "create_folder",
        "description": "Создать папку в почтовом ящике. Отправить {'mbox': 'Название папки'}",
    },
    {
        "name": "delete_folder",
        "description": "Удалить папку в почтовом ящике. Отправить {'mbox': 'Название папки'}",
    },
    {
        "name": "rename_folder",
        "description": "Сменить название папки в почтовом ящике. Отправить {'mbox': 'Название папки', 'new_box': 'Новое название'}",
    },
    {
        "name": "get_body_message",
        "description": f"Получить текст и вложения письма. Отправить 'mbox': 'Название папки', 'uid': 'uid СТРОКА!' Вернет {attachment}  ",
    },

]
