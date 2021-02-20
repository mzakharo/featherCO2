import network
import utime as time
import ujson as json
import machine
from umqtt.robust import MQTTClient
import adafruit_sgp30

wdt = machine.WDT()
wdt.feed()

ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('wireless', 'W@terl004ever')
print('connecting to wifi')
count = 0
while not sta_if.isconnected():
    time.sleep(0.1)
    print('.', end='')
    count += 1
    if count < 100:
        wdt.feed()
print('connected.')
print(sta_if.ifconfig())

i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=100000)
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)
print("SGP30 serial #", [hex(i) for i in sgp30.serial])
sgp30.iaq_init()
sgp30.set_iaq_baseline(0x8973, 0x8AAE)
wdt.feed()

def sub_cb(topic, msg):
    print((topic, msg))
con = MQTTClient("umqtt_client", "192.168.50.91")
# Print diagnostic messages when retries/reconnects happens
con.set_callback(sub_cb)
con.connect()
wdt.feed()
#con.subscribe(b"house/sgp30")
con.publish(b'house/sgp30', json.dumps(dict(boot=1)))
try:
    elapsed_sec = 0
    while True:
        #print("eCO2 = %d ppm \t TVOC = %d ppb" % (sgp30.eCO2, sgp30.TVOC))
        d = dict(eCO2=sgp30.eCO2, TVOC=sgp30.TVOC, Ethanol=sgp30.Ethanol, H2=sgp30.H2)
        elapsed_sec += 1
        if elapsed_sec > 10:
            elapsed_sec = 0
            d['baseline_eCO2'] = sgp30.baseline_eCO2
            d['baseline_TVOC'] = sgp30.baseline_TVOC
        print(d)
        con.publish(b'house/sgp30', json.dumps(d), qos=1)
        wdt.feed()
        time.sleep(1)
finally:
    con.disconnect()
