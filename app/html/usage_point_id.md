{% if address_data != {} and  
address_data['street'] is defined and 
address_data['postal_code'] is defined and 
address_data['city'] is defined and 
address_data['country'] is defined
%}
# {{address_data['street']}}, {{address_data['postal_code']}} {{address_data['city']}} {{address_data['country']}}
{% else %}
# Aucune infos 
{% endif %}

## Mon contrat

Status du point de livraison : **{{ contract_data['usage_point_status'] | default("Pas de données")}}**

Type de mesure : **{{ contract_data['meter_type'] | default("Pas de données") }}**

Segment: **{{ contract_data['segment'] | default("Pas de données") }}**

Puissance souscrite: **{{ contract_data['subscribed_power'] | default("Pas de données") }}**

Date d'activation : **{{ contract_data['last_activation_date'] | default("Pas de données") }}**

Tarif de distribution : **{{ contract_data['distribution_tariff'] | default("Pas de données") }}**

Seuil heures creuse / pleine : **{{ contract_data['offpeak_hours'] | default("Pas de données") }}**

Status du contrat : **{{ contract_data['contract_status'] | default("Pas de données") }}**

Dernière date de changement du tarif : **{{ contract_data['last_distribution_tariff_change_date'] | default("Pas de données") }}**