"""Constants for the BL Car Tracker integration."""

DOMAIN = "bl_car_tracker"

SUBENTRY_VEHICLE = "vehicle"
SUBENTRY_PERSON = "person"

CONF_MAC = "mac_address"
CONF_PICTURE = "picture"
CONF_PICTURE_FILE = "picture_file"
CONF_PHONE_SENSOR = "phone_sensor"
CONF_PERSON = "person"

MEDIA_DIR = "bl_car_tracker"  # under the Home Assistant config directory
MEDIA_URL = "/bl_car_tracker"

ATTR_CONNECTED_PERSON = "connected_person"
# Attribute exposed by the Home Assistant Companion app's Bluetooth sensor.
ATTR_CONNECTED_PAIRED_DEVICES = "connected_paired_devices"
