FROM python:3.11.4

RUN apt-get update && apt-get install sudo ffmpeg -y 

RUN sudo pip install flask openai google-cloud-secret-manager https://github.com/pyannote/pyannote-audio/archive/refs/heads/develop.zip pydub

COPY app.py /app.py

RUN mkdir -p /data/input && mkdir -p /data/output

CMD ["python", "/app.py"]