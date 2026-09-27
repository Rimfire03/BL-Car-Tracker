# Vehicle Presence (Car Tracker)

Intégration Home Assistant qui détecte, pour chaque véhicule, quelle personne connue s'y trouve — en observant la liste des appareils Bluetooth appairés exposée par les capteurs de téléphone (ex. `sensor.sm_xxxx_bluetooth_connection`).

Pour chaque véhicule configuré, l'intégration crée une entité `binary_sensor` :
- **état** : `on` si le téléphone d'au moins une personne connue est actuellement appairé avec le véhicule, `off` sinon
- **attribut `connexion`** : l'entité `person.*` détectée (ou `null` si personne)
- **attributs `latitude` / `longitude` / `gps_accuracy`** : repris de la personne détectée, avec repli sur la première personne configurée si aucun téléphone n'est actuellement appairé

## Installation

### Via HACS (dépôt personnalisé)

1. HACS → menu (⋮) → **Dépôts personnalisés** → ajouter l'URL de ce dépôt GitHub, catégorie *Intégration*.
2. Rechercher **Vehicle Presence** dans HACS et installer.
3. Redémarrer Home Assistant.

### Manuellement

1. Copier le dossier `custom_components/vehicle_presence` dans `<config>/custom_components/`.
2. Redémarrer Home Assistant.

## Configuration

Entièrement via l'interface (**Paramètres → Appareils et services → Ajouter une intégration → Vehicle Presence**) :

1. Nom du véhicule, adresse MAC Bluetooth du véhicule, image optionnelle.
2. Pour chaque personne à surveiller : le capteur Bluetooth du téléphone et la personne (`person.*`) correspondante. La première personne ajoutée sert de valeur par défaut (position affichée) quand aucun téléphone connu n'est appairé.
3. Répéter l'intégration pour ajouter d'autres véhicules.

## Statut du projet

⚠️ Avant publication sur HACS, mettre à jour dans `custom_components/vehicle_presence/manifest.json` :
- `codeowners`
- `documentation`
- `issue_tracker`

avec votre nom d'utilisateur GitHub et l'URL réelle du dépôt, puis créer une release Git taguée (ex. `v0.1.0`) — HACS s'appuie sur les tags/releases GitHub pour le versionnage.

## Licence

MIT — voir [LICENSE](LICENSE).
