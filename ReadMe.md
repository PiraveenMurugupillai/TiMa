# Praxisarbeit – VCID.IA1A.PA

## Anleitung zum Starten der Applikation

### Starten mit Docker
Am einfachsten lässt sich die Applikation über den Docker Desktop bzw. `docker-compose` starten.
Hierfür müssen Sie lediglich im Terminal bzw. Kommandozeile in diesen Ordner navigieren und den Docker Service starten mit:
```shell
docker-compose up -d
```
> Beachten Sie, dass die Applikation im Hintergrund gestartet wird und nicht direkt in der Konsole. Falls Sie bewusst die
> Applikation in der Konsole starten möchten, führen Sie den Befehl ohne `-d` aus: `docker-compose up`.

Die Applikation kann folgendermassen wieder beendet werden:
```shell
docker-compose down
```
> Falls Sie die Applikation ohne `-d` ausgeführt haben, drücken Sie CTRL + C auf Windows/Linux und CMD + C auf MacOS.

### Starten auf Windows

Falls Sie die Applikation ohne Unterstützung von Docker starten möchten, führen Sie folgende Befehle in 
Kommandozeile aus. Bitte beachten Sie auch hier, dass Sie sich im aktuellen Ordner befinden in der Konsole. 
Es wird davon ausgegangen, dass Sie [Python Version 3](https://www.python.org/downloads/) & [virtualenv](https://pypi.org/project/virtualenv/) installiert haben.
```shell
virtualenv venv
.\venv\Scripts\activate.bat # für Powershell bitte .\venv\Scripts\activate.ps1 ausführen
pip3 install -r requirements.txt

flask db init
flask db migrate -m "Initialize database"
flask db upgrade

set FLASK_APP=tima.py
flask run
```

### Starten auf MacOS oder Linux

Zum starten der Applikation, führen Sie folgende Schritte im Terminal durch. Vergewissern Sie sich, dass Sie in der Konsole 
in diesen Ordner navigiert sind. Es wird davon ausgegangen, dass Sie [Python Version 3](https://www.python.org/downloads/) & [virtualenv](https://pypi.org/project/virtualenv/) installiert haben.
```shell
virtualenv venv
source ./venv/bin/activate
pip3 install -r requirements.txt

flask db init
flask db migrate -m "Initialize database"
flask db upgrade

export FLASK_APP=tima.py
flask run
```

## Allgemeine Info

Dieses Repository beinhaltet eine einfache Webapplikation programmiert in Python Flask mit einer Anbindung an eine 
relationale Datenbank MariaDB. Die Webapplikation wurde von mir selbst programmiert. Gewisse Teile der Applikation wurden 
vom [Microblog](https://github.com/miguelgrinberg/microblog) von Miguel Grinberg übernommen. Es betrifft hauptsächlich 
die Struktur der Dateien und der Registrierung- & Login-Mechanismus.

### Autor

Piraveen Murugupillai

### Erreichbarkeit im Internet

Die Webapplikation ist für eine geraume Zeit öffentlich im Internet erreichbar unter dem URL [https://tima-webapp.tk](https://tima-webapp.tk).

### Repository vom Source Code

Der komplette Code befindet sich öffentlich zugänglich auf GitHub unter folgendem Repository: [https://github.com/PiraveenMurugupillai/TiMa](https://github.com/PiraveenMurugupillai/TiMa)

### Quellen

Teile der Applikation wurden inspiriert oder komplett von [MicroBlog](https://github.com/miguelgrinberg/microblog) entnommen.

## Technologien & Bibliotheken

Folgende Technologien kommen zum Einsatz in der Webanwendung:
- Programmiersprache: *[Python](https://www.python.org/)*
- Web-Framework: *[Flask](https://flask.palletsprojects.com/en/2.2.x/)*
- Datenbanksystem: *[MariaDB](https://mariadb.org/)*
- Containerisierung: *[Docker bzw. docker-compose](https://www.docker.com/)*
- Rendering der Webseiten: *[Jinja2](https://jinja.palletsprojects.com/en/3.1.x/)*
- Styling Bibliothek: *[Bootstrap](https://getbootstrap.com/)*
- Benutzte Icons: *[fontawesome](https://fontawesome.com/)*

## WebAPI

Die WebAPI ist eine Schnittstelle um HTTP Anfragen an den Webserver zu schicken und ggf. Daten zu laden. Die Webapplikation 
bietet derzeit APIs für folgende Szenarien:
- das Erstellen & Bearbeiten eines Nutzers
- Erstellen & Löschen eines Authentifizierung-Tokens
- Auslesen aller erfassten Arbeitsstunden
- Erstellen, Bearbeiten, Auslesen & Löschen erfasster Arbeitsstunden

Die Schnittstellen sind über den Pfad `/api/users`, `/api/working-hours` und `/api/tokens` erreichbar.

### Token API

#### Neuen Token erstellen

Base-Auth: `<USERNAME>:<PASSWORD>`
> Die Authentifizierungsdaten werden in der URL mitgegeben. Beispielsweise: `https://<USERNAME>:<PASSWORD>@tima-webapp.tk/api/tokens`

Pfad: `/api/tokens`

Methode: `POST`

Dieses Beispiel als `curl` Kommando:
```shell
curl https://TiMa:secret-12345@tima-webapp.tk/api/tokens -X POST
```

#### Token wiederrufen bzw. löschen

Pfad: `/api/tokens`

Methode: `DELETE`

Authorization im Header: `Authorization: Bearer <TOKEN>`
> Ersetzen Sie `<TOKEN>` durch Ihren eigenen Token.

Dieses Beispiel als `curl` Kommando:
```shell
curl https://tima-webapp.tk/api/tokens -X DELETE -H "Authorization: Bearer 62zNTEL/texJjlRyH5wo5KbtYDuUwvUM"
```


### Users API

#### Erstellen eines neuen Nutzers

Pfad: `/api/users`

Methode: `POST`

Content-Type im Header: `Content-Type: application/json`

Body als JSON:
```json
{
  "username": "TiMa",
  "email": "admin@tima.tk",
  "password": "secret-12345",
  "company": "Timapira",
  "job": "WebDev",
  "target_time": 8
}
```
> Ersetzen Sie die Beispielwerte im JSON mit Ihren eigenen.

Dieses Beispiel als `curl` Kommando:
```shell
curl https://tima-webapp.tk/api/users -X POST -H "Content-Type: application/json" -d "{\"username\": \"tima\", \"email\": \"admin@tima.tk\", \"password\": \"12345\", \"company\": \"TiMapira\", \"job\": \"WebDev\", \"target_time\": 8}"
```

#### Auslesen des Nutzer-Profils

Pfad: `/api/users`

Methode: `GET`

Authorization im Header: `Authorization: Bearer <TOKEN>`
> Ersetzen Sie `<TOKEN>` durch Ihren eigenen Token.

Dieses Beispiel als `curl` Kommando:
```shell
curl https://tima-webapp.tk/api/users -H "Authorization: Bearer 62zNTEL/texJjlRyH5wo5KbtYDuUwvUM"
```

#### Bearbeiten des Nutzer-Profils

Pfad: `/api/users`

Methode: `PUT`

Content-Type im Header: `Content-Type: application/json`

Authorization im Header: `Authorization: Bearer <TOKEN>`
> Ersetzen Sie `<TOKEN>` durch Ihren eigenen Token.

Body als JSON:
```json
{
  "username": "TiMa",
  "email": "admin@tima.tk",
  "password": "secret-12345",
  "company": "Timapira",
  "job": "WebDev",
  "target_time": 8
}
```
> Ersetzen Sie die Beispielwerte im JSON mit Ihren eigenen. Es müssen nicht alle Werte mitgegeben werden, nur jene, 
> welche geändert werden sollen.

Dieses Beispiel als `curl` Kommando:
```shell
curl https://tima-webapp.tk/api/users -X PUT -H "Authorization: Bearer 62zNTEL/texJjlRyH5wo5KbtYDuUwvUM" -H "Content-Type: application/json" -d "{\"company\":\"TiMapira Informatik AG\", \"job\":\"Webapplication Developer\"}"
```

### Arbeitsstunden API

#### Erfassen neuer Arbeitsstunden

Pfad: `/api/working-hours`

Methode: `POST`

Content-Type im Header: `Content-Type: application/json`

Authorization im Header: `Authorization: Bearer <TOKEN>`
> Ersetzen Sie `<TOKEN>` durch Ihren eigenen Token.

Body als JSON:
```json
{
  "date": "2022-09-02",
  "working_hours": 8.4,
  "comment": "TiMa Flask Applikation"
}
```
> Ersetzen Sie die Beispielwerte im JSON mit Ihren eigenen.
> Beachten Sie, dass das Datum im Format YYYY-MM-DD mitgegeben werden muss.

Dieses Beispiel als `curl` Kommando:
```shell
curl https://tima-webapp.tk/api/working-hours -X POST -H "Authorization: Bearer 62zNTEL/texJjlRyH5wo5KbtYDuUwvUM" -H "Content-Type: application/json" -d "{\"date\":\"2022-09-02\",\"working_hours\":\"8.4\",\"comment\":\"TiMa Flask Applikation\"}"
```

#### Auslesen aller bereits erfassen Arbeitsstunden

Pfad: `/api/working-hours`

Methode: `GET`

Authorization im Header: `Authorization: Bearer <TOKEN>`
> Ersetzen Sie `<TOKEN>` durch Ihren eigenen Token.

Dieses Beispiel als `curl` Kommando:
```shell
curl https://tima-webapp.tk/api/working-hours -H "Authorization: Bearer 62zNTEL/texJjlRyH5wo5KbtYDuUwvUM"
```

#### Auslesen einer bestimmten erfassten Arbeitsstunden mit dem ID

Pfad: `/api/working-hours/<ID>`
> Hier `<ID>` durch die ID der erfassten Arbeitsstunden ersetzen. Diese ID kann man herausfinden, indem man alle Einträge der 
> Arbeitsstunden lädt und die ID ausliest.

Methode: `GET`

Authorization im Header: `Authorization: Bearer <TOKEN>`
> Ersetzen Sie `<TOKEN>` durch Ihren eigenen Token.

Dieses Beispiel als `curl` Kommando:
```shell
curl https://tima-webapp.tk/api/working-hours/1 -H "Authorization: Bearer 62zNTEL/texJjlRyH5wo5KbtYDuUwvUM"
```

#### Bearbeiten einer bestimmten erfassten Arbeitsstunden

Pfad: `/api/working-hours/<ID>`
> Hier `<ID>` durch die ID der erfassten Arbeitsstunden ersetzen. Diese ID kann man herausfinden, indem man alle Einträge der
> Arbeitsstunden lädt und die ID ausliest.

Methode: `PUT`

Content-Type im Header: `Content-Type: application/json`

Authorization im Header: `Authorization: Bearer <TOKEN>`
> Ersetzen Sie `<TOKEN>` durch Ihren eigenen Token.

Body als JSON:
```json
{
  "working_hours": 9,
  "comment": "TiMa Dokumentation"
}
```
> Ersetzen Sie die Beispielwerte im JSON mit Ihren eigenen. Es kann nur der Kommentar bzw. die geleistete Arbeitsstunden bearbeitet werden.

Dieses Beispiel als `curl` Kommando:
```shell
curl https://tima-webapp.tk/api/working-hours/1 -X PUT -H "Authorization: Bearer 62zNTEL/texJjlRyH5wo5KbtYDuUwvUM" -H "Content-Type: application/json" -d "{\"working_hours\":9,\"comment\":\"TiMa Dokumentation\"}"
```

#### Löschen einer bestimmten erfassten Arbeitsstunden

Pfad: `/api/working-hours/<ID>`
> Hier `<ID>` durch die ID der erfassten Arbeitsstunden ersetzen. Diese ID kann man herausfinden, indem man alle Einträge der
> Arbeitsstunden lädt und die ID ausliest.

Methode: `DELETE`

Authorization im Header: `Authorization: Bearer <TOKEN>`
> Ersetzen Sie `<TOKEN>` durch Ihren eigenen Token.

Dieses Beispiel als `curl` Kommando:
```shell
curl https://tima-webapp.tk/api/working-hours/1 -X DELETE -H "Authorization: Bearer 62zNTEL/texJjlRyH5wo5KbtYDuUwvUM"
```


## Checkliste mit den Anforderungen der Praxisarbeit

- [x] interaktive Weboberfläche (Benutzereingaben, -verarbeitungen & -aktionen)
- [x] Authentifizierung & Authorisierung mit Benutzernamen, E-Mail Adresse & Passwort
- [x] Datenspeicherung in einer relationaler Datenbank
- [x] Implementierung der Geschäftslogik
- [x] mind. 1 Lesezugriff über RESTful Web-API
- [x] Scripts zur automatisierten Bau & Inbetriebnahme der Webanwendung