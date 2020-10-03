# lifoid-dynamodb

DynamoDB backend plugin for Lifoid.

## Installation

```bash
pip install lifoid-dynamodb
```

## Development

Use Dockerfile to build an image:

```bash
docker build -t lifoid_dynamodb .
```

The image `lifoid_dynamodb` is used by a container example in `examples/mqtt-automation`:

```bash
docker-compose up
```

Then talk to the bot with:

```bash
lifoid mqtt_client
```

## How to use

Amazon AWS must configured with the Lifoid configuration file.
The `prefix` value points at a table name on DynamoDB service of Amazon AWS.
Names of key and sort_key must configured.

```python
import datetime
from lifoid.data.record import NamedtupleRecord
from lifoid.data.repository import Repository
from lifoid_dynamodb.backend import DynamodbBackend

fields = ['title', 'content']


class Message(namedtuple('Message', fields),
              NamedtupleRecord):
    """
    Example of namedtuple based record
    """
    def __new__(cls, **kwargs):
        default = {f: None for f in fields}
        default.update(kwargs)
        return super(Message, cls).__new__(cls, **default)

class MessagesRepository(Repository):
    klass = Message
    key = 'key'
    sort_key = 'date'

my_repository = MessagesRepository(backend=DynamodbBackend, prefix='messages')
msg1 = Message(title='Message1',
               content='and this is the content')
msg2 = Message(title='Message2',
               content='and this is the content')
now1 = datetime.datetime.utcnow().isoformat()[:-3]
my_repository.save('user-messages',
                   now1, msg1)
now2 = datetime.datetime.utcnow().isoformat()[:-3]
my_repository.save('user-messages',
                   now2, msg2)
record2 = my_repository.latest('user-messages')
record1 = my_repository.get('user-messages', now1)
records1 = my_repository.history('user-messages')
records2 = my_repository.history('user-messages', _from=now1)
records3 = my_repository.history('user-messages', _to=now2, _desc=False)
now3 = datetime.datetime.utcnow().isoformat()[:-3]
records4 = my_repository.history('user-messages', _from=now1, _to=now3)
```
