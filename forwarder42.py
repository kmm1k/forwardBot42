import asyncio
import time

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

    def _save_tag_data(self, config):
        with open('config.yml', 'w') as f:
            yaml.safe_dump(config, f)

    def _get_tag_index(self, tag_name):
        tag_index = -1
        for tag_line in config["tags"]:
            for list_tag_name in tag_line:
                tag_index = tag_index + 1
                if tag_name == list_tag_name:
                    return tag_index
        return tag_index


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
        help_pattern = f'\/help'
        tag_create_pattern = f'\/tagcreate.+'
        tag_user_pattern = f'\/taguser.+'
        tag_remove_pattern = f'\/tagremove.+'
        tag_remove_user_pattern = f'\/tagrmuser.+'
        tag_list_pattern = f'\/taglist'
        at_tag_pattern = f'(?i)@.+'

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
                self._save_tag_data(config)
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
                self._save_tag_data(config)
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
                    await bot.send_message(source_id, 'Booked!')

            for i in self.channel_pairs:
                if i[1] == event.chat_id:
                    target_id = i[0]
                    source_id = i[1]
                    await bot.send_message(source_id, 'sent message back to origin group')

            if target_id != 0:
                if event.reply_to_msg_id:
                    await bot.forward_messages(target_id, event.reply_to_msg_id, source_id)
                    time.sleep(2)
                await bot.forward_messages(target_id, event.id, source_id)
                logger.info('messages sent out')

        @bot.on(events.NewMessage(pattern=help_pattern))
        async def handler(event: NewMessage.Event):
            logger.info(event)
            await bot.send_message(event.chat_id, f'this bot contains forwarder: \n'
                                                  f'/fblist - displays all the forwarded chats [input, output] \n'
                                                  f'/fbadd [input_chat_id] [output_chat_id] - add a forward \n'
                                                  f'/fbremove [input_chat_id] [output_chat_id] - remove forward \n'
                                                  f'@botname [message] forwards this message \n'
                                                  f' \n'
                                                  f'and tags: \n'
                                                  f'/tagcreate [tag_name] - create tag with tag_name \n'
                                                  f'/taguser [username] [tag_name] - add username to tag_name tag \n'
                                                  f'/tagremove [tag_name] - removes tag \n'
                                                  f'/tagrmuser [username] [tag_name] - removes user from tag \n'
                                                  f'/taglist - shows the tags info \n'
                                                  f'use @tag_name to display the tags')

        @bot.on(events.NewMessage(pattern=tag_list_pattern))
        async def handler(event: NewMessage.Event):
            logger.info(event)
            await bot.send_message(event.chat_id, f'tags {config["tags"]}')

        @bot.on(events.NewMessage(pattern=tag_create_pattern))
        async def handler(event: NewMessage.Event):
            if str(event.to_id.user_id) in config["bot_token"]:
                logger.info(event)
                request = event.text.replace(f'/tagcreate ', "")
                config["tags"].append({request: []})
                self._save_tag_data(config)
                await bot.send_message(event.chat_id, f'tags {config["tags"]}')

        @bot.on(events.NewMessage(pattern=tag_user_pattern))
        async def handler(event: NewMessage.Event):
            if str(event.to_id.user_id) in config["bot_token"]:
                logger.info(event)
                request = event.text.replace(f'/taguser ', "")
                username, tag_name = request.split(" ")
                tag_index = self._get_tag_index(tag_name)
                if tag_index != -1:
                    config["tags"][tag_index][tag_name].append(username)
                    self._save_tag_data(config)
                    await bot.send_message(event.chat_id, f'tags {config["tags"]}')
                else:
                    await bot.send_message(event.chat_id, f'{tag_name} tag does not exist, create tag with /tagcreate {tag_name}')

        @bot.on(events.NewMessage(pattern=tag_remove_user_pattern))
        async def handler(event: NewMessage.Event):
            if str(event.to_id.user_id) in config["bot_token"]:
                logger.info(event)
                request = event.text.replace(f'/tagrmuser ', "")
                username, tag_name = request.split(" ")
                tag_index = self._get_tag_index(tag_name)
                if tag_index != -1:
                    config["tags"][tag_index][tag_name].remove(username)
                    self._save_tag_data(config)
                    await bot.send_message(event.chat_id, f'tags {config["tags"]}')
                else:
                    await bot.send_message(event.chat_id, f'{tag_name} tag does not exist, create tag with /tagcreate {tag_name}')

        @bot.on(events.NewMessage(pattern=tag_remove_pattern))
        async def handler(event: NewMessage.Event):
            if str(event.to_id.user_id) in config["bot_token"]:
                logger.info(event)
                request = event.text.replace(f'/tagremove ', "")
                tag_index = self._get_tag_index(request)
                if tag_index != -1:
                    config["tags"].remove(config["tags"][tag_index])
                    self._save_tag_data(config)
                    await bot.send_message(event.chat_id, f'tags {config["tags"]}')
                else:
                    await bot.send_message(event.chat_id, f'tag was not removed, because it was not found')

        @bot.on(events.NewMessage(pattern=at_tag_pattern))
        async def handler(event: NewMessage.Event):
            logger.info(event)
            request = event.text.replace(f'@', "")
            tag_text = ""
            has_tag = False

            for tag_line in config["tags"]:
                for tag_name in tag_line:
                    if tag_name == request:
                        has_tag = True
                        for user in tag_line[tag_name]:
                            tag_text = tag_text + f'@{user} '

            if has_tag:
                await bot.send_message(event.chat_id, tag_text)

        await bot.run_until_disconnected()


if __name__ == "__main__":
    with open('config.yml', 'rb') as f:
        config = yaml.safe_load(f)
    logger.info("init")
    forwarder = Forwarder42()
    # forwarder.testing(config)
    asyncio.run(forwarder.start(config))
