import websocket
import json
import base64

def on_message(ws, message):
    try:
        data = json.loads(message)
        print("Получено новое письмо:", data)
    except Exception as e:
        print("Ошибка при разборе сообщения:", e)

def on_error(ws, error):
    print("Ошибка WebSocket:", error)

def on_close(ws, close_status_code, close_msg):
    print("Соединение закрыто")

def on_open(ws):
    print("Подключено к WebSocket. Ожидание новых писем...")

if __name__ == "__main__":
    ws_url = "ws://127.0.0.1:8001/ws/imap_new_mails"

    # Логин и пароль
    username = "user"
    password = "12345678"

    # Кодируем в base64 для заголовка Basic Auth
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    auth_header = f"Authorization: Basic {encoded_credentials}"

    ws = websocket.WebSocketApp(
        ws_url,
        header=[auth_header],  # Вот тут передаем заголовок
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever()
