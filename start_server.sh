#! /bin/sh
# Временное решение
cd /var/www/fastapi_mail/app/
export CPPFLAGS="-I/opt/rubin/openssl/include"
export LDFLAGS="-L/opt/rubin/openssl/lib"
export LD_LIBRARY_PATH="/opt/rubin/openssl/lib:$LD_LIBRARY_PATH"
#/opt/rubin/bin/uvicorn main:app --uds /run/fastapi.sock
/opt/rubin/python39/bin/uvicorn main:app --host 0.0.0.0 --port $1 --workers 4

#gunicorn main:app --workers 4 --worker-class gunicorn.workers.UnicormWorker --bind 0.0.0.0:8000

