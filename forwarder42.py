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

        at_bot_pattern = f'(?i)@{self.bot_name}.+'
        adding_pattern = f'\/fbadd.+'
        remove_pattern = f'\/fbremove.+'
        list_pattern = f'\/fblist'

        @bot.on(events.NewMessage(pattern=list_pattern))
        async def handler(event: NewMessage.Event):
            logger.info(event)
            if str(event.to_id.user_id) in config["bot_token"]:
                await bot.send_message(event.chat_id, f'config channel pairs {config["channel_pairs"]}')

        @bot.on(events.NewMessage(pattern=adding_pattern))
        async def handler(event: NewMessage.Event):
            logger.info(event)
            if str(event.to_id.user_id) in config["bot_token"]:
                add_request = event.text.replace(f'/fbadd ', "")
                add_request = add_request.replace(',', "")
                add_request = add_request.replace('g', "-")
                ids = add_request.split(" ")
                source = int(ids[0])
                target = int(ids[1])
                config["channel_pairs"].append([source, target])
                with open('config.yml', 'w') as f:
                    yaml.safe_dump(config, f)
                self.channel_pairs = config["channel_pairs"]
                await bot.send_message(event.chat_id, f'added chat id\'s input: {source}, output: {target}')
                await bot.send_message(event.chat_id, f'config channel pairs {config["channel_pairs"]}')

        @bot.on(events.NewMessage(pattern=remove_pattern))
        async def handler(event: NewMessage.Event):
            logger.info(event)
            if str(event.to_id.user_id) in config["bot_token"]:
                add_request = event.text.replace(f'/fbremove ', "")
                add_request = add_request.replace(',', "")
                add_request = add_request.replace('g', "-")
                ids = add_request.split(" ")
                source = int(ids[0])
                target = int(ids[1])
                config["channel_pairs"].remove([source, target])
                with open('config.yml', 'w') as f:
                    yaml.safe_dump(config, f)
                self.channel_pairs = config["channel_pairs"]
                await bot.send_message(event.chat_id, f'removed chat id\'s input: {source}, output: {target}')
                await bot.send_message(event.chat_id, f'config channel pairs {config["channel_pairs"]}')

        @bot.on(events.NewMessage(pattern=at_bot_pattern))
        async def handler(event: NewMessage.Event):
            logger.info(event)

            target_id = 0
            source_id = 0
            for i in self.channel_pairs:
                if i[0] == event.chat_id:
                    target_id = i[1]
                    source_id = i[0]

            if target_id != 0:
                await bot.send_message(source_id, 'Booked!')
                await bot.forward_messages(target_id, event.id, source_id)
                if event.reply_to_msg_id:
                    await bot.forward_messages(target_id, event.reply_to_msg_id, source_id)
                logger.info('messages sent out')

        await bot.run_until_disconnected()


if __name__ == "__main__":
    with open('config.yml', 'rb') as f:
        config = yaml.safe_load(f)
    logger.info("init")
    forwarder = Forwarder42()
    asyncio.run(forwarder.start(config))
