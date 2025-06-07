import sys
import pam
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()
if sys.platform == "win32":
    # Заглушка для Windows — всегда "авторизуем" пользователя
    users = ['user', 'user1', 'user2', 'user3', 'user4', 'user5', 'user6', 'user7', 'user8', 'user9', 'user10',
             'user11','user12','user13','user14','user15','user16','user17','user18','user19','user20',
             'user21','user22','user23','user24','user25','user26','user27','user28','user29','user30',]


    async def pam_auth(credentials: HTTPBasicCredentials = Depends(security)):
        if credentials.username not in users or credentials.password != "12345678":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неправильный логин или пароль",
                headers={"WWW-Authenticate": 'Basic realm="Secure Area"'},
            )
        return credentials.username
else:
    p = pam.pam()


    async def pam_auth(credentials: HTTPBasicCredentials = Depends(security)):
        if not p.authenticate(credentials.username, credentials.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": 'Basic realm="Secure Area"'},
            )
        return credentials.username
