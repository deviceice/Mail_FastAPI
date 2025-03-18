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
    504: {
        "description": "Проблемы с IMAP сервером",
        "content": {
            "application/json": {
                'example': {'message': "Сервер IMAP не ответил"}
            }
        }
    }
}
