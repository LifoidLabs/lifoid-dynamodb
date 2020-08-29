# -*- coding: utf8 -*-
"""
Dynamodb backend plugin for Lifoid
Author: Romary Dupuis <romary@me.com>
"""
from lifoid import signals
from .config import DynamoDBConfiguration
from .backend import DynamodbBackend

__version__ = '0.1.0'


def get_backend(app):
    return DynamodbBackend


def get_conf(configuration):
    setattr(configuration, 'dynamodb', DynamoDBConfiguration())


def register():
    signals.get_backend.connect(get_backend)
    signals.get_conf.connect(get_conf)
