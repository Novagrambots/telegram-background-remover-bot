FROM python:3.12-slim

# Минимальные системные зависимости для rembg + onnxruntime
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libgl1 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Сначала зависимости (кэшируется Docker слоем)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Предзагрузка поддерживаемых моделей (~176 МБ каждая) в /root/.u2net/
RUN python -c "from rembg import new_session; [new_session(m) for m in ['u2net', 'isnet-general-use']]"

# Потом код
COPY bot/ bot/

CMD ["python", "-m", "bot.main"]
