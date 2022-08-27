# Bezug von Docker Basis-Image
FROM python:3.9.13-slim-buster

# Ordner der Webapplikation
WORKDIR /app

# Kopieren der Liste mit allen abhängigen Erweiterungen
COPY requirements.txt requirements.txt

# pip auf den neusten Stand aktualisieren
RUN pip3 install --upgrade pip

# Installieren aller abhängigen Erweiterungen
RUN pip3 install -r requirements.txt

# Kopieren aller Dateien der Webanwendung
COPY . .

RUN export FLASK_APP=tima.py

RUN apt-get update
RUN apt-get install mariadb-client-10.3 -y

# Starten der Webanwendung
CMD [ "flask", "run", "-h", "0.0.0.0" ]
