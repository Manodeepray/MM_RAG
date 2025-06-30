#!bin/bash/

uvicorn server:app --reload &

python frontend/app.py 

wait