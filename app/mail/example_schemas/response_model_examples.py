get_mails_response_example = {
    200: {
        "description": "Пример с несколькими письмами",
        "content": {
            "application/json": {
                'example': {
                    "status": True,
                    "total_message": 235,
                    "folders": [
                        "Trash",
                        "АРХИВ",
                        "Sent",
                        "Важное",
                        "Drafts",
                        "INBOX"
                    ],
                    "emails": [
                        {
                            "uid": "967",
                            "message_id": "a28f777575be3a9440bcf61250d32b4a@mail.palas",
                            "from": "user@mail.palas",
                            "to": ["user@mail.palas"],
                            "subject": "3 files",
                            "date": "Fri, 14 Mar 2025 12:51:11 +0300",
                            "is_read": False,
                            "flags": True,
                            "attachments": [
                                {
                                    "filename": "bespreryivnyiy-gulkiy-shum-eduschego-avtomobilya.mp3",
                                    "size": "126.78 KB"
                                },
                                {
                                    "filename": "bespreryivnyiy.mp3",
                                    "size": "34.72 MB"
                                },
                            ],
                            "mails_referance": [
                                {
                                    "uid": "975",
                                    "message_id": "bf75b69ec6546344be86c2aba0a4be56@mail.palas",
                                    "from": "user@mail.palas",
                                    "to": ["user@mail.palas", "user1@mail.palas", "user2@mail.palas"],
                                    "subject": "Ответ:1",
                                    "date": "Fri, 14 Mar 2025 12:28:47 +0300",
                                    "is_read": False,
                                    "flags": False,
                                    "attachments": [
                                        {
                                            "filename": "sources.list",
                                            "size": "198 Bytes"
                                        }
                                    ]
                                },
                                {
                                    "uid": "976",
                                    "message_id": "a28f777575bfgf9440bcf61250d123b4a@mail.palas",
                                    "from": "user@mail.palas",
                                    "to": ["user@mail.palas"],
                                    "subject": "Ответ 2",
                                    "date": "Fri, 14 Mar 2025 12:54:11 +0300",
                                    "is_read": True,
                                    "flags": False,
                                    "attachments": []
                                },
                            ],
                        },
                        {
                            "uid": "968",
                            "message_id": "bf75b69ec6546344be86c2aba0a4be26@mail.palas",
                            "from": "user@mail.palas",
                            "to": ["user@mail.palas", "user1@mail.palas", "user2@mail.palas"],
                            "subject": "2 files",
                            "date": "Fri, 14 Mar 2025 12:28:47 +0300",
                            "is_read": False,
                            "mails_referance": [],
                            "flags": False,
                            "attachments": [
                                {
                                    "filename": "sources.list",
                                    "size": "198 Bytes"
                                }
                            ]
                        },
                        {
                            "uid": "969",
                            "message_id": "a28f777575bfgf9440bcf61250d32b4a@mail.palas",
                            "from": "user@mail.palas",
                            "to": ["user@mail.palas"],
                            "subject": "0 files",
                            "date": "Fri, 14 Mar 2025 12:54:11 +0300",
                            "is_read": True,
                            "mails_referance": [],
                            "flags": False,
                            "attachments": []
                        },
                    ]

                }

            }
        }
    },
    404: {
        "description": "Если не найдена Папка в почтовом ящике",
        "content": {
            "application/json": {
                'example': {'message': "Папка не найдена в почтовом ящике"}
            }
        }
    },
    401: {
        "description": "Не прошла авторизация",
        "content": {
            "application/json": {
                'example': {'message': "Не правильный логин или пароль"}
            }
        }
    },
    429: {
        "description": "Превышено кол-во запросов к IMAP серверу",
        "content": {
            "application/json": {
                'example': {'message': "Превышено кол-во запросов к IMAP серверу"}
            }
        }
    },
    504: {
        "description": "Проблемы с IMAP сервером",
        "content": {
            "application/json": {
                'example': {'message': "Сервер IMAP не ответил"}
            }
        }
    }
}
body_message_response_example = {
    200: {
        "description": "Ответа на получение тела письма",
        "content": {
            "application/json": {
                'example': {
                    "status": True,
                    "uid": "989",
                    "from": "user@mail.palas",
                    "to": ["user@mail.palas"],
                    "subject": "Присылаю вам файл",
                    "date": "Sat, 15 Mar 2025 15:24:54 +0300",
                    "body": "Отправляю файл sources.list посмотрите",
                    "attachments": [
                        {
                            "filename": "sources.list",
                            "size": "198 Bytes"
                        },
                        {
                            "filename": "sources2.list",
                            "size": "198 Bytes"
                        }
                    ]
                }
            }
        }
    },
    404: {
        "description": "Если не найдена Папка в почтовом ящике",
        "content": {
            "application/json": {
                "examples": {
                    "Папка не найдена": {
                        "value": {
                            "message": "Папка NAME не найдена в почтовом ящике"
                        }
                    },
                    "Письмо не найдено": {
                        "value": {
                            "message": "Письмо не найдено с таким UID = 942"
                        }
                    }
                }
            }
        }
    },
    401: {
        "description": "Не прошла авторизация",
        "content": {
            "application/json": {
                'example': {'message': "Не правильный логин или пароль"}
            }
        }
    },
    429: {
        "description": "Превышено кол-во запросов к IMAP серверу",
        "content": {
            "application/json": {
                'example': {'message': "Превышено кол-во запросов к IMAP серверу"}
            }
        }
    },
    504: {
        "description": "Проблемы с IMAP сервером",
        "content": {
            "application/json": {
                'example': {'message': "Сервер IMAP не ответил"}
            }
        }
    }
}
get_folders_response_example = {
    200: {
        "description": "Ответ на получения названия всех папок в почтовом ящике",
        "content": {
            "application/json": {
                'example': {
                    "status": True,
                    "folders": [
                        "Trash",
                        "АРХИВ",
                        "Sent",
                        "Важное",
                        "Drafts",
                        "INBOX"
                    ]
                }
            }
        }
    },
    401: {
        "description": "Не прошла авторизация",
        "content": {
            "application/json": {
                'example': {'message': "Не правильный логин или пароль"}
            }
        }
    },
    429: {
        "description": "Превышено кол-во запросов к IMAP серверу",
        "content": {
            "application/json": {
                'example': {'message': "Превышено кол-во запросов к IMAP серверу"}
            }
        }
    },
    504: {
        "description": "Проблемы с IMAP сервером",
        "content": {
            "application/json": {
                'example': {'message': "Сервер IMAP не ответил"}
            }
        }
    }
}
create_folder_response_example = {
    200: {
        "description": "Ответ на создание папки в почтовом ящике",
        "content": {
            "application/json": {
                "examples": {
                    "example1": {
                        "summary": "Пример успешного ответа",
                        "value": {
                            "status": True,
                            "message": "Папка NAME успешно создана"
                        }
                    },
                    "example2": {
                        "summary": "Пример если папка не создалась",
                        "value": {
                            "status": False,
                            "message": "Не удалось создать папку NAME"
                        }
                    }
                }
            }
        }
    },
    401: {
        "description": "Не прошла авторизация",
        "content": {
            "application/json": {
                'example': {'message': "Не правильный логин или пароль"}
            }
        }
    },
    429: {
        "description": "Превышено кол-во запросов к IMAP серверу",
        "content": {
            "application/json": {
                'example': {'message': "Превышено кол-во запросов к IMAP серверу"}
            }
        }
    },
    504: {
        "description": "Проблемы с IMAP сервером",
        "content": {
            "application/json": {
                "example": {
                    "message": "Сервер IMAP не ответил"
                }
            }
        }
    }
}
delete_folder_response_example = {
    200: {
        "description": "Ответ на создание папки в почтовом ящике",
        "content": {
            "application/json": {
                "examples": {
                    "example1": {
                        "summary": "Пример успешного ответа",
                        "value": {
                            "status": True,
                            "message": "Папка NAME успешно удалена"
                        }
                    },
                    "example2": {
                        "summary": "Пример если папка не создалась",
                        "value": {
                            "status": False,
                            "message": "Не удалось удалить папку NAME"
                        }
                    }
                }
            }
        }
    },
    401: {
        "description": "Не прошла авторизация",
        "content": {
            "application/json": {
                'example': {'message': "Не правильный логин или пароль"}
            }
        }
    },
    429: {
        "description": "Превышено кол-во запросов к IMAP серверу",
        "content": {
            "application/json": {
                'example': {'message': "Превышено кол-во запросов к IMAP серверу"}
            }
        }
    },
    504: {
        "description": "Проблемы с IMAP сервером",
        "content": {
            "application/json": {
                "example": {
                    "message": "Сервер IMAP не ответил"
                }
            }
        }
    }
}
rename_folder_response_example = {
    200: {
        "description": "Ответ на изменения названия папки в почтовом ящике",
        "content": {
            "application/json": {
                "examples": {
                    "example1": {
                        "summary": "Пример успешного ответа",
                        "value": {
                            "status": True,
                            "message": "Папка old_NAME успешно переименована в new_NAME"
                        }
                    },
                    "example2": {
                        "summary": "Пример если папку не удалось переименовать",
                        "value": {
                            "status": False,
                            "message": "Не удалось переименовать папку old_NAME"
                        }
                    }
                }
            }
        }
    },
    401: {
        "description": "Не прошла авторизация",
        "content": {
            "application/json": {
                'example': {'message': "Не правильный логин или пароль"}
            }
        }
    },
    429: {
        "description": "Превышено кол-во запросов к IMAP серверу",
        "content": {
            "application/json": {
                'example': {'message': "Превышено кол-во запросов к IMAP серверу"}
            }
        }
    },
    504: {
        "description": "Проблемы с IMAP сервером",
        "content": {
            "application/json": {
                "example": {
                    "message": "Сервер IMAP не ответил"
                }
            }
        }
    }
}
status_folder_response_example = {
    200: {
        "description": "Ответ на получение статуса папки",
        "content": {
            "application/json": {
                "example": {
                    'messages': 21,
                    'recent': 0,
                    'unseen': 3
                }
            }
        }

    },
    401: {
        "description": "Не прошла авторизация",
        "content": {
            "application/json": {
                'example': {'message': "Не правильный логин или пароль"}
            }
        }
    },
    404: {
        "description": "Если не найдена Папка в почтовом ящике",
        "content": {
            "application/json": {
                'example': {'message': "Папка не найдена в почтовом ящике"}
            }
        }
    },
    429: {
        "description": "Превышено кол-во запросов к IMAP серверу",
        "content": {
            "application/json": {
                'example': {'message': "Превышено кол-во запросов к IMAP серверу"}
            }
        }
    },
    504: {
        "description": "Проблемы с IMAP сервером",
        "content": {
            "application/json": {
                "example": {
                    "message": "Сервер IMAP не ответил"
                }
            }
        }
    }
}
status_flags_response_example = {
    200: {
        "description": "Ответ на получение статуса изменение флагов",
        "content": {
            "application/json": {
                "example": {
                    'status': True,
                }
            }
        }

    },
    401: {
        "description": "Не прошла авторизация",
        "content": {
            "application/json": {
                'example': {'message': "Не правильный логин или пароль"}
            }
        }
    },
    404: {
        "description": "Если не найдена Папка в почтовом ящике",
        "content": {
            "application/json": {
                'example': {'message': "Папка не найдена в почтовом ящике"}
            }
        }
    },
    429: {
        "description": "Превышено кол-во запросов к IMAP серверу",
        "content": {
            "application/json": {
                'example': {'message': "Превышено кол-во запросов к IMAP серверу"}
            }
        }
    },
    504: {
        "description": "Проблемы с IMAP сервером",
        "content": {
            "application/json": {
                "example": {
                    "message": "Сервер IMAP не ответил"
                }
            }
        }
    }
}
