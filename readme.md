### The idea of this script is to forward messages from one Telegram group to another.

### Usage:
```
Group 1:  
@your_bot_name text you want to forward  
Group 2:  
Your_bot_name: text you want to forward #bot will output this text
```

### Setup
1) install python 3.6+
2) run `make install` or `pip install -r requirements.txt`
3) create a file named config.yml using sample_config.yml
4) create a Telegram bot using botFather, paste the given bot token to the config.yml, also put the name of your bot there
5) use botFather to turn off privacy of the bot
6) obtain api keys from https://core.telegram.org/api/obtaining_api_id and paste them to config.yml
7) add your bot to the group chats
8) get the group chat id's and place them into the config.yml as shown in the sample_config.yml
9) run `make run` or `python forwarder42.py`
