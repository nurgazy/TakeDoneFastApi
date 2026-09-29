# Используем легковесный образ Python 3.13
FROM python:3.13-slim

# Отключаем запись байткода (.pyc) и буферизацию логов для вывода в реальном времени
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Задаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем системные утилиты и зависимости компилятора,
# необходимые для сборки пакетов bcrypt и cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем сначала только список зависимостей, чтобы Docker кэшировал слой с pip install
COPY requirements.txt .

# Устанавливаем библиотеки без сохранения кэша pip (уменьшает вес образа)
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код проекта в контейнер
COPY . .

# Открываем порт 8000 для входящих запросов
EXPOSE 8008

# Запускаем приложение через uvicorn, обязательно слушая 0.0.0.0
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8008"]