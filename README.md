# 🚗 BL Car Tracker

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/Rimfire03/BL-Car-Tracker?include_prereleases)](https://github.com/Rimfire03/BL-Car-Tracker/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-orange.svg?logo=buy-me-a-coffee&logoColor=white)](https://buymeacoffee.com/slide598b)

> Give a position to your vehicles in **Home Assistant** (car, motorbike, bike...) by copying the position of the person whose phone is connected to the vehicle over Bluetooth, 100% configurable from the UI, ready for **HACS**.  
> *Donnez une position à vos véhicules dans **Home Assistant** (voiture, moto, vélo...) en copiant celle de la personne dont le téléphone est connecté en Bluetooth au véhicule, 100 % configurable depuis l'interface, prêt pour **HACS**.*

---

## ☕ Support / Soutenir le projet

If you find this integration helpful, consider buying me a coffee to support the development!  
*Si vous appréciez cette intégration, vous pouvez m'offrir un café pour soutenir le développement !*

<a href="https://buymeacoffee.com/slide598b" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 50px !important;width: 217px !important;" ></a>

---

## 🌐 Languages Supported / Langues Disponibles

- 🇬🇧 **English**
- 🇫🇷 **Français**

---

# 🇬🇧 English Documentation

Each vehicle is identified by the Bluetooth device it carries (head unit, hands-free kit...). When a known phone connects to it, the vehicle follows that person. When the phone disconnects, the vehicle stays where it was parked.

## ✨ Features

- ⚙️ **100% UI configurable, no YAML:** vehicle, Bluetooth device, persons and picture are set up in **Settings → Devices & services**.
- 📍 **`device_tracker` per vehicle:**
  - phone connected: the vehicle copies the person's position (latitude, longitude, accuracy);
  - phone disconnected: the last position is kept (the parking spot), also after a Home Assistant restart.
- 🧑 **`binary_sensor` per vehicle (occupancy):** `on` while a known person's phone is connected. The `connected_person` attribute holds the matching `person.*` entity, or `null`.
- 🖼️ **Picture by drag & drop:** drop an image (PNG, JPG, GIF, WebP) in the setup form, or give a URL.
- 👥 **Persons and vehicles are independent:** every person can drive the position of every vehicle. When several phones are connected to the same vehicle, the first person added wins.
- 🚪 **Zone triggers:** use the `device_tracker` in automations, for example to close the gate when the car leaves home.

Requires the **Home Assistant Companion app for Android**, which exposes `sensor.<phone>_bluetooth_connection` and its `connected_paired_devices` attribute (enable that sensor in the app).

## 📦 Installation

### Method 1: Via HACS (custom repository)

1. In Home Assistant, open **HACS** → menu (⋮) → **Custom repositories**.
2. Add `https://github.com/Rimfire03/BL-Car-Tracker`, category **Integration**.
3. Search for **BL Car Tracker** in HACS and click **Download**.
4. Restart Home Assistant.

### Method 2: Manual

Copy `custom_components/bl_car_tracker` into your Home Assistant `custom_components` folder and restart.

## ⚙️ Setup

Entirely from the UI: **Settings → Devices & services → Add integration → BL Car Tracker**.

1. Add the integration once, then use its **Add person** and **Add vehicle** buttons.
2. **Person:** a `person.*` entity and the Bluetooth sensor of their phone (the equipment).
3. **Vehicle:** name, Bluetooth MAC address of its on-board device (`AA:BB:CC:DD:EE:FF`, visible in the `paired_devices` attribute of the phone sensor), optional picture (dropped file or URL). A dropped image is copied to `<config>/bl_car_tracker/`, served at `/bl_car_tracker/...` and deleted with the vehicle.
4. Persons and vehicles can be edited or deleted at any time. A MAC address can only be used once.

## 🔄 Upgrading

### From v0.2.0 (one entry per vehicle)

Automatic. On the first start after the update, the old entries are merged into a single **BL Car Tracker** entry: each old entry becomes a vehicle, and the persons of all entries become independent persons. Entity IDs, devices and history are kept. If several old entries listed persons in a different order, the order of the first entry is used.

### From v0.1.0 ("Vehicle Presence")

The domain changed from `vehicle_presence` to `bl_car_tracker`, so the old entries are no longer loaded. Delete them, restart Home Assistant, then add each vehicle again. The position now lives on `device_tracker.<vehicle>`, no longer on the `binary_sensor`.

### From YAML template sensors

Remove the old template `binary_sensor` entities (and their entity registry entries) before adding the vehicle, so the new entities take the same name. In your automations, replace the zone trigger on the old `binary_sensor.<vehicle>` with `device_tracker.<vehicle>`.

## 🏷️ Releases

Semantic versioning. To release: bump `version` in `custom_components/bl_car_tracker/manifest.json`, commit, then publish a new GitHub release with a new `vX.Y.Z` tag (never reuse a tag). HACS offers it as an update.

---

# 🇫🇷 Documentation en Français

Chaque véhicule est identifié par l'appareil Bluetooth qu'il embarque (autoradio, kit mains libres...). Quand un téléphone connu s'y connecte, le véhicule suit cette personne. Quand le téléphone se déconnecte, le véhicule reste là où il est garé.

## ✨ Fonctionnalités

- ⚙️ **100 % configurable depuis l'interface, sans YAML :** véhicule, appareil Bluetooth, personnes et image se règlent dans **Paramètres → Appareils et services**.
- 📍 **`device_tracker` par véhicule :**
  - téléphone connecté : le véhicule copie la position de la personne (latitude, longitude, précision) ;
  - téléphone déconnecté : la dernière position est conservée (la place de stationnement), même après un redémarrage de Home Assistant.
- 🧑 **`binary_sensor` par véhicule (occupation) :** `on` tant que le téléphone d'une personne connue est connecté. L'attribut `connected_person` contient l'entité `person.*` correspondante, ou `null`.
- 🖼️ **Image par glisser-déposer :** déposez une image (PNG, JPG, GIF, WebP) dans le formulaire, ou indiquez une URL.
- 👥 **Personnes et véhicules indépendants :** chaque personne peut piloter la position de tous les véhicules. Si plusieurs téléphones sont connectés au même véhicule, la première personne ajoutée est prioritaire.
- 🚪 **Déclencheurs de zone :** utilisez le `device_tracker` dans vos automatisations, par exemple pour fermer le portail quand la voiture quitte la maison.

Nécessite l'**app Home Assistant Companion pour Android**, qui expose `sensor.<téléphone>_bluetooth_connection` et son attribut `connected_paired_devices` (activez ce capteur dans l'app).

