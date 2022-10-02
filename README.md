# EnedisGateway2MQTT

[![Donate][donation-badge]](https://www.buymeacoffee.com/m4dm4rtig4n)

[donation-badge]: https://img.shields.io/badge/Buy%20me%20a%20coffee-%23d32f2f?logo=buy-me-a-coffee&style=flat&logoColor=white

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield]

**Best french discord community about "Domotique & Diy" :**

[![https://discord.gg/DfVJZme](discord.png 'Best french discord community about "Domotique & Diy"')](https://discord.gg/DfVJZme)

****

## IMPORTANT !
**The tool is still under development.
It is possible that various functions disappear or be modified**

# Links

* Github Repository : https://github.com/m4dm4rtig4n/enedisgateway2mqtt
* Docker Hub Images : https://hub.docker.com/r/m4dm4rtig4n/enedisgateway2mqtt
* Hassio Addons : https://github.com/alexbelgium/hassio-addons/tree/master/enedisgateway2mqtt
* Saniho Card for Home Assistant : https://github.com/saniho/content-card-linky

## Informations

EnedisGateway2MQTT use [Enedis Gateway](https://enedisgateway.tech/) API to send data in your MQTT Broker.

### Generate ACCESS_TOKEN

#### 1st Step - Enedis Website

- Go to [Enedis Website](https://mon-compte.enedis.fr/alex-gdc/identity/manageexternalaccount)
- Log or create account
- Link your Linky
- Go in page "Gérer l’accès à mes données" and enable all collect. (The boxes at the bottom right of the page.)

**Sometimes it takes several days for Enedis to activate the collection.**

**Activation is only valid for 1 year.**

#### 2sde Step - Enedis Gateway

- Go to [Enedis Gateway](https://enedisgateway.tech/) and clic on "*Faire la demande de consentement*"
- Approuve your concentment
- At the end, your are redirect to [Enedis Gateway](https://enedisgateway.tech/) and you can found your access_token
and curl test command.

**WARNING, The enedis website has some issues with chrome / chromium based browsers.
The easiest way is to use Firefox in the consent process** 


## EnedisGateway2MQTT limit

In order to avoid saturation of Enedis Gateway services, the number of API calls is limited to 15 per day.
Most of the information will be collected during the first launch.
You will just need a few days to report all "detailed" consumption over 2 years (about 1 week)

## Enedis Gateway limit

Enedis Gateway limit to 50 call per day / per pdl.

If you reach this limit, you will be banned for 24 hours!

**API call number by parameters :**

| Parameters  | Call number |
|:---------------|:---------------:|
| GET_CONSUMPTION | 3 |
| GET_CONSUMPTION_DETAIL | 105 |
| GET_PRODUCTION | 3 |
| GET_PRODUCTION_DETAIL | 105 |
| ADDRESSES | 1 |
| CONTRACT | 1 |

See chapter [persistance](#persistance), to reduce API call number.


## Configuration File

Filename : config.yaml

Container path : /data/config.yaml

The easiest is to map the "/data" in local because it is also this folder that contains the cache.

3 parameters is mandatory :
- MQTT Hostname
- At least one PDL 
- PDL token

> All other variables have default values

Exemple :

```yaml
##########
# GLOBAL #
##########
debug: false

####################
##      MQTT      ##
####################
mqtt:
  host: MOSQUITO_SERVER       # MANDATORY
  port: 1883
  username: ""
  password: ""
  prefix: enedis_gateway
  client_id: enedis_gateway
  retain: true
  qos: 0

####################
## Home assistant ##
####################
home_assistant:
  discovery: false
  discovery_prefix: homeassistant
  card_myenedis: false
  hourly: false

###############
## Influx DB ##
###############
#influxdb: 
#  scheme: http    # or https
#  host: MY_INFLUXDB_SERVER
#  port: 8086
#  token: MY_TOKEN
#  org: MY_ORG
#  bucket: MY_BUCKET

####################
## ENEDIS GATEWAY ##
####################
enedis_gateway:
  "XXXXXXXXXXXXXX":              # Replace XXXXXXXXXXXXXX by your PDL Number. MANDATORY
    token: "YOUR_TOKEN"          # MANDATORY
    plan: BASE                 # BASE or HP/HC
    consumption: true                 
    consumption_detail: true         
    consumption_price_hc: 0           
    consumption_price_hp: 0           
    consumption_price_base: 0         
    production: false                 
    production_detail: false          
    offpeak_hours: ""         # USE ONLY IF YOU WANT OVERLOAD DEFAULT VALUE, Format : 22h36-06h00;11h30-14h30
    addresses: true
#  YYYYYYYYYYYYYY:            # Replace YYYYYYYYYYYYYY by your other PDL Number
#    token: YOUR_TOKEN
#    plan: HP/HC
#    consumption: true
#    consumption_detail: true
#    consumption_price_hc: 0.1781
#    consumption_price_hp: 0.1337
#    consumption_price_base: 0.1781
#    production: false
#    production_detail: false
#    addresses: true
```
> offpeak_hours : I automatically retrieve the information via the Enedis APIs, but it happens that some account does not upload it.
This parameter will allow you to fill in your HP / HC ranges yourself in order to be able to compare your consumption according to the 2 subscriptions. 

## Cache

Since v0.3, Enedis Gateway use SQLite database to store all data and reduce API call number.
> **Don't forget to mount /data to keep database persistance !!**

If you wan wipe cache, just delete enedisgateway.db and restat container.

**WARNING, if you wipe all data you generate lot of API Call (don't forget [Enedis Gateway limit](#Enedis Gateway limit))**

> It doesn't forget that it takes several days to recover consumption/production in detail mode.

## Consumption BASE vs HP/HC

Even if you are on a basic plan (and not HP / HC), it is interesting to enter the prices of each plan.
The tool will do calculation for you and tell you which plan is the most advantageous for you based on your consumption.

### Blacklist

Sometimes there are holes in the Enedis consumption records. So I set up a blacklist system for certain dates.

If date does not return information after 7 try (7 x CYCLE), I blacklist this date and will no longer generate an API call

## InfluxDB

Gateway is work with influxDB version 1.X & 2.X

### v1.X :
```yaml
influxdb:
    host: influxdb
    port: 8086
    token: USERNAME:PASSWORD
    org: "-"
    bucket: "DATABASE/RETENTION"
```

### v2.X :
```yaml
influxdb:
    host: influxdb
    port: 8086
    token: MY_TOKEN
    org: MY_ORG
    bucket: MY_BUCKET
```

## Grafana 

When you are exported all data in your influxDB, you can use this [grafana dashboard](grafana_dashboard.json).

> Actually it's work only in InfluxQL (v1 language), Flux mode (v2 language) it's in progress...
> But you can use InfluxQL in V2. 

## Usage :

**These are EXAMPLES, and do not necessarily represent your settings!**

**Please read [parameter table](#environment-variable) and adapt to your configuration.**


```
docker run -it --restart=unless-stopped -v $(pwd):/data m4dm4rtig4n/enedisgateway2mqtt:latest
```

**docker-compose.yml**
```
version: "3.9"
services:
  enedisgateway2mqtt:
    image: m4dm4rtig4n/enedisgateway2mqtt:latest
    restart: unless-stopped
    volumes:
        -./:/data     
```

## Dev environment

Requirement:
 - docker
 - docker-compose
 - make

Display help information:
```bash
make
````

Start containers:
```bash
make up
````

Stop containers:
```bash
make down
````

Start application:
```bash
make start
````

Connect to container:
```bash
make start
````

## Roadmap

- Add **DJU18**
- Add Postgres/MariaDB Connector
- [Add max power](https://github.com/m4dm4rtig4n/enedisgateway2mqtt/issues/66)
- [Add range date](https://github.com/m4dm4rtig4n/enedisgateway2mqtt/issues/68)

## Change log:

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
