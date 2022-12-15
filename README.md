# MyElectricalData

[![Donate][donation-badge]](https://www.buymeacoffee.com/m4dm4rtig4n)

[donation-badge]: https://img.shields.io/badge/Buy%20me%20a%20coffee-%23d32f2f?logo=buy-me-a-coffee&style=flat&logoColor=white

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield]

**Vous recherchez un Discord Francais autour de la "Domotique & Diy" ?**

[![https://discord.gg/DfVJZme](ressources/discord.png 'Vous recherchez un Discord Francais autour de la "Domotique & Diy" ?')](https://discord.gg/DfVJZme)

****

## IMPORTANT !
**EnedisGateway2MQTT** devient **MyElectricalData** !

La dépendance à MQTT n'est plus obligatoire et je supporte :
- MQTT
- Home Assistant (Via MQTT Auto Discovery)
- InfluxDB

# Links

* Github Repository : https://github.com/m4dm4rtig4n/myelectricaldata
* Docker Hub Images : https://hub.docker.com/r/m4dm4rtig4n/myelectricaldata
* Hassio Addons : https://github.com/alexbelgium/hassio-addons/tree/master/myelectricaldata
* Saniho Card pour Home Assistant : https://github.com/saniho/content-card-linky

## Informations

MyElectricalData utilise une [API](https://myelectricaldata.fr/) dédiée afin de récupérer toutes les informations auprès d'Enedis.

Avant d'utiliser l'outil, il est nécessaire de réaliser votre parcours de consentements.

Tout est expliqué directement sur la passerelle [https://myelectricaldata.fr/](https://myelectricaldata.fr/).

Une fois les consentements effectués et récupérés votre "point de livraison" & "token", vous avez toutes les informations nécéssaires au fonctionnement de l'outil.

> Pour récupérer votre consommation détaillée, il est nécessaire d'activer la "collecte horaire sur Enedis"
>
> Voir [F.A.Q](https://www.myelectricaldata.fr/faq) pour plus de détail.
> 
> **Attention, la collecte horaire est valide pendant 1 an maximum.**

## MyElectricalData limitation

Les API d'Enedis limitent le nombre d'appels par société, à savoir :
- 5 appels par seconde 
- 10 000 appels par heure

Cette limitation est pour la totalité des utilisateurs !

Afin d'éviter d'atteindre cette limite, j'ai mis en place plusieurs fonctionnalités :
- Sans activation du cache, 50 appels / jours et par point de livraison.
- Avec activation du cache, 150 appels / jours et par point de livraison (en cours d'intégration).

> L'activation du cache, m'oblige à stocker vos données (chiffrées) sur ma passerelle pendant une certaine période.
> 
> Voir [F.A.Q](https://www.myelectricaldata.fr/faq) pour plus de détail.

De part ces limitations, il est possible que la récupération des données prennent plusieurs jours si vous n'activez par le cache car :
- ~= 105 appels pour les données horaires sur 2 ans d'historique.
- ~= 36 appels pour les données journalières sur 3 ans.
- 1 appel pour le contrat.
- 1 appel pour les coordonnées.

Un 1er lancement consomme donc environ 150 appels.

> Si vous avez également de la production, vous pouvez doubler le nombre.

L'activation de la persistance des données est donc quasiment obligatoire si vous ne voulez pas dépasser les quotas.

Cf. [persistance](#persistance)


## Fichier de configuration

Nom du ficher : [config.yaml](https://github.com/m4dm4rtig4n/myelectricaldata/blob/master/config.exemple.yaml)

Chemin dans le conteneur docker : _/data/config.yaml_

Un template est disponible sur le repo [config.yaml](https://github.com/m4dm4rtig4n/myelectricaldata/blob/master/config.exemple.yaml)

| Champs           | Information                                                                                                                                                                            | Défaut |
|------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------|
| cycle            | Permet de définir l'interval d'exécution du job d'importation des données (minimun 3600)<br/>Plus vous baissez cette valeur, plus vous avez de chance d'atteindre les quota rapidement | 14400 |
| debug            | Affichage des logs en mode Debug                                                                                                                                                       | False |
| wipe_cache       | Permet de faire une purge des données du cache                                                                                                                                         | False |
| wipe_influxdb    | Permet de faire une purge des données dans InfluxDB                                                                                                                                    | False |
| home_assistant   | Voir block home_assistant                                                                                                                                                              | {}    |
| influxdb         | Voir block influxdb                                                                                                                                                                    | {}    |
| mqtt             | Voir block mqtt                                                                                                                                                                        | {}    |
| myelectricaldata | Voir block myelectricaldata                                                                                                                                                            | {}    |

### home_assistant
| Champs           | Information                                                                  | Défaut        |
|------------------|------------------------------------------------------------------------------|---------------|
| enable           | Activation ou non des exports MQTT au format Home Assistant (auto-discovery) | False         |
| discovery_prefix | Préfixe configuré dans Home Assistant pour l'auto-discovery                  | homeassistant |

### influxdb

> Version supportée minimun 1.8

| Champs           | Information                                                   | Défaut           |
|------------------|---------------------------------------------------------------|------------------|
| enable           | Activation ou non des exports vers InfluxDB                   | False            |
| hostname         | Addresse IP ou domaine vers votre serveur InfluxDB            | influxdb         |
| port             | Port du serveur InfluxDB                                      | 8086             |
| token            | Token en V2 & USERNAME:PASSWORD pour la V1                    | myelectricaldata |
| org              | Nom de l'organisation V2, en V1 mettre "-"                    | myelectricaldata |
| bucket           | Nom du bucket en V2 et "DATABASE/RETENTION" en V1             | myelectricaldata |
| method           | synchronous / asynchronous / batching                         | synchronous      |
| batching_options | https://github.com/influxdata/influxdb-client-python#batching |                  |

#### **method & batching_options :**

Ces 2 propriétés vont vous permettre de jouer sur la rapidité d'importation dans l'influxdb.

> ATTENTION, en fonction de la configuration, vous risquez de surcharger votre serveur.

- **synchronous** : Mode classique assez lent sur l'importation, mais évite de surcharger le CPU & la mémoire.
- **asynchronous** : Mode "bourrin", la totalité des valeurs sera envoyée en même temps et donc consommera énormément de ressources le temps du traimement 
- **batching** : Mode custom qui va vous permettre de jouer sur divers paramètres. A utiliser si le mode synchronous est encore trop gourmand. Plus d'informations disponible [ici](https://github.com/influxdata/influxdb-client-python#batching).

#### Configuration par version :

##### v1.8 :
```yaml
influxdb:
  enable: 'true'  
  hostname: influxdb
  port: 8086
  token: USERNAME:PASSWORD
  org: "-"
  bucket: "DATABASE/RETENTION"
  method: asynchronous
```

##### v2.X :
```yaml
influxdb:
  enable: 'true'  
  hostname: influxdb
  port: 8086
  token: MY_TOKEN
  org: MY_ORG
  bucket: MY_BUCKET
  method: batching
```

### mqtt
| Champs     | Information                                                       | Défaut           |
|------------|-------------------------------------------------------------------|------------------|
| enable     | Activation ou non des exports vers MQTT                           | False            |
| hostname   | Addresse IP ou domaine vers votre serveur MQTT                    | influxdb         |
| port       | Port du serveur MQTT                                              | 8086             |
| username   | Mettre "null" si pas d'authentification                           | myelectricaldata |
| password   | Mettre "null" si pas d'authentification                           | myelectricaldata |
| prefix     | Préfixe de la queue dans MQTT                                     | myelectricaldata |
| client_id  | ID de connexion UNIQUE sur la totalité des clients                | myelectricaldata |
| retain     | Activation de la persistance dans MQTT                            | True             |
| qos        | Inutile de mettre plus de 0 (a part pour surcharger votre réseau) | 0                |


### myelectricaldata

Dictionnaire avec comme clef votre Point de Livraison (entre double quote) contenant toute sa configuration.

| Champs                      | Information                                                                    | Défaut |
|-----------------------------|--------------------------------------------------------------------------------|--------|
| token                       | Activation ou non des exports vers MQTT                                        | ""     |
| name                        | Alias de votre point livraison pour faciliter la navigation                    | ""     |
| addresses                   | Récupération des coordonnées du point de livraison                             | False  |
| cache                       | Activation du cache sur la passerelle                                          | True   |
| consumption                 | Activation de la collecte de consommation journalière                          | True   |
| consumption_detail          | Activation de la collecte de consommation horaire                              | True   |
| consumption_max_date        | Permet de la date boutoir de récupération de la consommation journalière       | ""     |
| consumption_detail_max_date | Permet de la date boutoir de récupération de la consommation détaillée         | ""     |
| consumption_price_base      | Prix d'achat du kW sans forfait HP/HC                                          | 0      |
| consumption_price_hc        | Prix d'achat du kW en Heure Creuse                                             | 0      |
| consumption_price_hp        | Prix d'achat du kW en Heure Pleine                                             | 0      |
| enable                      | Activation du PDL                                                              | True   |
| offpeak_hours_0             | Heure creuse du Lundi                                                          | ""     |
| offpeak_hours_1             | Heure creuse du Mardi                                                          | ""     |
| offpeak_hours_2             | Heure creuse du Mercredi                                                       | ""     |
| offpeak_hours_3             | Heure creuse du Jeudi                                                          | ""     |
| offpeak_hours_4             | Heure creuse du Vendredi                                                       | ""     |
| offpeak_hours_5             | Heure creuse du Samedi                                                         | ""     |
| offpeak_hours_6             | Heure creuse du Dimanche                                                       | ""     |
| plan                        | Votre type de plan BASE ou HP/HC                                               | BASE   |
| production                  | Activation de la collecte de production journalière                            | False  |
| production_detail           | Activation de la collecte de production horaire                                | False  |
| production_price            | Prix de revente à Enedis (Inutile pour l'instant)                              | 0      |
| production_max_date         | Permet de la date boutoir de récupération de la production journalière         | ""     |
| production_detail_max_date  | Permet de la date boutoir de récupération de la production détaillée           | ""     |
| refresh_addresse            | Permet de forcer un rafraichissement des informations "postale" dans le cache  | False  |
| refresh_contract            | Permet de forcer un rafraichissement des informations du contrat dans le cache | False  |

> Si les valeurs **consumption_max_date**, **consumption_max_detail_date**, **production_max_date**, **production_detail_max_date** 
> ne sont pas défini, ce sera la date de début de contrat remonté par Enedis qui sera prise en compte.

#### offpeak_hours

Les champs offpeak_hours_X vont vous permettre de définir vos seuils d'heure creuse/pleine de votre point de livraison si Enedis
ne renvoie pas l'information.

Même si votre forfait est en BASE, je vous recommande de saisir vos HC/HP afin de savoir si votre mode de consommation est
plus adapté au forfait BASE ou HP/HC.

#### Plusieurs mode de HP/HC ?
Pour les utilisateurs ayant différentes plages en fonction des jours de semaine ou weekend, il est nécessaire de renseigner la
configuration manuellement, car les API d'Enedis ne renvoie pas toutes les informations...

_Exemple :_
```
offpeak_hours_0: 3H40-8h10;12H40-16H10
offpeak_hours_1: 3H40-8h10;12H40-16H10
offpeak_hours_2: 0H00-0H00
offpeak_hours_3: 3H40-8h10;12H40-16H10
offpeak_hours_4: 3H40-8h10;12H40-16H10
offpeak_hours_5: 0H00-0H00
offpeak_hours_6: 0H00-0H00 
``` 

#### Tempo

Actuellement Tempo n'est pas encore intégré, mais c'est dans ma TODO. 

## Cache

Afin de réduire le plus possible le nombre de demandes auprès de la passerelle MyElectricaData et d'Enedis, j'ai mis 
en place 2 systèmes de cache :
- Cache Local stocké chez vous (/data/cache.db) obligatoire.
- Cache en ligne sur la passerelle optionnel, mais fortement conseillé (cf #MyElectricalData limitation).

Cependant en utilisant le cache en ligne, vous m'autorisez à stocker temporairement vos données (30j max)

Voir [F.A.Q](https://www.myelectricaldata.fr/faq) pour plus de détail.


## Grafana 

> Actuellement la dashboard est uniquement compatible avec les version <= 0.7.8

Une fois les données exporté dans Grafana, vous pouvez utiliser la dashboard [ICI](ressources/grafana_dashboard.json)

> Ne fonctionne qu'avec InfluxDB <= V1.8

## Docker :

```
docker run -it --restart=unless-stopped -v $(pwd):/data -p 5000:5000 -e TZ="Europe/Paris" m4dm4rtig4n/myelectricaldata:latest
```

## Docker Compose:

```
version: "3.9"
services:
  myelectricaldata:
    image: m4dm4rtig4n/myelectricaldata:latest
    restart: unless-stopped
    volumes:
      - ./:/data     
    environment:
      TZ: Europe/Paris
    ports:
      - '5000:5000'
```

## Environnement de développement

Pré-requis:
 - docker
 - docker-compose
 - make

Affiche l'aide :
```bash
make
````

Démarrer tous les conteneurs en mode "Daemon" :
```bash
make up
````

Arrêter tous les conteneurs :
```bash
make down
````

Démarre l'application en mode normal :
```bash
make run
````

Démarre l'application en mode debug :
```bash
make debug
````

Pour ce connecter au docker en bash :
```bash
make bash
````

## F.A.Q

### Si vous rencontrez des erreurs SQL au démarrage ?

Le plus simple est de supprimer le fichier cache.db et de relancer l’intégration, mais attention, vous allez perdre tout l’historique dans le cache.
Il est cependant possible de le récupérer via la procédure ci-dessous en nommant votre fichier de cache actuel en enedisgateway.db.

### Comment migrer de EnedisGateway2MQTT vers MyElectricalData ?

Pour migrer proprement depuis EnedisGateway2MQTT et avant de lancer la migration vers une version >= 0.8.0, merci de respecter cette procédure :
- Arrêter l’integration
- Backup le fichier enedisgateway.db (au cas où)
- Renommer l’actuel en enedisgateway.db.wait
- Migrer en 0.8.X (Attention le fichier de config a changé vous pouvez reprendre l’exemple [ici](https://github.com/m4dm4rtig4n/myelectricaldata/blob/master/config.exemple.yaml))
- Démarrer en 0.8.X pour initialiser le nouveau cache.
- Arrêter l’intégration.
- Renommer le enedisgateway.db.wait en enedisgateway.db
- Re-lancer l’intégration, il va migrer les anciennes données du enedisgateway.db vers le cache.db (visible dans les logs)

Pour ceux qui auraient eu des soucis lors de la migration et souhaitent récupérer leurs anciennes données en cache: 
- Arrêter l’intégration
- Supprimer le cache.db
- Démarrer l’intégration pour initialiser correctement le cache.db.
- Arrêter l’intégration
- Reprendre le backup (ou le enedisgateway.db.migrate) et le positionner au même endroit que le cache.db avec le nom enedisgateway.db
- Lancer l’intégration en v0.8.X
- L’import du enedisgateway.db vers cache.db se fera au lancement
- Le fichier enedisgateway.db sera renommé en enedisgateway.db.migrate.

## Roadmap

- Intégrer Tempo.
- Gestion du **DJU18** pour une meilleure estimation de l'évolution de votre consommation.
- Ajout d'un connecteur PostgreSQL / MariaDB.
- [Remonter la puissance max](https://github.com/m4dm4rtig4n/enedisgateway2mqtt/issues/66).

## Change log:

### [0.8.0] - 2022-11-XX

#### BREAKING CHANGE

Il est nécessaire de refaire vos consentements sur [MyElectricalData.fr](https://www.myelectricaldata.fr)

Il est nécessaire de reprendre le nouveau "template" du [config.yaml](https://github.com/m4dm4rtig4n/myelectricaldata/blob/master/config.exemple.yaml)

Les "mesurements" d'influxDB ont étaient renommés :
- enedisgateway_daily devient consumption 
- enedisgateway_detail devient consumption_detail 

#### Change Log :
- Ajout d'une interface Web de gestion de vos points de livraison.
- Migration vers la nouvelle plateforme MyElectricalData
- Refonte complète du projet

### [0.7.8] - 2021-11-XX

- Add "wipe_influxdb" paramaters (drop meseaurement enedisgateway_daily & enedisgateway_detail)
- Remove addresses parameters
- Force to false refresh paramaters (refresh_addresses, refresh_contracts, wipe_cache, wipe_influxdb)
- Add hourly consumption compatible with apexchart-card.

*Exemple for hourly consumption :*

```
type: custom:apexcharts-card
graph_span: 5d
span:
  start: day
  offset: '-6d'
apex_config:
  dataLabels:
    enabled: true
series:
  - entity: sensor.enedisgateway_XXXXXXXXXXXXXXXXXX_hourly
    name: af
    extend_to_end: false
    data_generator: |
      return entity.attributes.hourly.map((hourly, index) => {     
                return [new Date(hourly).getTime(), entity.attributes.hourly_value[index]];
              });

```


### [0.7.7] - 2021-11-22

*UPGRADE Procedure :*
- 0.7.6 -> 0.7.7 : Wipe influxdb database. 

*Change Log :*
- Fix [Null values don’t mean no values](https://github.com/m4dm4rtig4n/enedisgateway2mqtt/issues/45)
- Fix [Timezone bug](https://github.com/m4dm4rtig4n/enedisgateway2mqtt/issues/48)
- Fix [HP/HC no cost](https://github.com/m4dm4rtig4n/enedisgateway2mqtt/issues/67)
- Fix [HP/HC wrong price](https://github.com/m4dm4rtig4n/enedisgateway2mqtt/issues/54)
- Switch Enedis API Call in UTC Datetime (reduce error)
- Fix offpeak hours in HA Sensor

### [0.7.4] - 2021-11-18

- Fix SQLite closed connection

### [0.7.3] - 2021-11-17

- Fix debug

### [0.7.2] - 2021-11-17

- Fix OFFPEAK_HOUR bug

### [0.7.1] - 2021-11-16

**BREAKING CHANGE - All configuration is now in config.yml**

>**Not update to 0.7.0 if you don't have adapt your configuration**

### [0.7.0] - 2021-11-14

- Skip version

### [0.6.0] - 2021-11-05

- Add timeout to API Call

### [0.5.7] - 2021-11-02

- Fix bug
- HassOS Addons available : https://github.com/alexbelgium/hassio-addons/tree/master/enedisGateway2MQTT (special thx to [alexbelgium](https://github.com/alexbelgium))

### [0.5.6] - 2021-11-01

- Reduce API Call
- Add more log
- Fix bug

### [0.5.5] - 2021-11-01

- Fix log on MQTT connection failed :
> NameError: name 'client' is not defined

### [0.5.4] - 2021-10-31

- HA Sensor (kW => Wh)
- HA Sensor add uniq_id 
- HA Sensor add device (thx to Smeagolworms4)
- Fix offpeak bug
- Add dev environment (thx to Smeagolworms4)

### [0.5.3] - 2021-10-23

- Fix bug

### [0.5.2] - 2021-10-22

- Add influxdb connecter & exporter
- Grafana dashboard exemple

### [0.5.1] - 2021-10-15

- Create HA sensor for Linky Card with auto-discovery
- Add param to choose current plan

### [0.5.0] - 2021-10-13

- Add HC/HP
- Rework database structure (all cached data are reset)
- Add new params to reset all cache.

### [0.4.1] - 2021-10-06

- Cache addresses & contracts data.

### [0.4.0] - 2021-10-05

- Switch locale to fr_FR.UTF8 (french date format)
- Switch ha_discovery state in kW by default (W before)
- Add Database structure check + reset if broken
- Optimise caching
- Change MQTT structure per days
- I remove the "years" parameter and automatically set the max value (36 month)
- Switch image docker to python-slim to reduce image size (900mo => 150mo)
- Fixes various bugs 

### [0.3.2] - 2021-09-29

- Fix HA Discovery error.

### [0.3.1] - 2021-09-29

- Fix error when API call limit is reached.

### [0.3] - 2021-09-28

- Rework ha discovery to reduce items
- Fix ha_autodiscovery always enable
- Get Production
- Add SQLite database to store data and reduce number of API Call.

### [0.2] - 2021-09-25

- Helm chart
- Home Assistant auto-discovery
- Add Retain & QoS (MQTT)
- Add Timestamp in log

### [0.1] - 2021-09-24

- First Release

[smb-shield]: https://img.shields.io/badge/SMB--green?style=plastic.svg
[repository]: https://github.com/alexbelgium/hassio-addons
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
