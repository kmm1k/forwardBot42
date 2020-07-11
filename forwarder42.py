import asyncio

from telethon import TelegramClient, events
from telethon.events import NewMessage
import yaml
import logging

loggingFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=loggingFormat)
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


class Forwarder42:
    channel_pairs = []
    bot_name = "bot"

    async def start(self, config):
        self.channel_pairs = config["channel_pairs"]
        self.bot_name = config["bot_name"]
        bot = TelegramClient(config["bot_name"],
                             config["api_id"],
                             config["api_hash"])
        await bot.start(bot_token=config["bot_token"])
        logger.info("loaded configs and starting")

        pattern_to_match = f'(?i)@{self.bot_name}.+'

        @bot.on(events.NewMessage(pattern=pattern_to_match))
        async def handler(event: NewMessage.Event):
            logger.info(event)
            response = event.text.replace(f'@{self.bot_name}', "")

            target_id = 0
            for i in self.channel_pairs:
                if i[0] == event.chat_id:
                    target_id = i[1]

            if target_id != 0:
                await bot.send_message(target_id, response)

        await bot.run_until_disconnected()


if __name__ == "__main__":
    with open('config.yml', 'rb') as f:
        config = yaml.safe_load(f)
    logger.info("init")
    forwarder = Forwarder42()
    asyncio.run(forwarder.start(config))
