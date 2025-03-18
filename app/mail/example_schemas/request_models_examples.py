# get_mails_request_example = {
#     "Parametrs": {
#         "content": {
#             "application/json": {
#                 "examples": {
#                     "example1": {
#                         "summary": "Пример с INBOX без last_uid",
#                         "value": {
#                             "mbox": "INBOX"
#                         }
#                     },
#                     "example2": {
#                         "summary": "Пример с INBOX и last_uid",
#                         "value": {
#                             "mbox": "INBOX",
#                             "last_uid": "243"
#                         }
#                     }
#                 }
#             }
#         }
#     }
# }

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
                            "subject": "Привет",
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
