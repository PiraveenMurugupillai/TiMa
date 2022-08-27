# Praxisarbeit – VCID.IA1A.PA

## Lokaler Start der Applikation

Um die Applikation lokal zu starten, benötigen Sie Docker Desktop bzw. `docker-compose`. \
Starten Sie die Applikation mit folgendem Befehl in Ihrem Terminal:
```shell
docker-compose up
```

## Allgemeine Info

Dieses Repository beinhaltet eine einfache Webanwendung programmiert in Python Flask mit einer Anbindung an eine relationale Datenbank MariaDB. Die Webanwendung wurde von mir selbst programmiert. Nicht von mir entwickelte beziehungsweise von anderen publizierten Code inspirierte Teile in diesem Projekt werden als solches gekennzeichnet und zu der jeweilgen Quelle verwiesen.

### Autor

Piraveen Murugupillai

## Technologien

Folgende Technologien kommen zum Einsatz in der Webanwendung:
- Programmiersprache: *Python*
- Web-Framework: *Flask*
- Datenbanksystem: *MariaDB*
- Containerisierung: *Docker bzw. docker-compose*
- Rendering der Webseiten: *Jinja2*
- Styling Bibliothek: *Bootstrap*

## Checkliste der Anforderungen

- [ ] interaktive Weboberfläche (Benutzereingaben, -verarbeitungen & -aktionen)
- [ ] Authentifizierung & Authorisierung mit Benutzernamen, E-Mail Adresse & Passwort
- [ ] Datenspeicherung in einer relationaler Datenbank
- [ ] Implementierung der Geschäftslogik
- [ ] mind. 1 Lesezugriff über RESTful Web-API
- [ ] Scripts zur automatisierten Bau & Inbetriebnahme der Webanwendung

## Web-API

### Modelle

#### Benutzer

*Definition:*

| Feld     | Typ    | Eigenschaften / Beschreibung                   |
|----------|--------|------------------------------------------------|
| id       | String | UUID, eindeutige Identifikation eines Nutzers  |
| username | String | Benutzername (Alias) des Nutzers (eindeutig)   |
| email    | String | E-Mail Adresse des Nutzers (eindeutig)         |
| password | String | Passwort des Benutzerkontos                    |

Dieses Modell ist in der Datenbank in der Tabelle *USERS* abgelegt.

*Beispiel:*
```json
{
  "id": "d82fdc20-17fe-11ed-baa1-0242ac110002",
  "username": "Pira",
  "email": "pira@veen.ch",
  "password": "secret"
}
```

#### Tweets

*Definition:*

| Feld     | Typ    | Eigenschaften / Beschreibung                                        |
|----------|--------|---------------------------------------------------------------------|
| id       | String | UUID, eindeutige Identifikation eines Tweets                        |
| user_id  | String | UUID, die eindeutige ID des Nutzers, welcher den Tweet erstellt hat |
| tweet    | String | Inhalt des Tweets mit maximal 200 Zeichen                           |
| creation | String | Zeitstempel der Erstellung des Tweets in ISO Format                 |

Dieses Modell ist in der Datenbank in der Tabelle *TWEETS* abgelegt.

*Beispiel:*
```json
{
  "id": "eeb17f34-17ff-11ed-8c97-0242ac110002",
  "user_id": "d82fdc20-17fe-11ed-baa1-0242ac110002",
  "tweet": "Hello World!",
  "creation": "2022-08-09T16:36:33.514731Z"
}
```

#### Likes

*Definition:*

| Feld     | Typ    | Eigenschaften / Beschreibung                                        |
|----------|--------|---------------------------------------------------------------------|
| id       | String | UUID, eindeutige Identifikation eines Tweets                        |
| tweet_id | String | UUID, die eindeutige ID des Tweets, welcher geliked wurde           |
| user_id  | String | UUID, die eindeutige ID des Nutzers, welcher den Tweet geliked hat  |

Dieses Modell ist in der Datenbank in der Tabelle *LIKES* abgelegt.

*Beispiel:*
```json
{
  "id": "33bb23f5-1802-11ed-bdd1-a46bb6241f89",
  "tweet_id": "eeb17f34-17ff-11ed-8c97-0242ac110002",
  "user_id": "d82fdc20-17fe-11ed-baa1-0242ac110002"
}
```

### Authentifizierung (Registration & Login)

| Path         | `/api/auth/register`                                                            |
|--------------|---------------------------------------------------------------------------------|
| Method       | POST                                                                            |
| Body         | `{ "email": <E-MAIL_ADDRESS>, "username": <USERNAME>, "password": <PASSWORD> }` |
| Example Body | `{ "email": "pira@veen.ch", "username": "Pira", "password": "secret" }`         |
| Responses    | 201 Created                                                                     |
|              | 409 Conflict                                                                    |

---

| Path         | `/api/auth/login   `                                 |
|--------------|------------------------------------------------------|
| Method       | POST                                                 |
| Body         | `{ "username": <USERNAME>, "password": <PASSWORD> }` |
| Example Body | `{ "username": "Pira", "password": "secret" }`       |
| Responses    | 200 OK                                               |
|              | 400 Bad Request                                      |

### Tweets

