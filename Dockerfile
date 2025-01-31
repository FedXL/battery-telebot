FROM python:3.12-alpine3.21
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY req.txt .
RUN pip install --no-cache-dir -r req.txt
COPY ./aiogram-bot /app
CMD ["python", "run_bot.py"]