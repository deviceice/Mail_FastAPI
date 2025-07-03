send_mail_request_example = {
    "requestBody": {
        "content": {
            "application/json": {
                "examples": {
                    "example1": {
                        "summary": "Пример простого письма",
                        "value": {
                            "to": "user@mail.palas",
                            "subject": "Отправляю письмо посмотрите",
                            "body": "Отправляю письмо посмотрите",
                            "reference": '',
                            "attachments": []
                        }
                    },
                    "example2": {
                        "summary": "Пример с 2 файлами ",
                        "value": {
                            "to": "user@mail.palas",
                            "subject": "Присылаю вам файл",
                            "body": "Отправляю файл sources.list посмотрите",
                            "reference": '',
                            "attachments": [
                                {"filename": "09tr.tar", "uuid": "668c3935-4e98-4438-b7e6-3738c903a463"},
                                {"filename": "image.png", "uuid": "6862a706-663e-4d1c-aa08-782eb1846fc9"},]
                        }
                    },
                    "example3": {
                        "summary": "Пример письма на несколько почтовых ящиков ",
                        "value": {
                            "to": ["user@mail.palas", "user1@mail.palas", "user2@mail.palas"],
                            "subject": "Пример письма на несколько почтовых ящиков",
                            "body": "Отправляю письмо посмотрите",
                            "reference": '',
                            "attachments": []
                        }
                    },
                    "example4": {
                        "summary": "Пример Ответа на письмо ",
                        "value": {
                            "to": "user@mail.palas",
                            "subject": "Ответ: Привет",
                            "body": "Отправляю письмо посмотрите",
                            "reference": "a28f777575be3a9440bcf61250d32b4a@mail.palas",
                            "attachments": []
                        }
                    }

                }
            }
        }
    }
}
create_folder_request_example = {
    "requestBody": {
        "content": {
            "application/json": {
                "examples": {
                    "example1": {
                        "summary": "Пример создание папки в почтовом ящике",
                        "value": {
                            "name": "Архив",
                        }
                    }
                }
            }
        }
    }
}
delete_folder_request_example = {
    "requestBody": {
        "content": {
            "application/json": {
                "examples": {
                    "example1": {
                        "summary": "Пример удаления папки в почтовом ящике",
                        "value": {
                            "name": "Архив",
                        }
                    }
                }
            }
        }
    }
}
rename_folder_request_example = {
    "requestBody": {
        "content": {
            "application/json": {
                "examples": {
                    "example1": {
                        "summary": "Пример изменения названия папки в почтовом ящике",
                        "value": {
                            "old_name_mbox": "Архив",
                            "new_name_mbox": "Архив 2025"
                        }
                    }
                }
            }
        }
    }
}
move_mail_request_example = {
    "requestBody": {
        "content": {
            "application/json": {
                "examples": {
                    "example1": {
                        "summary": "Пример перемещения одного письма",
                        "value": {
                            "source_folder": "INBOX",
                            "target_folder": "АРХИВ",
                            "uid": "1051",
                        }
                    },
                    "example2": {
                        "summary": "Пример перемещения нескольких писем",
                        "value": {
                            "source_folder": "INBOX",
                            "target_folder": "АРХИВ",
                            "uid": ["1049", "1048"],
                        }
                    },

                }
            }
        }
    }
}
copy_mail_request_example = {
    "requestBody": {
        "content": {
            "application/json": {
                "examples": {
                    "example1": {
                        "summary": "Пример копирования одного письма",
                        "value": {
                            "source_folder": "INBOX",
                            "target_folder": "АРХИВ",
                            "uid": "1051",
                        }
                    },
                    "example2": {
                        "summary": "Пример копирования нескольких писем",
                        "value": {
                            "source_folder": "INBOX",
                            "target_folder": "АРХИВ",
                            "uid": ["1049", "1048"],
                        }
                    },

                }
            }
        }
    }
}
