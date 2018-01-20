#!/usr/bin/python3
# -*- coding: UTF-8 -*-


from contextlib import closing
from datetime import timedelta
from json import loads
from re import match, IGNORECASE
from sys import stderr
from time import sleep
from urllib.error import URLError
from urllib.request import urlopen

import config as cfg
from utils import wait_for_internet


def get_channel_list(json_url):
    for attempt_number in range(1, cfg.JSON_SRC_MAX_ATTEMPTS):
        print('Retrieving JSON file, attempt', attempt_number, 'of', cfg.JSON_SRC_MAX_ATTEMPTS, end='\n\n')

        if attempt_number > 1:
            wait_for_internet()

        try:
            with closing(urlopen(json_url, timeout=cfg.CONN_TIMEOUT)) as response:
                response = response.read()

            channel_list = loads(response).get('channels')

            return channel_list
        except URLError as url_error:
            print('Can not retrieve JSON file.', file=stderr)
            print('Error:', url_error, file=stderr)

            if attempt_number < cfg.JSON_SRC_MAX_ATTEMPTS:
                print('Sleeping for', timedelta(seconds=cfg.JSON_SRC_REQ_DELAY), 'before trying again.', end='\n\n',
                      file=stderr)
                sleep(cfg.JSON_SRC_REQ_DELAY)
            else:
                print('Raising an exception.', end='\n\n', file=stderr)
                raise


def replace_categories(channel_list, replace_cats):
    for target_name in replace_cats:
        target_category = replace_cats.get(target_name)

        for current_channel in channel_list:
            current_name = current_channel.get('name')

            if match(target_name, current_name, IGNORECASE):
                current_channel['cat'] = target_category

    return channel_list


def is_channel_allowed(channel, exclude_cats, exclude_names):
    if len(exclude_cats) > 0:
        categories_filter = '(' + ')|('.join(exclude_cats) + ')'

        if match(categories_filter, channel.get('cat'), IGNORECASE):
            return False

    if len(exclude_names) > 0:
        names_filter = '(' + ')|('.join(exclude_names) + ')'

        if match(names_filter, channel.get('name'), IGNORECASE):
            return False

    return True
