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
                            "referance": '',
                            "attachments": []
                        }
                    },
                    "example2": {
                        "summary": "Пример с 2 файлами ",
                        "value": {
                            "to": "user@mail.palas",
                            "subject": "Присылаю вам файл",
                            "body": "Отправляю файл sources.list посмотрите",
                            "referance": '',
                            "attachments": [{
                                "filename": "sources.list",
                                "file": "I2RlYiBjZHJvbTpbT1MgQXN0cmEgTGludXggMS41IHNtb2xlbnNrIC0gYW1kNjQgRFZEIF0vIHNtb2xlbnNrIGNvbnRyaWIgbWFpbiBub24tZnJlZSAKCmRlYiBmaWxlOi8vL3JlcGEvZGlzazEvIHNtb2xlbnNrIGNvbnRyaWIgbWFpbiBub24tZnJlZQpkZWIgZmlsZTovLy9yZXBhL2Rpc2syLyBzbW9sZW5zayBjb250cmliIG1haW4gbm9uLWZyZWUK"
                            },
                                {
                                    "filename": "sources2.list",
                                    "file": "I2RlYiBjZHJvbTpbT1MgQXN0cmEgTGludXggMS41IHNtb2xlbnNrIC0gYW1kNjQgRFZEIF0vIHNtb2xlbnNrIGNvbnRyaWIgbWFpbiBub24tZnJlZSAKCmRlYiBmaWxlOi8vL3JlcGEvZGlzazEvIHNtb2xlbnNrIGNvbnRyaWIgbWFpbiBub24tZnJlZQpkZWIgZmlsZTovLy9yZXBhL2Rpc2syLyBzbW9sZW5zayBjb250cmliIG1haW4gbm9uLWZyZWUK"
                                }]
                        }
                    },
                    "example3": {
                        "summary": "Пример письма на несколько почтовых ящиков ",
                        "value": {
                            "to": ["user@mail.palas", "user1@mail.palas", "user2@mail.palas"],
                            "subject": "Пример письма на несколько почтовых ящиков",
                            "body": "Отправляю письмо посмотрите",
                            "referance": '',
                            "attachments": []
                        }
                    },
                    "example4": {
                        "summary": "Пример Ответа на письмо ",
                        "value": {
                            "to": "user@mail.palas",
                            "subject": "Ответ: Привет",
                            "body": "Отправляю письмо посмотрите",
                            "referance": "a28f777575be3a9440bcf61250d32b4a@mail.palas",
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
