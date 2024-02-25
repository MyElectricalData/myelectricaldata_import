# MyElectricalData

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield]

## Francais

### IMPORTANT

**EnedisGateway2MQTT** devient **MyElectricalData** et la dépendance à MQTT n'est plus obligatoire.

---

MyElectricalData est le client officiel de la plateforme [MyElectricaData](https://myelectricaldata.fr) qui va vous permettre de récupérer votre consommation depuis les API d'Enedis.

Toutes les données seront importées dans un cache local (SQLite) ou externe (PostgreSQL) qui pourrais ensuite être exporté vers :

- MQTT
- Home Assistant (Via l'auto-discovery MQTT)
- InfluxDB
- PostgresSQL

L'outil possède également des APIs.

### [Documentation / Wiki](https://github.com/m4dm4rtig4n/myelectricaldata/wiki/01.-Home)

Tout est disponible directement sur le [Wiki](https://github.com/m4dm4rtig4n/myelectricaldata/wiki/01.-Home) du projet.

---

#### Si vous souhaitez soutenir le projet ainsi que la passerelle

[![Donate][donation-badge]](https://www.buymeacoffee.com/m4dm4rtig4n)

[![Donate][donation-paypal]](https://www.paypal.me/m4dm4rtig4n)

[donation-badge]: https://img.shields.io/badge/Buy%20me%20a%20coffee-%23d32f2f?logo=buy-me-a-coffee&style=flat&logoColor=white
[donation-paypal]: https://www.appvizer.fr/media/application/1591/logo/logo-paypal.png

**Vous recherchez un Discord Francais autour de la "Domotique & Diy" ?**

[![https://discord.gg/DfVJZme](ressources/discord.png 'Vous recherchez un Discord Francais autour de la "Domotique & Diy" ?')](https://discord.gg/DfVJZme)

---

---

## English

> This tools is only for french user with electric meter Linky.

### IMPORTANT

**EnedisGateway2MQTT** became **MyElectricalData** and MQTT dependency isn't mandatory.

MyElectricalData is official client for gateway [MyElectricaData](https://myelectricaldata.fr) to import your electricity consumption from the officiel Enedis APIs.

All data are import in local cache (SQLite) or external backend (PostgreSQL) which could then be exported to:

- MQTT
- Home Assistant (auto-discovery MQTT)
- InfluxDB
- PostgresSQL

The tool also has APIs.

### [Documentation / Wiki](https://github.com/m4dm4rtig4n/myelectricaldata/wiki/01.-Home)

Available here [Wiki](https://github.com/m4dm4rtig4n/myelectricaldata/wiki/01.-Home) but only in french.

### If you want support project (Client & Gateway)

[![Donate][donation-badge]](https://www.buymeacoffee.com/m4dm4rtig4n)

[![Donate][donation-paypal]](https://www.paypal.me/m4dm4rtig4n)

**If you seek french discord community around Home Automation "Domotique & Diy" ?**

[![https://discord.gg/DfVJZme](ressources/discord.png 'Vous recherchez un Discord Francais autour de la "Domotique & Diy" ?')](https://discord.gg/DfVJZme)

---

### Liens / Link

- Github Repository : <https://github.com/m4dm4rtig4n/myelectricaldata>
- Docker Hub Images : <https://hub.docker.com/r/m4dm4rtig4n/myelectricaldata>
- Hassio Addons : <https://github.com/alexbelgium/hassio-addons/tree/master/myelectricaldata>
- Saniho Card for Home Assistant : <https://github.com/saniho/content-card-linky>
- Energy Home Assistant import script : <https://github.com/chocomega/statistics_importer>

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
