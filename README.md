### SMS-Extracror

Polls the modem and saves decoded SMS to DB

Идея немного изменилась. Периодически раз в месяц, отправляются служебные sms сами себе, чтоб провайдер видел, что номер активный.
Можно подключить несколько модемов одновременно. Все входящие SMS пересылаются пользователю TG через бота (маппинг пока через таблицу workflow).
Таким образом можно оставлять SIM-карту на время отпуска/командировок дома, не платить за роуминг. Можно выделить один номер для регистраций/смс, на который никто не будет звонить )


Для: Linux Ubuntu 20.04  Modem HUAWEI E1750

### Install

make venv & install libs

classic pip

`python -m venv venv`

`pip install -r requirements.txt --extra-index-url https://nexus.webzaim.tech/repository/pip/simple`

fast uv

`pip install uv==0.6.14`

```bash
uv venv venv --python 3.11
source venv/bin/activate
uv pip install -r requirements.txt
```


### Run

python3 src/modem.py

``
modem = ModemGSM(tty_name='/dev/ttyUSB0', logger=log, sms_saver=CSVSaverRepository)
``

# Для поддержки нескольких модемов

Создайте и заполните таблицу из [init.sql](src/sqls/init.sql)


service_id = APP_MODEM_NAME

external_id  = id ТГ чата, куда бот отправит сообщение