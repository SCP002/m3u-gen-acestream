#!/usr/bin/python3
# -*- coding: UTF-8 -*-


from codecs import open
from contextlib import closing
from datetime import timedelta
from json import loads, load
from re import match, IGNORECASE
from sys import stderr
from time import sleep
from urllib.error import URLError
from urllib.request import urlopen

import config as cfg
from utils import wait_for_internet


def get_channel_list(data_set):
    json_url = data_set.get('JSON_URL')
    resp_encoding = data_set.get('RESP_ENCODING')

    for attempt_number in range(1, cfg.JSON_SRC_MAX_ATTEMPTS):
        print('Retrieving JSON file, attempt', attempt_number, 'of', cfg.JSON_SRC_MAX_ATTEMPTS, end='\n\n')

        if attempt_number > 1:
            wait_for_internet()

        try:
            with closing(urlopen(json_url, timeout=cfg.CONN_TIMEOUT)) as response:
                response = response.read().decode(resp_encoding)

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


def replace_categories(channel_list, data_set):
    with closing(open(data_set.get('FILTER_FILE_NAME'), 'r', data_set.get('FILTER_FILE_ENCODING'))) as filter_file:
        filter_contents = load(filter_file)

    replace_cats = filter_contents.get('replace_cats')

    replaced = False

    for replace_cat in replace_cats:
        target_name = replace_cat.get('for_name')
        target_category = replace_cat.get('to_cat')

        for channel in channel_list:
            current_name = channel.get('name')
            current_category = channel.get('cat')

            if match(target_name, current_name, IGNORECASE) and not current_category == target_category:
                channel['cat'] = target_category
                replaced = True
                print('Replaced category for channel "' + current_name + '", from "' + current_category + '" to "' +
                      target_category + '".')

    if replaced:
        print()

    return channel_list


def is_channel_allowed(channel, data_set):
    with closing(open(data_set.get('FILTER_FILE_NAME'), 'r', data_set.get('FILTER_FILE_ENCODING'))) as filter_file:
        filter_contents = load(filter_file)

    exclude_cats = filter_contents.get('exclude_cats')

    if len(exclude_cats) > 0:
        categories_filter = '(' + ')|('.join(exclude_cats) + ')'

        if match(categories_filter, channel.get('cat'), IGNORECASE):
            return False

    exclude_names = filter_contents.get('exclude_names')

    if len(exclude_names) > 0:
        names_filter = '(' + ')|('.join(exclude_names) + ')'

        if match(names_filter, channel.get('name'), IGNORECASE):
            return False

    return True


def write_entry(channel, data_set, out_file):
    out_file_format = data_set.get('OUT_FILE_FORMAT')

    entry = out_file_format \
        .replace('{CATEGORY}', channel.get('cat')) \
        .replace('{NAME}', channel.get('name')) \
        .replace('{CONTENT_ID}', channel.get('url'))

    out_file.write(entry)
