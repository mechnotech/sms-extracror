import configparser


class ExtraConfig:

    def __init__(self, minutes_left_default: int):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.minutes_left_default = minutes_left_default
        try:
            self.wf = self.config['workflow']
            self.min_left = int(self.wf['minutesleft'])
        except KeyError:
            self.config['workflow'] = {'minutesleft': str(minutes_left_default)}
            self.min_left = int(self.config['workflow']['minutesleft'])
            self._save()

    def _save(self):
        with open('config.ini', 'w') as f:
            self.config.write(f)

    def decrease(self):
        self.min_left -= 1
        self.config['workflow']['minutesleft'] = str(self.min_left)
        self._save()

    def reset(self):
        self.config['workflow']['minutesleft'] = str(self.minutes_left_default)
        self.min_left = self.minutes_left_default
        self._save()