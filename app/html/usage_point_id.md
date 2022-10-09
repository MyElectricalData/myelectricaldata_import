# {{address_data['usage_point']['usage_point_addresses']['street']}}, {{address_data['usage_point']['usage_point_addresses']['postal_code']}} {{address_data['usage_point']['usage_point_addresses']['city']}} {{address_data['usage_point']['usage_point_addresses']['country']}}
## Contrat

Status du point de livraison : **{{ contract_data['usage_point']['usage_point_status'] }}**

Type de mesure : **{{ contract_data['usage_point']['meter_type'] }}**

Segment: **{{ contract_data['contracts']['segment'] }}**

Puissance souscrite: **{{ contract_data['contracts']['subscribed_power'] }}**

Date d'activation : **{{ contract_data['contracts']['last_activation_date'] }}**

Tarif de distribution : **{{ contract_data['contracts']['distribution_tariff'] }}**

Seuil heures creuse / pleine : **{{ contract_data['contracts']['offpeak_hours'] }}**

Status du contrat : **{{ contract_data['contracts']['contract_status'] }}**

Dernière date de changement du tarif : **{{ contract_data['contracts']['last_distribution_tariff_change_date'] }}**

## Consomation journalière

{{ daily_consumption }}