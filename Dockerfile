FROM python:3.10-bullseye

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt ./

RUN pip3 install --upgrade pip --no-cache-dir && pip3 install -r requirements.txt --no-cache-dir

COPY ./src ./


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
