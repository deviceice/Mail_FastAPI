#! /bin/bash
cd /mail
gunicorn main:app --workers 4 --worker-class gunicorn.workers.UnicormWorker --bind 0.0.0.0:8000

