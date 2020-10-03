# Example of Chatbot with temperature sensor

This project structure was initialized with `lifoid init` command.

Build `lifoid_dynamodb` with `Dockerfile` at the root of the git repository:

```bash
docker build -t lifoid_dynamodb .
```

The image `lifoid_dynamodb` is used by a container in `examples/mqtt-automation`:

```bash
docker-compose up
```

In a separate terminal use `mosquitto_pub` tool to simulate information sent
by a temperature sensor:

```
mosquitto_pub -t temperature -m 27.3
```

Then talk to the bot with:

```bash
lifoid mqtt_client

+-----------------------------------------------------------------------------+
|                                                                             |
|   Lifoid                                                                    |
|                                                                             |
|   Copyright (C) 2017-2018 Romary Dupuis                                     |
|                                                                             |
+-----------------------------------------------------------------------------+


* PLease type in your messages below
hello
from simple-bot --> Hello, what is your name?
My name is Bob
from simple-bot --> Hello Bob
What's the temperature today?
from simple-bot --> Temperature is 27.3
```
