# -*- coding: utf8 -*-
"""
Rasa_nlu plugin configuration
Author: Romary Dupuis <romary@me.com>
"""
from lifoid.config import Configuration, environ_setting


class DynamoDBConfiguration(Configuration):
    """
    Dynamodb configuration
    """
