from umqtt.robust import MQTTClient
import network
import utime as time
import ujson as json
import machine

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


echo = 10
def sub_cb(topic, msg):
    global echo
    echo = 10
    print((topic, msg))
con = MQTTClient("umqtt_client", "192.168.50.91")
# Print diagnostic messages when retries/reconnects happens
con.set_callback(sub_cb)
con.connect()
wdt.feed()

# construct an I2C bus
i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4), freq=100000)

import adafruit_sgp30
# Create library object on our I2C port
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

print("SGP30 serial #", [hex(i) for i in sgp30.serial])

sgp30.iaq_init()
wdt.feed()
sgp30.set_iaq_baseline(0x8973, 0x8AAE)

elapsed_sec = 0
wdt.feed()
con.subscribe(b"house/sgp30")
while True:
    #print("eCO2 = %d ppm \t TVOC = %d ppb" % (sgp30.eCO2, sgp30.TVOC))
    d = dict(eCO2=sgp30.eCO2, TVOC=sgp30.TVOC, Ethanol=sgp30.Ethanol, H2=sgp30.H2)
    elapsed_sec += 1
    if elapsed_sec > 10:
        elapsed_sec = 0
        d['baseline_eCO2'] = sgp30.baseline_eCO2
        d['baseline_TVOC'] = sgp30.baseline_TVOC
    print(d)
    try:
        echo -= 1
        con.publish(b'house/sgp30', json.dumps(d))
        con.wait_msg()
        if echo > 0:
            wdt.feed()
    except OSError as e:
        print('err', e)
    time.sleep(1)

c.disconnect()
