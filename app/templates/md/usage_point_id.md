# {{title}}

## Mon contrat

* Les données ont été récupérées via les API d'Enedis et ne sont pas toujours correctement mises à jour par Enedis.
Vérifiez bien vos horaires HC/HP et votre date d'activation. Vous pouvez surcharger ces valeurs dans la configuration du point de livraison.

Adresse postale : **{{ address | default("Pas de données.") }}**

Statut du point de livraison : **{{ contract_data['usage_point_status'] | default("Pas de données.")}}**

Type de mesure : **{{ contract_data['meter_type'] | default("Pas de données.") }}**

Segment: **{{ contract_data['segment'] | default("Pas de données.") }}**

Puissance souscrite: **{{ contract_data['subscribed_power'] | default("Pas de données.") }}**

Date d'activation : **{{ contract_data['last_activation_date'] | default("Pas de données.") }}**

Tarif de distribution : **{{ contract_data['distribution_tariff'] | default("Pas de données.") }}**

Statut du contrat : **{{ contract_data['contract_status'] | default("Pas de données.") }}**

Dernière date de changement du tarif : **{{ contract_data['last_distribution_tariff_change_date'] | default("Pas de données.") }}**

Seuil heures creuses / pleines :
