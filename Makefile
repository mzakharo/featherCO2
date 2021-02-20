
install:
	ampy --port /dev/ttyUSB0 put main.py
erase:
	esptool.py --port /dev/ttyUSB0 erase_flash
firmware:
	esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 firmware-combined.bin
