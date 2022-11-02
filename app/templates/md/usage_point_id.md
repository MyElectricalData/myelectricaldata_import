# {{title}}

## Mon contrat

Adresse postal : **{{ address | default("Pas de donnée.") }}**

Status du point de livraison : **{{ contract_data['usage_point_status'] | default("Pas de donnée.")}}**

Type de mesure : **{{ contract_data['meter_type'] | default("Pas de donnée.") }}**

Segment: **{{ contract_data['segment'] | default("Pas de donnée.") }}**

Puissance souscrite: **{{ contract_data['subscribed_power'] | default("Pas de donnée.") }}**

Date d'activation : **{{ contract_data['last_activation_date'] | default("Pas de donnée.") }}**

Tarif de distribution : **{{ contract_data['distribution_tariff'] | default("Pas de donnée.") }}**

Status du contrat : **{{ contract_data['contract_status'] | default("Pas de donnée.") }}**

Dernière date de changement du tarif : **{{ contract_data['last_distribution_tariff_change_date'] | default("Pas de donnée.") }}**

Seuil heures creuse / pleine :