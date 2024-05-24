### SMS-Extracror

Polls the modem and saves decoded SMS to csv

Linux Ubuntu 20.04
Modem HUAWEI E1750

### Install

make venv & install libs
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run

python3 src/modem.py

``
modem = ModemGSM(tty_name='/dev/ttyUSB0', logger=log, sms_saver=CSVSaverRepository)
``

