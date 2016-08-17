# garage-butler
Program to manage your garage doors with a Raspberry Pi.

## Features
* Open/close status
* Remote open and close
* SMS notification(via Amazon Web Services SNS) if the garage door is open too long
* Image capture on open
* Image capture on demand

## Hardware
* Raspberry Pi 3 (any pi with network connnectivity will work)
  * Mobel B recommend since the software references GPIO 16,19
* 5v relay
  * I use this one:  https://amzn.com/B00E0NTPP4
* Magnetic switch
  * I use this one:  https://amzn.com/B000GUSNQW
  
