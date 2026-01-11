# Используем полную версию Python (в ней есть все нужные инструменты для сборки)
FROM python:3.13

# Устанавливаем переменные окружения, чтобы Python не тупил в контейнере
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Создаем рабочую папку
WORKDIR /app

# Сначала копируем только требования, чтобы Docker закешировал установку библиотек
COPY requirements.txt /app/

# Устанавливаем библиотеки (теперь точно должно пройти)
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . /app/

# Открываем порт
EXPOSE 8000

# Команда для запуска
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]