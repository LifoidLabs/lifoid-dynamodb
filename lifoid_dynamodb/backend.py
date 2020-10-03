import json
import boto3
from boto3.dynamodb.conditions import Key
from awesomedecorators import memoized
from lifoid.data.backend import Backend
from lifoid.config import settings
from lifoid.logging.mixin import LoggingMixin


class DynamodbBackend(Backend, LoggingMixin):
    """
    Backend based on DynamoDB
    """

    def __init__(self, prefix, secondary_indexes, key='key', sort_key='date'):
        """
        `prefix` must correspond to a table name on DynamoDB AWS Dynamodb.
        Key and sort_key must configured.
        """
        self._prefix = prefix
        self._secondary_indexes = secondary_indexes
        self._key = key
        self._sort_key = sort_key

    @memoized
    def table(self):
        if settings.dynamodb.endpoint is not None:
            self.logger.debug('endpoint {}'.format(settings.dynamodb.endpoint))
            dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url=settings.dynamodb.endpoint,
                region_name=settings.dynamodb.region
            )
        else:
            dynamodb = boto3.resource(
                'dynamodb',
                region_name=settings.dynamodb.region
            )

        existing_tables = dynamodb.tables.all()
        self.logger.debug('{}'.format(existing_tables))
        for existing_table in existing_tables:
            if existing_table == self._prefix:
                return dynamodb.Table(self._prefix)

        # table is not available so we create it
        self.logger.debug('table {} is not available so we create it'.format(self._prefix))
        new_table = dynamodb.create_table(
            TableName=self._prefix,
            KeySchema=[
                {
                    'AttributeName': self._key,
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': self._sort_key,
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': self._key,
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': self._sort_key,
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        # Wait for creation of table
        new_table.meta.client.get_waiter('table_exists').wait(TableName=self._prefix)
        return new_table

    def get(self, key, sort_key):
        query = {
            self._key: self.prefixed(key),
        }
        if sort_key is not None:
            query.update({
                self._sort_key: sort_key
            })
        self.logger.debug('Storage - get {}'.format(query))
        res = self.table.get_item(Key=query)
        if 'Item' in res and 'value' in res['Item']:
            return res['Item']['value']

    def set(self, key, sort_key, value):
        self.logger.debug('Storage - set value {} for {}'
                          .format(value,
                                  self.prefixed(key)))
        item = {
            self._key: self.prefixed(key),
            'value': value
        }
        obj = json.loads(value)
        for index in self._secondary_indexes:
            if obj.get(index, None) not in ['', None]:
                item.update({
                    index: obj[index]
                })
        if sort_key is not None:
            item.update({
                self._sort_key: sort_key
            })
        return self.table.put_item(Item=item)

    def delete(self, key, sort_key):
        self.logger.debug('Storage - delete {}'.format(self.prefixed(key)))
        query = {
            self._key: self.prefixed(key),
        }
        if sort_key is not None:
            query.update({
                self._sort_key: sort_key
            })
        return self.table.delete_item(Key=query)

    def history(self, key, _from='-', _to='+', _desc=True):
        if _from != '-':
            response = self.table.query(
                KeyConditionExpression=Key(self._key)
                .eq(self.prefixed(key)) &
                Key(self._sort_key)
                .gt(_from),
                Limit=100
            )
            return [item['value'] for item in response['Items']]
        if _to != '+':
            response = self.table.query(
                KeyConditionExpression=Key(self._key)
                .eq(self.prefixed(key)) &
                Key(self._sort_key)
                .lt(_to),
                Limit=100,
                ScanIndexForward=False
            )
            return [item['value'] for item in response['Items']]
        return []

    def latest(self, key):
        self.logger.debug('Storage - get latest for {}'.format(
            self.prefixed(key)
        ))
        response = self.table.query(
            KeyConditionExpression=Key(self._key)
            .eq(self.prefixed(key)),
            Limit=1,
            ScanIndexForward=False
        )
        if len(response['Items']) > 0:
            return response['Items'][0]['value']
        else:
            return None

    def find(self, index, value):
        res = self.table.query(
            KeyConditionExpression=Key(index).eq(value),
            IndexName='{}-index'.format(index)
        )
        self.logger.debug('{}'.format(res))
        return {
            'count': res['Count'],
            'items': [item['value'] for item in res['Items']]
        }
