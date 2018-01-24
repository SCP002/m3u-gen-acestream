#!/usr/bin/python3
# -*- coding: UTF-8 -*-


from codecs import open
from contextlib import closing
from datetime import datetime
from datetime import timedelta
from os import makedirs
from os.path import dirname
from socket import gethostname, gethostbyname
from sys import stderr
from time import sleep
from traceback import print_exc, format_exc

import config as cfg
from channel_handler import get_channel_list, is_channel_allowed, replace_categories, write_entry
from utils import wait_for_internet, send_email


def main():
    while True:
        print('Started at', datetime.now().strftime('%b %d %H:%M:%S'), end='\n\n')

        wait_for_internet()

        data_set_number = 0

        for data_set in cfg.DATA_SETS:
            data_set_number += 1
            print('Processing data set', data_set_number, 'of', len(cfg.DATA_SETS))

            out_file_name = data_set.get('OUT_FILE_NAME')
            out_file_encoding = data_set.get('OUT_FILE_ENCODING')
            out_file_first_line = data_set.get('OUT_FILE_FIRST_LINE')

            makedirs(dirname(out_file_name), exist_ok=True)

            with closing(open(out_file_name, 'w', out_file_encoding)) as out_file:
                out_file.write(out_file_first_line)

                total_channel_count = 0
                allowed_channel_count = 0

                channel_list = get_channel_list(data_set)
                channel_list = replace_categories(channel_list, data_set)
                channel_list.sort(key=lambda x: x.get('name'))
                channel_list.sort(key=lambda x: x.get('cat'))

                for channel in channel_list:
                    total_channel_count += 1

                    if is_channel_allowed(channel, data_set):
                        write_entry(out_file, data_set, channel)
                        allowed_channel_count += 1

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


# Main start point.
if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        main()
    except Exception:
        print_exc()

        if cfg.MAIL_ON_CRASH:
            print('Sending notification.', file=stderr)
            send_email('M3UGenerator has crashed on ' + gethostname() + '@' + gethostbyname(gethostname()),
                       format_exc())

        if cfg.PAUSE_ON_CRASH:
            input('Press <Enter> to exit...\n')

        exit(1)
