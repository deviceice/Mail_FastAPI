from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

from mail.imap_smtp_connect.imap_connection import get_imap_connection, get_imap_connection_ws
from mail.utils_func_API import *

api_ws = APIRouter(prefix="/ws")


@api_ws.websocket("/imap_new_mails")
async def websocket_imap(websocket: WebSocket,
                         ):
    """WebSocket-эндпоинт для получения новых писем в реальном времени"""
    # await websocket.accept()
    gen = get_imap_connection_ws(websocket)
    try:
        imap = await gen.__anext__()
    except StopAsyncIteration:
        return
    except WebSocketDisconnect as e:
        logger.info(f"WebSocket disconnected: {e.code}, reason: {e.reason}")
        return
    connection_active = True
    try:
        await imap.select("INBOX")
        await imap.idle_start()
        while connection_active:
            try:
                # Создаем задачи для ожидания IMAP и закрытия WebSocket
                imap_task = asyncio.create_task(imap.wait_server_push())
                close_task = asyncio.create_task(websocket.receive())
                done, pending = await asyncio.wait(
                    {imap_task, close_task},
                    return_when=asyncio.FIRST_COMPLETED
                )
                for task in pending:
                    task.cancel()

                if imap_task in done:
                    response = imap_task.result()
                    if response and b'EXISTS' in response[0]:
                        latest_uid = str(response[0].decode().split()[0])
                        try:
                            await websocket.send_json(latest_uid)
                        except (WebSocketDisconnect, RuntimeError):
                            connection_active = False
                            break

                if close_task in done:
                    connection_active = False
                    break

            except asyncio.CancelledError:
                break
            except Exception as e:
                # print(f"IMAP Error: {e}")
                await websocket.send_json({"error": str(e)})
                break

    except WebSocketDisconnect:
        pass
        # print("WebSocket Disconnect")
    except Exception as e:
        pass
        # print(f"Unexpected error: {e}")
    finally:
        # print('Stopping IMAP idle')
        try:
            if 'imap' in locals() and imap:
                imap.idle_done()
        except Exception as e:
            pass
            # print(f"Error closing IMAP: {e}")

        try:
            if (websocket.application_state != WebSocketState.DISCONNECTED and
                    websocket.client_state != WebSocketState.DISCONNECTED):
                await websocket.close()
        except Exception as e:
            pass
            # print(f"Error closing WebSocket: {e}")
