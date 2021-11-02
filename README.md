# EnedisGateway2MQTT

## IMPORTANT !
**The tool is still under development.
It is possible that various functions disappear or be modified**

# Links

Github Repository : https://github.com/m4dm4rtig4n/enedisgateway2mqtt

Docker Hub Images : https://hub.docker.com/r/m4dm4rtig4n/enedisgateway2mqtt

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


## Environment variable 

| Variable  | Information | Mandatory/Default |
|:---------------|:---------------:|:-----:|
| ACCESS_TOKEN | Your access token generate after Enedis Gateway consent | * |
| PDL | Your Linky Point Of Delivery | * |
| MQTT_HOST | Mosquitto IP address  | * |
| MQTT_PORT | Mosquitto Port | 1883 |
| MQTT_PREFIX | Mosquitto Queue Prefix | enedis_gateway |
| MQTT_CLIENT_ID | Mosquitto Client ID | enedis_gateway |
| MQTT_USERNAME | Mosquitto Username (leave empty if no user) |  |
| MQTT_PASSWORD | Mosquitto Password (leave empty if no user) |  |
| RETAIN | Retain data in MQTT | False |
| QOS | Quality Of Service MQTT | 0 |
| GET_CONSUMPTION | Enable API call to get your consumption | True |
| GET_CONSUMPTION_DETAIL | Enable API call to get your consumption in detail mode | True |
| GET_PRODUCTION | Enable API call to get your production | False |
| GET_PRODUCTION_DETAIL | Enable API call to get your production in detail mode | False |
| HA_AUTODISCOVERY | Enable auto-discovery | False |
| HA_AUTODISCOVERY_PREFIX | Home Assistant auto discovery prefix | homeassistant |
| OFFPEAK_HOURS | Force HP/HC format : "HHhMM-HHhMM;HHhMM-HHhMM;...". It's optionnal, by default I load this info automatically when I get contracts | "" |
| CONSUMPTION_PRICE_BASE | Price of kWh in base plan | 0 |
| CONSUMPTION_PRICE_HC | Price of HC kWh | 0 |
| CONSUMPTION_PRICE_HP | Price of HP kWh | 0 |
| CYCLE | Data refresh cycle (1h minimum) | 3600 |
| ADDRESSES | Get all addresses information | False |
| REFRESH_CONTRACT | Refresh contract data | False | 
| REFRESH_ADDRESSES | Refresh addresses data | False |  
| WIPE_CACHE | Force refresh all data (wipe all cached data)  | False |   
| DEBUG | Display debug information  | False |   
| CARD_MYENEDIS | Create HA sensor for Linky Card with auto-discovery  | False |   
| CURRENT_PLAN | Choose you plan "BASE" or "HP/HC"  | BASE |   
| INFLUXDB_ENABLE | Enable influxdb exporter  | False |   
| INFLUXDB_HOST | Influxdb Host or IP Address  | "" |   
| INFLUXDB_PORT | Influxdb port | 8086 |   
| INFLUXDB_TOKEN | Influxdb token (v2)  | "" |   
| INFLUXDB_ORG | Influxdb Org (v2)  | "" |   
| INFLUXDB_BUCKET | Influxdb bucket name (v2)  | "" |

## Cache

Since v0.3, Enedis Gateway use SQLite database to store all data and reduce API call number.
> **Don't forget to mount /data to keep database persistance !!**

If you change your contract, plan it is necessary to do a reset "**REFRESH_CONTRACT**" to "**True**"

if you move, it is necessary to make a "**REFRESH_ADDRESSES**" to "**True**"

If you want force refresh all data you can set environment variable "**WIPE_CACHE**" to "**True**".

