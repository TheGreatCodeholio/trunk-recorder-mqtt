import time
from colorama import Fore, Back, Style
import paho.mqtt.client as mqtt

# MQTT settings
MQTT_BROKER = 'mercury.icarey.net'  # Example: 'mqtt.example.com'
MQTT_PORT = 1883  # Default port for MQTT
MQTT_TOPIC = 'trunk_recorder/feeds/audio'  # Subscribes to all topics starting with 'trunk_recorder'
MQTT_USERNAME = 'trunk_recorder'  # MQTT username
MQTT_PASSWORD = '4Ij29R&RaSkVgwhx'  # MQTT password


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)  # Subscribe to the topic on successful connect


def on_message(client, userdata, msg):
    print(f"Topic: {Fore.LIGHTGREEN_EX}{msg.topic}{Style.RESET_ALL} Message: {msg.payload.decode()}")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    try:
        client.on_connect = on_connect
        client.on_message = on_message

        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        client.connect(MQTT_BROKER, MQTT_PORT, 60)

        # Process network traffic and dispatch callbacks
        client.loop_start()

        # Run indefinitely or until some condition or input requests termination
        while True:
            time.sleep(1)  # Sleep to allow signal handling or simple background processing

    except KeyboardInterrupt:
        # Handle graceful exit when an interrupt signal is received (e.g., CTRL+C)
        print("Disconnecting from broker...")
    finally:
        client.loop_stop()  # Stop the loop that handles callbacks
        client.disconnect()  # Disconnect gracefully


if __name__ == '__main__':
    main()
