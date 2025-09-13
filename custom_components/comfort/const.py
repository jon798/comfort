"""Constants for comfort integration."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "comfort"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
COMFORT_IP = "Comfort (ETH02 or ETH03) IP address"
COMFORT_PORT = "Comfort (ETH02 or ETH03) Port"
COMFORT_PIN = "Login PIN for Integration to use"
COMFORT_TIMEOUT = "Comfort ETH/UCM Timeout"
COMFORT_RETRY = "Comfort Retry interval"
BUFFER_SIZE = "Comfort receive buffer size"