## 📦 Installation

### Méthode 1 : Via HACS (dépôt personnalisé)

1. Dans Home Assistant, ouvrez **HACS** → menu (⋮) → **Dépôts personnalisés**.
2. Ajoutez `https://github.com/Rimfire03/BL-Car-Tracker`, catégorie **Intégration**.
3. Recherchez **BL Car Tracker** dans HACS et cliquez sur **Télécharger**.
4. Redémarrez Home Assistant.

### Méthode 2 : Manuelle

Copiez `custom_components/bl_car_tracker` dans le dossier `custom_components` de Home Assistant et redémarrez.

## ⚙️ Configuration

Entièrement depuis l'interface : **Paramètres → Appareils et services → Ajouter une intégration → BL Car Tracker**.

1. Ajoutez l'intégration une seule fois, puis utilisez ses boutons **Ajouter une personne** et **Ajouter un véhicule**.
2. **Personne :** une entité `person.*` et le capteur Bluetooth de son téléphone (l'équipement).
3. **Véhicule :** nom, adresse MAC Bluetooth de son appareil embarqué (`AA:BB:CC:DD:EE:FF`, visible dans l'attribut `paired_devices` du capteur du téléphone), image optionnelle (fichier déposé ou URL). Une image déposée est copiée dans `<config>/bl_car_tracker/`, servie sur `/bl_car_tracker/...` et supprimée avec le véhicule.
4. Personnes et véhicules peuvent être modifiés ou supprimés à tout moment. Une adresse MAC ne peut être utilisée qu'une fois.

## 🔄 Mise à jour

### Depuis la v0.2.0 (une entrée par véhicule)

Automatique. Au premier démarrage après la mise à jour, les anciennes entrées sont fusionnées en une seule entrée **BL Car Tracker** : chaque ancienne entrée devient un véhicule, et les personnes de toutes les entrées deviennent des personnes indépendantes. Les `entity_id`, appareils et historiques sont conservés. Si d'anciennes entrées listaient les personnes dans un ordre différent, l'ordre de la première entrée est retenu.

### Depuis la v0.1.0 (« Vehicle Presence »)

Le domaine est passé de `vehicle_presence` à `bl_car_tracker` : les anciennes entrées ne sont plus chargées. Supprimez-les, redémarrez Home Assistant, puis ajoutez à nouveau chaque véhicule. La position est désormais sur `device_tracker.<véhicule>`, plus sur le `binary_sensor`.

### Depuis des capteurs template YAML

Supprimez les anciens `binary_sensor` template (et leurs entrées du registre d'entités) avant d'ajouter le véhicule, pour que les nouvelles entités reprennent le même nom. Dans vos automatisations, remplacez le déclencheur de zone sur l'ancien `binary_sensor.<véhicule>` par `device_tracker.<véhicule>`.

## 🏷️ Versions

Versionnage sémantique. Pour publier : incrémenter `version` dans `custom_components/bl_car_tracker/manifest.json`, commiter, puis publier une nouvelle release GitHub avec un nouveau tag `vX.Y.Z` (ne jamais réutiliser un tag). HACS la propose comme mise à jour.

---

## 📄 Licence

Projet open-source sous licence [MIT](LICENSE) - Développé pour la communauté Home Assistant par [Rimfire03](https://github.com/Rimfire03).
