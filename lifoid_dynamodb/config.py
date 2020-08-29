# -*- coding: utf8 -*-
"""
Dynamodb plugin configuration
Author: Romary Dupuis <romary@me.com>
"""
from lifoid.config import Configuration, environ_setting


class DynamoDBConfiguration(Configuration):
    """
    Dynamodb configuration
    """
    endpoint = environ_setting('DYNAMODB_ENDPOINT', None, required=False)
    region = environ_setting('DYNAMODB_REGION', 'eu-west-1', required=False)
