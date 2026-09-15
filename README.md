# MyElectricalData

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armhf Architecture][armhf-shield] ![Supports armv7 Architecture][armv7-shield]

---

## ⚠️ Fork personnel (Marlboro62) — patch beta

Ce fork ajoute les fonctionnalités suivantes en attendant leur intégration éventuelle dans le projet officiel :

### 1. Date de début de période annuelle personnalisée (`annual_period_start`)

- Nouvelle option de configuration par point de livraison, format `MM-JJ` (ex. `09-01` pour le 1er septembre), configurable directement dans le formulaire web du PDL (section "Global").
- Par défaut : `01-01` (comportement identique à l'original, année civile).
- Impacte :
  - Le calcul de consommation/production annuelle (`Stat.current_year`, `last_year`, `get_year`)
  - Le tableau récapitulatif "Annuel" (affiché en plage de dates explicite, ex. `10/2025 - 09/2026`)
  - Les graphiques mensuels (réordonnés pour commencer au mois de la période choisie)
  - Les statistiques tarifaires Tempo (`generate_price`)
  - Les exports MQTT (labels `current` cohérents avec la période choisie)
- Référence : [issue #621](https://github.com/MyElectricalData/myelectricaldata_import/issues/621), [PR #637](https://github.com/MyElectricalData/myelectricaldata_import/pull/637)

### 2. Répartition Tempo à 6 catégories (Bleu/Blanc/Rouge × HC/HP)

- Le camembert "Ratio HC/HP" de l'interface web affiche désormais 6 parts pour les points de livraison en plan Tempo (au lieu de 2 parts HC/HP génériques), aligné sur la période annuelle personnalisée.
- Nouveaux capteurs Home Assistant : pourcentage de chaque catégorie Tempo pour l'année en cours (`Pourcentage Bleu HC`, `Pourcentage Rouge HP`, etc.).
- La production (`recap()`) a été basculée sur la même logique que la consommation (`recapv2()`) pour plus de cohérence et moins de code dupliqué.

### 3. Noms de capteurs Home Assistant traduits en français

- Les capteurs MQTT/discovery (Linky, EDF Tempo, RTE Tempo) affichent désormais des noms français lisibles : `Consommation HC Bleu`, `Coût consommation HP Rouge`, `Historique Consommation`, `Aujourd'hui`/`Demain`, `Jours Bleu`, `Prix Rouge HP`, etc.
- La valeur d'état des capteurs RTE Tempo (`Aujourd'hui`/`Demain`) affiche `Bleu`/`Blanc`/`Rouge` au lieu de `BLUE`/`WHITE`/`RED` (uniquement l'affichage, la logique interne reste inchangée).
- Les statistiques long terme du tableau de bord Énergie de Home Assistant (`recorder/import_statistics`) sont également traduites : `Bleu HC Consommation`, `Rouge HP Consommation`, `Coût`/`Revenu` au lieu de `Cost`/`Revenue`, etc. Home Assistant régénère automatiquement les métadonnées (quelques minutes) sans perte d'historique.

### Fichiers modifiés

- `src/models/config.py`, `src/db_schema.py`, `src/models/database.py` — stockage de `annual_period_start`
- `src/alembic/versions/d4f21c9a8b6e_add_annual_period_start.py` — migration DB
- `src/templates/models/configuration.py` — champ dans le formulaire web
- `src/models/stat.py` — calculs alignés sur la période perso
- `src/templates/usage_point.py` — graphiques, tableau annuel, camembert Tempo
- `src/models/export_home_assistant.py`, `src/models/export_home_assistant_ws.py` — traductions + capteurs pourcentage
- `src/models/export_mqtt.py` — cohérence du label `current`
- `src/__version__.py` — version interne synchronisée

### Utilisation

Ce fork est disponible comme addon Home Assistant via [Marlboro62/hassio-addons](https://github.com/Marlboro62/hassio-addons), construit à partir de l'image Docker [`marlboro62/myelectricaldata:patched`](https://hub.docker.com/r/marlboro62/myelectricaldata).

---


## Francais

### IMPORTANT

**EnedisGateway2MQTT** devient **MyElectricalData** et la dépendance à MQTT n'est plus obligatoire.

---

MyElectricalData est le client officiel de la plateforme [MyElectricaData](https://myelectricaldata.fr) qui va vous permettre de récupérer votre consommation depuis les API d'Enedis.

Toutes les données seront importées dans un cache local (SQLite) ou externe (PostgreSQL) qui pourrais ensuite être exporté vers :

- MQTT
- Home Assistant (Via l'auto-discovery MQTT)
- InfluxDB / VictoriaMetrics
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
- InfluxDB / VictoriaMetrics
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
