# BL Car Tracker

Intégration Home Assistant qui donne une position à un véhicule (voiture, moto, vélo…) en copiant celle de la personne dont le téléphone est connecté en Bluetooth à ce véhicule. Un appareil Bluetooth (autoradio, kit mains libres…) identifie chaque véhicule.

Prérequis : l'app **Home Assistant Companion pour Android**, qui expose le capteur `sensor.<téléphone>_bluetooth_connection` et son attribut `connected_paired_devices`. Ce capteur doit être activé dans l'app.

## Entités créées (par véhicule)

- **`device_tracker.<véhicule>`** : position du véhicule (GPS), utilisable sur la carte et dans les déclencheurs de zone.
  - téléphone connecté : le véhicule suit la position de la personne ;
  - téléphone déconnecté : la dernière position est conservée (place de stationnement), même après un redémarrage de Home Assistant.
- **`binary_sensor.<véhicule>`** (occupation) : `on` tant que le téléphone d'une personne connue est connecté au véhicule.
- Attribut `connected_person` sur les deux entités : l'entité `person.*` connectée, ou `null`.

Si plusieurs téléphones sont connectés en même temps, la première personne configurée est prioritaire.

## Installation

### Via HACS (dépôt personnalisé)

1. HACS → menu (⋮) → **Dépôts personnalisés** → ajouter `https://github.com/Rimfire03/Car-Tracker`, catégorie *Intégration*.
2. Rechercher **BL Car Tracker** dans HACS et installer.
3. Redémarrer Home Assistant.

### Manuellement

1. Copier le dossier `custom_components/bl_car_tracker` dans `<config>/custom_components/`.
2. Redémarrer Home Assistant.

## Configuration

Entièrement via l'interface (**Paramètres → Appareils et services → Ajouter une intégration → BL Car Tracker**) :

1. Nom du véhicule, adresse MAC Bluetooth de son appareil embarqué (`AA:BB:CC:DD:EE:FF`, visible dans l'attribut `paired_devices` du capteur du téléphone), image optionnelle.
2. Pour chaque personne : le capteur Bluetooth de son téléphone et la personne (`person.*`) correspondante.
3. Répéter l'intégration pour chaque véhicule.

Un même MAC ne peut être configuré qu'une fois.

## Migration depuis des templates YAML

Supprimer les anciens `binary_sensor` template (et leurs entrées du registre d'entités) avant d'ajouter le véhicule, pour que les nouvelles entités reprennent le même nom. Remplacer ensuite, dans les automatisations, le déclencheur de zone sur l'ancien `binary_sensor.<véhicule>` par `device_tracker.<véhicule>`.

## Statut du projet

⚠️ Avant soumission à HACS, créer une release Git taguée (ex. `v0.1.0`) — HACS s'appuie sur les tags/releases GitHub pour le versionnage.

## Licence

MIT — voir [LICENSE](LICENSE).
