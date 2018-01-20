#!/usr/bin/python3
# -*- coding: UTF-8 -*-


from codecs import open
from datetime import datetime
from datetime import timedelta
from os import makedirs
from os.path import dirname
from socket import gethostname, gethostbyname
from sys import stderr
from time import sleep
from traceback import print_exc, format_exc

import config as cfg
from channel_handler import get_channel_list, is_channel_allowed, replace_categories
from utils import wait_for_internet, send_email


def write_entry(out_file, out_file_format, channel):
    entry = out_file_format \
        .replace('{CATEGORY}', channel.get('cat')) \
        .replace('{NAME}', channel.get('name')) \
        .replace('{CONTENT_ID}', channel.get('url'))
    out_file.write(entry)


def main():
    while True:
        print('Started at', datetime.now().strftime('%b %d %H:%M:%S'), end='\n\n')

        wait_for_internet()

        data_set_number = 0

        for data_set in cfg.DATA_SETS:
            data_set_number += 1
            print('Processing data set', data_set_number, 'of', len(cfg.DATA_SETS))

            json_url = data_set.get('JSON_URL')
            out_file = data_set.get('OUT_FILE_NAME')
            out_file_first_line = data_set.get('OUT_FILE_FIRST_LINE')
            out_file_format = data_set.get('OUT_FILE_FORMAT')
            replace_cats = data_set.get('REPLACE_CATS')
            exclude_cats = data_set.get('EXCLUDE_CATS')
            exclude_names = data_set.get('EXCLUDE_NAMES')

            makedirs(dirname(out_file), exist_ok=True)
            out_file = open(out_file, 'w', 'utf-8')
            out_file.write(out_file_first_line)

            total_channel_count = 0
            allowed_channel_count = 0

            channel_list = get_channel_list(json_url)
            channel_list = replace_categories(channel_list, replace_cats)
            channel_list.sort(key=lambda x: x.get('cat'))

            for channel in channel_list:
                total_channel_count += 1

                if is_channel_allowed(channel, exclude_cats, exclude_names):
                    write_entry(out_file, out_file_format, channel)
                    allowed_channel_count += 1

            out_file.close()

            print('Playlist', data_set.get('OUT_FILE_NAME'), 'successfully generated.')
            print('Channels processed in total:', total_channel_count)
            print('Channels allowed:', allowed_channel_count)
            print('Channels denied:', total_channel_count - allowed_channel_count)

            if data_set_number < len(cfg.DATA_SETS):
                print('Sleeping for', timedelta(seconds=cfg.DATA_SET_DELAY), 'before processing next data set...')
                sleep(cfg.DATA_SET_DELAY)

            print('')

        print('Finished at', datetime.now().strftime('%b %d %H:%M:%S'))
        print('Sleeping for', timedelta(seconds=cfg.UPDATE_DELAY), 'before the new update...')
        print('-' * 45, end='\n\n\n')
        sleep(cfg.UPDATE_DELAY)


# Main entry point
if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        main()
    except Exception:
        print_exc()

        if cfg.NOTIFY:
            print('Sending notification.', file=stderr)
            send_email('M3UGenerator has crashed on ' + gethostname() + '@' + gethostbyname(gethostname()),
                       format_exc())

        if cfg.PAUSE:
            input('Press <Enter> to exit...')

        exit(1)
