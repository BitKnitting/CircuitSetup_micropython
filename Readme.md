
# micropython Library for atm90e32
This library does the same thing the [Circuit Python library](https://github.com/BitKnitting/CircuitSetup_CircuitPython) does.  We can write micropython to talk to the atm90e32.  [An example](Examples/simple_test.py) is included.

__TODO__: I did not implement all the mehods/properties that are in the Arduino port.  I am hoping through Open Source that someone (you?) would like to add more.  

# Thanks to Those That Went Before
There is _so much_ prior work that made it easier to write a CP library for the atm90e32.  Efforts include:   
* Circuit Setup's [Split Single Phase Energy Meter](https://circuitsetup.us/index.php/product/split-single-phase-real-time-whole-house-energy-meter-v1-2/).  I am delighted that John is providing us with this open source energy monitor!  It makes it easy to figure out how much electricity is being used.  Thank you John.  Thank you for helping me get started with your product.
* Tisham Dhar's [atm90e26 Arduino library](https://github.com/whatnick/ATM90E26_Arduino).   Tisham deserves a HUGE THANK YOU for his open source atm90e* hw and sw design. Tisham's excellent work and friendly help are inspirational.
* The [atm90e26 Circuit Python library I wrote](https://github.com/BitKnitting/HappyDay_ATM90e26_CircuitPython)  
* Circuit Setup's [atm90e32 Arduino library](https://github.com/CircuitSetup/Split-Single-Phase-Energy-Meter/tree/master/Software/libraries/ATM90E32)

# Installing micropython on the wemos
I used a wemos D1.
## From the Command Line
The [micropython docs have a tutorial](https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html) on getting micropython onto the esp8266.  We used what is currently the latest ```esp8266-20190529-v1.11.bin```.  


## Installing micropython
### Standard Install
Following [the install instructions](http://docs.micropython.org/en/latest/esp8266/tutorial/intro.html#deploying-the-firmware),   
* erase the flash:
```esptool.py --port /dev/tty.wchusbserial1410 erase_flash```  
* Copy micropython:  
```esptool.py --port /dev/tty.wchusbserial1410 --baud 460800 write_flash --flash_size=detect 0 esp8266-20190125-v1.11.bin```   
### Using uPyCraft
I started using [uPyCraft](http://docs.dfrobot.com/upycraft/).  It is super easy to install micropython from the uPyCraft IDE.
# Talking SPI
The difference between the Circuit Python and micropython libraries is captured in  the ```__init__``` and ```_spi_rw``` methods of [atm90e32_u.py](src/atm90e32_u.py).
