import configparser

from repositories.saver import PostgresSaverRepository
from settings import Settings


class ExtraConfig:

    def __init__(self, minutes_left_default: int):
        self.config = configparser.ConfigParser()
        self.config.read('config/config.ini')
        self.minutes_left_default = minutes_left_default
        try:
            self.wf = self.config['workflow']
            self.min_left = int(self.wf['minutesleft'])
        except KeyError:
            self.config['workflow'] = {'minutesleft': str(minutes_left_default)}
            self.min_left = int(self.config['workflow']['minutesleft'])
            self._save()

    def _save(self):
        with open('config.ini/config.ini', 'w') as f:
            self.config.write(f)

    def decrease(self):
        self.min_left -= 1
        self.config['workflow']['minutesleft'] = str(self.min_left)
        self._save()

    def reset(self):
        self.config['workflow']['minutesleft'] = str(self.minutes_left_default)
        self.min_left = self.minutes_left_default
        self._save()

class PGExtraConfig(ExtraConfig):

    def __init__(self, minutes_left_default: int, config: Settings, pg_conn: PostgresSaverRepository):
        super().__init__(minutes_left_default)

        self.config = config
        self.pg_conn = pg_conn
        self.minutes_left_default = minutes_left_default
        self.name = self.config.app_modem_name
        self.min_left = self.read_left()
        if not self.min_left:
            self.set_new_record()

    def read_left(self):
        # Прочитать из базы сколько минут осталось до действия

        raw_row = self.pg_conn.read_sql(f"select * from service.workflow where service_id = '{self.name}';")
        if raw_row and len(raw_row) > 1:
            return int(raw_row[1])

    def set_new_record(self):
        sql = f"insert into service.workflow (service_id, minutes_left) values ('{self.name}', {self.minutes_left_default});"
        self.pg_conn.execute_sql(sql)

    def _save(self):
        sql = f"update service.workflow set minutes_left = {self.min_left} where service_id = '{self.name}'"
        self.pg_conn.execute_sql(sql)

    def decrease(self):
        self.min_left -= 1
        self._save()

    def reset(self):
        self.min_left = self.minutes_left_default
        self._save()