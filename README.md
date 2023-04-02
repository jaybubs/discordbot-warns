# discordbot-warn

Simple warn system implementable into discord bots. This solution leverages [pocketbase](https://pocketbase.io) as it comes with an extremely convenient rest api out of the box.

You will need to create a `config.py` and supply the following credentials:

```
discord_bot_token="<token>"
pb_identity="<admin email>"
pb_password="hunter2"
```

The commands api is directly documented in `command.py`
