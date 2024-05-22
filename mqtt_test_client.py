import base64
import json
import os
import time
from datetime import datetime

from colorama import Fore, Back, Style
import paho.mqtt.client as mqtt

# MQTT settings
MQTT_BROKER = ''  # Example: 'mqtt.example.com'
MQTT_PORT = 1883  # Default port for MQTT
MQTT_TOPIC = 'trunk_recorder/#'  # Subscribes to all topics starting with 'trunk_recorder'
MQTT_USERNAME = 'trunk_recorder'  # MQTT username
MQTT_PASSWORD = ''  # MQTT password


def save_files(wav_data, metadata):
    # Get the current date
    current_date = datetime.utcnow()

    # Create folder structure using current date
    folder_path = os.path.join("audio", metadata.get("short_name", "unknown"), str(current_date.year), str(current_date.month), str(current_date.day))
    os.makedirs(folder_path, exist_ok=True)

    # You can now use the wav_data as a binary stream
    with open(os.path.join(folder_path, metadata["call_filename"]), "wb") as wav_file, open(
            os.path.join(folder_path, metadata["call_filename"].replace(".wav", ".json")), "w") as json_file:
        wav_file.write(wav_data)
        json.dump(metadata, json_file, indent=4)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)  # Subscribe to the topic on successful connect


def on_message(client, userdata, msg):
    if msg.topic == 'trunk_recorder/feeds/audio':
        data = json.loads(msg.payload)
        call_data = data.get("call", {})
        wav_data = base64.b64decode(call_data.get("audio_wav_base64", ""))
        metadata = call_data.get("metadata", {})

        save_files(wav_data, metadata)

        print(f"Saved Audio")


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
