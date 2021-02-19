from umqtt.robust import MQTTClient
import network
import utime as time
import ujson as json

from machine import WDT
wdt = WDT()
wdt.feed()

ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('wireless', 'W@terl004ever')
print('connecting to wifi')
while not sta_if.isconnected():
    time.sleep(0.1)
    print('.', end='')
    wdt.feed()
    pass
print('connected.')
print(sta_if.ifconfig())

def sub_cb(topic, msg):
    print((topic, msg))

c = MQTTClient("umqtt_client", "192.168.50.91")
# Print diagnostic messages when retries/reconnects happens
c.DEBUG = True
c.set_callback(sub_cb)

c.subscribe(b"house/sgp30")
while 1:
    try:
        c.publish(b'house/sgp30', json.dumps(dict(foo='bar')))
        c.wait_msg()
    except OSError as e:
        print('err', e)
    time.sleep(1)
    wdt.feed()

c.disconnect()
