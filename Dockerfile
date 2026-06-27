FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    xvfb \
    pulseaudio \
    ffmpeg \
    chromium \
    chromium-driver \
    xdotool \
    && rm -rf /var/lib/apt/lists/*

RUN pip install selenium xvfbwrapper


WORKDIR /app
COPY recorder.py /app/

CMD ["python", "recorder.py"]