**WARNING, This parameters wipe all data (addresses, contracts, consumption, production) and generate lot of API Call (don't forget [Enedis Gateway limit](#Enedis Gateway limit))**

> It doesn't forget that it takes several days to recover consumption/production in detail mode.

## Consumption BASE vs HP/HC

Even if you are on a basic plan (and not HP / HC), it is interesting to enter the prices of each plan.
The tool will do calculation for you and tell you which plan is the most advantageous for you based on your consumption.

### Blacklist

Sometimes there are holes in the Enedis consumption records. So I set up a blacklist system for certain dates.

If date does not return information after 7 try (7 x CYCLE), I blacklist this date and will no longer generate an API call

## Grafana & InfluxDB v2

> Not compatible with InfluxDB v1.X

EnedisGateway2MQTT integrates an influxdb connector which will allow you to export all the information.
And you can found Grafana dashboard [here](grafana_dashboard.json).

## Usage :

**These are EXAMPLES, and do not necessarily represent your settings!**

**Please read [parameter table](#environment-variable) and adapt to your configuration.**


```
ACCESS_TOKEN="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
PDL="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
MQTT_HOST='' 
MQTT_PORT="1883"                
MQTT_PREFIX="enedis_gateway"    
MQTT_CLIENT_ID="enedis_gateway" 
MQTT_USERNAME='enedis_gateway_username'
MQTT_PASSWORD='enedis_gateway_password'
RETAIN="True"
QOS=0
GET_CONSUMPTION="True"
GET_CONSUMPTION_DETAIL="True"
GET_PRODUCTION="False"
GET_PRODUCTION_DETAIL="False"
HA_AUTODISCOVERY="False"
HA_AUTODISCOVERY_PREFIX='homeassistant'
CONSUMPTION_PRICE_BASE=0
CONSUMPTION_PRICE_HC=0
CONSUMPTION_PRICE_HP=0   
CARD_MYENEDIS="False"              

docker run -it --restart=unless-stopped \
    -e ACCESS_TOKEN="$ACCESS_TOKEN" \
    -e PDL="$PDL" \
    -e MQTT_HOST="$MQTT_HOST" \
    -e MQTT_PORT="$MQTT_PORT" \
    -e MQTT_PREFIX="$MQTT_PREFIX" \
    -e MQTT_CLIENT_ID="$MQTT_CLIENT_ID" \
    -e MQTT_USERNAME="$MQTT_USERNAME" \
    -e MQTT_PASSWORD="$MQTT_PASSWORD" \
    -e RETAIN="$RETAIN" \
    -e QOS="$QOS" \
    -e GET_CONSUMPTION="$GET_CONSUMPTION" \
    -e GET_CONSUMPTION_DETAIL="$GET_CONSUMPTION_DETAIL" \
    -e GET_PRODUCTION="$GET_PRODUCTION" \
    -e GET_PRODUCTION_DETAIL="$GET_PRODUCTION_DETAIL" \
    -e HA_AUTODISCOVERY="$HA_AUTODISCOVERY" \
    -e HA_AUTODISCOVERY_PREFIX="$HA_AUTODISCOVERY_PREFIX" \
    -e CONSUMPTION_PRICE_BASE="$CONSUMPTION_PRICE_BASE" \
    -e CONSUMPTION_PRICE_HC="$CONSUMPTION_PRICE_HC" \
    -e CONSUMPTION_PRICE_HP="$CONSUMPTION_PRICE_HP" \
    -e CARD_MYENEDIS="$CARD_MYENEDIS" \
m4dm4rtig4n/enedisgateway2mqtt:latest
```

**docker-compose.yml**
```
version: "3.9"
services:
  enedisgateway2mqtt:
    image: m4dm4rtig4n/enedisgateway2mqtt:latest
    restart: unless-stopped
    volumes:
        - mydata:/data
    environment:
      ACCESS_TOKEN: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
      PDL: "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
      MQTT_HOST: ""
      MQTT_PORT: "1883"
      MQTT_PREFIX: "enedis_gateway"
      MQTT_CLIENT_ID: "enedis_gateway"
      MQTT_USERNAME: 'enedis_gateway_username'
      MQTT_PASSWORD: 'enedis_gateway_password'
      RETAIN: "True"
      QOS: 0
      GET_CONSUMPTION: "True"
      GET_PRODUCTION: "False"
      HA_AUTODISCOVERY: "False"
      HA_AUTODISCOVERY_PREFIX: 'homeassistant'
      CONSUMPTION_PRICE_BASE: 0
      CONSUMPTION_PRICE_HC: 0
      CONSUMPTION_PRICE_HP: 0 
      CARD_MYENEDIS: "False"    
    logging:
      options:
        max-size: "10m"
        max-file: "3"
volumes:
  mydata:      
```

## Dev environment

Requirements:
 - docker
 - docker-compose
 - make

Display help informations:
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

Connect to app container:
```bash
make bash
````

## Roadmap

- Add **DJU18**
- Add Postgres/MariaDB Connector

## Change log:

### [0.5.7] - 2021-11-02

- Fix bug
- HassOS Addons available : https://github.com/alexbelgium/hassio-addons/tree/master/enedisGateway2MQTT (special thx to alexbelgium)

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
