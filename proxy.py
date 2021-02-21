import paho.mqtt.client as mqtt
import time
import queue
import json

influx_token = 'QyPrOXP8rillSdl_5-hI9y2WuSxK7P5Smha3ALKXcnTrw9zrzvXJ8jxJhdhsqFFG8N4OPJwx0S6QgpOMD26p-w=='
influx_url = "https://us-central1-1.gcp.cloud2.influxdata.com"
influx_org  = "d5c111f1b4fc56c1"
influx_bucket  = "main"

import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision, rest
from influxdb_client.client.write_api import SYNCHRONOUS
import urllib3
from urllib3 import Retry

retries = Retry(connect=3, read=2, redirect=3)
inf_client = InfluxDBClient(url=influx_url, token=influx_token, timeout=10, retries=retries, enable_gzip=True)
write_api = inf_client.write_api(write_options=SYNCHRONOUS)

q = queue.Queue()

def on_message(client, userdata, message):
    print('on message', message.topic)
    data = json.loads(message.payload.decode("utf-8"))
    q.put(data)

def on_connect(client, a, b, c):
    client.subscribe('house/sgp30', qos=0)

client =mqtt.Client()
client.connect_async('192.168.50.91')
client.on_message = on_message
client.on_connect = on_connect
client.loop_start()

while True:
    data = q.get()
    print("message received " , data)
    send_buffer = []
    for k, v in data.items():
        point = Point('butch').field(k, v).time(int(time.time() * 1000), WritePrecision.MS)
        send_buffer.append(point)
    try:
        write_api.write(influx_bucket, influx_org, send_buffer)
    except Exception as e:
        print('Exception', e)
