# Zadania 4 i 6: serwer HTTP z wynikami, sprawdzający przy starcie usługę train
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /srv
# tylko biblioteka standardowa, więc bez requirements.txt
COPY serve.py .
EXPOSE 8080
CMD ["python", "serve.py"]
