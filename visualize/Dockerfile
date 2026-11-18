# Zadanie 4: serwer HTTP wystawiający katalog z wynikami (models/ z wolumenu)
FROM python:3.11-slim
WORKDIR /srv
EXPOSE 8080
CMD ["python", "-m", "http.server", "8080", "--directory", "/srv/models"]
