import time, logging

mqtt_log = logging.getLogger('mqtt')
mqtt_log.setLevel(logging.DEBUG)

# documentation: https://www.eclipse.org/paho/clients/python/docs/
import paho.mqtt.client as mqtt

# documentation: https://mqtt.ideate.cmu.edu/
hostname = "mqtt.ideate.cmu.edu"
portnum = 8884

# MQTT server thread callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected to server with with flags: %s, result code: %s" % (flags, rc))
    client.subscribe("#")

def on_message(client, userdata, msg):
    print("{%s} %s" % (msg.topic, msg.payload))

def on_log(client, userdata, level, buf):
    logging.debug("on_log level %s: %s", level, userdata)

    
# Create a default MQTT object to connect to the remote broker server.
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log
client.enable_logger(mqtt_log)

# Set up TLS
client.tls_set()
client.username_pw_set("students", "cks")

# Connect to a remote broker. Some other default args: port=1883, keepalive=60
client.connect_async(host=hostname, port=portnum)

# Start a background thread to process network traffic.
client.loop_start()

# Idle until the server completes the connection
while not client.is_connected():
    print (".")
    time.sleep(0.1)
    
# Send a sequence of updates.
for count in range(10):
    
    # Publish a message on a topic.  The message is always a string; passing an
    # integer converts it to a string representation.
    # Some other defaults args: qos=0, retain=False
    client.publish(topic="mytesttopic", payload="ping%d" % count)
    time.sleep(1)
    
# Disconnect cleanly from the broker server.
client.loop_stop()
client.disconnect()