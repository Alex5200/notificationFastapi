## ▶️ Запуск локально

Убедитесь, что у вас установлен Python 3.12+.

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск приложения
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
# Сборка образа
docker build -t notification-fastapi .

# Запуск контейнера
docker run -p 8000:8000 notification-fastapi

## ✅ Чек-лист перед отправкой
- [x]  Docker-контейнер собирается и запускается.
- [x] API работает асинхронно (клиент не ждет секунду при отправке Email).
- [x] Работает фильтрация в GET запросе.
- [ ] Написаны тесты.