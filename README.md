<header>

<!--
  <<< Author notes: Course header >>>
  Include a 1280×640 image, course title in sentence case, and a concise description in emphasis.
  In your repository settings: enable template repository, add your 1280×640 social image, auto delete head branches.
  Add your open source license, GitHub uses MIT license.
-->

# Telegram Movie-Bot

_Ein Telegram Bot, welcher das Entdecken von neuen Filmen oder Serien vereinfachen soll._

</header>

## Materialien
Dieses Projekt ist mit einem Rapberry-PI 3 erstellt, funktioniert aber auf jedem Python-lauffähigen Gerät (hier Python3). Als Datenbank für die Filme und Serien wird die eine API zur TMDB (The Movie Database) verwendent.

## Schritt 1: Libraries installieren
Für die Schnittstelle zu Telegramm wird zunächst die Library telebot verwendet.
```
pip install telebot
```
Außerdem wird die [tmdbsimple](https://github.com/celiao/tmdbsimple) Library verwendet, um das Abfragen der Datenbank einfacher zu gestalten.
```
pip install tmdbsimple
```
Diese Library beruht auf [requests](https://requests.readthedocs.io/en/latest/) und wird dabei mit installiert.
<!--
PIL?
io?
random?
-->

## Schritt 2: Telegram Bot einrichten
Um eine Telegram Bot zu erstellen ist es am Einfachsten, dieser [Anleitung](https://core.telegram.org/bots/tutorial#obtain-your-bot-token) zu folgen.

In kurzform sind es folgende Schritte:
+ bei Telegram @BotFather eine Nachricht mit "/newbot" schreiben
+ den Anweisungen folgen
+ den erhaltenen Token kopieren, dieser wird in Schritt 4 benötigt

> [!TIP]
> Der Token sollte folgendes Format haben: _4839574812:AAFD39kkdpWt3ywyRZergyOLMaJhac60qc_

> [!NOTE]
> Der Name des Bots kann nicht verändert werden, dafür muss ein neuer Bot (mit neuem Token) angelegt werden.

## Schritt 3: API-Token von TMDB erhalten
Um einen eigenen API-Token von TMDB zu erhalten, muss dort zunächst ein [Account](https://www.themoviedb.org/signup) erstellt werden. 
Mit Login kann dann ein [API-Token](https://www.themoviedb.org/settings/api) angefragt werden. Diese Maske muss nun ausgefüllt werden, um den Token zu erhalten. Auch dieser Token wird in Schritt 4 benötigt.

> [!TIP]
> Bei der **Anwendungs-URL** kann ***not available*** eingetragen werden.

## Schritt 4: Programm mit API- und Bot-Token ausführen
Die Tokens aus Schritt 2 und 3 müssen noch in den Code eingefügt werden. Nun kann das Programm ausgeführt und getestet werden.

Für den einfacheren Umgang kann das Programm auch als Service ausgeführt werden, dies wird in Schritt 5 erklärt.

## Schritt 5 _(Optional)_: 

--> Service

<footer>

_Ein Projekt für die HAW-Hamburg im Kurs Paspberry-PI bei Dr. Claudius Noack_

</footer>
