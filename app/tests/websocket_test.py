import websocket
import json


def on_message(ws, message):
    """Обработка входящих сообщений от сервера"""
    try:
        data = json.loads(message)
        print("Получено новое письмо:", data)
    except Exception as e:
        print("Ошибка при разборе сообщения:", e)


def on_error(ws, error):
    """Обработка ошибок"""
    print("Ошибка WebSocket:", error)


def on_close(ws, close_status_code, close_msg):
    """Действия при закрытии соединения"""
    print("Соединение закрыто")


def on_open(ws):
    """Действия при успешном подключении"""
    print("Подключено к WebSocket. Ожидание новых писем...")


if __name__ == "__main__":
    # URL вашего WebSocket-эндпоинта
    ws_url = "ws://127.0.0.1:8001/ws/imap_new_mails"  # Замените на ваш адрес, если нужно
    # ws_url = "ws://127.0.0.1:8001/ws/imap_inbox"  # Замените на ваш адрес, если нужно

    # Создаем WebSocket-клиент
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    # Запускаем бесконечный цикл прослушивания
    ws.run_forever()