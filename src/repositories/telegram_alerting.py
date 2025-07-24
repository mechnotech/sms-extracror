import re
from logging import Logger
from urllib.parse import urlencode

import aiohttp

from settings import Settings


class TelegramAlerting:

    def __init__(self, config: Settings, logger: Logger):
        self.logger = logger
        self.api_key = config.app_message_creds
        self.chat_id = None
        self.url = f'https://api.telegram.org/bot{self.api_key}/sendMessage'
        self.dummy_send = False
        self.pattern = r'[_[\]()~>#\+\-=|{}.!]'

    async def send(self, message: str):
        if self.dummy_send:
            self.logger.warning('Dummy Telegram send: {}'.format(message))
            return
        message = re.sub(self.pattern, lambda x: '\\' + x.group(), message)
        params = {'chat_id': int(self.chat_id), 'text': message, 'parse_mode': 'MarkdownV2'}
        patch_params = urlencode(params, encoding='utf-8')

        url = self.url + '?' + patch_params
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=url) as r:
                    if r.status != 200:
                        self.logger.warning(f'TG-bot message not delivered - status {r.status}')
                    return r.status

        except Exception as e:
            self.logger.warning(f'TG-bot connection error - {e}')
            return
