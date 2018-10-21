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
from typing import List

from channel.channel import Channel
from channel.handler import ChannelHandler
from config.config import Config
from filter.handler import FilterHandler
from utils import Utils


class M3UGenerator:

    @staticmethod
    def main() -> None:
        while True:
            print('Started at', datetime.now().strftime('%b %d %H:%M:%S'), end='\n\n')

            Utils.wait_for_internet()

            data_set_number: int = 0

            for data_set in Config.DATA_SETS:
                data_set_number += 1
                print('Processing data set', data_set_number, 'of', len(Config.DATA_SETS))

                out_file_name: str = data_set.out_file_name
                out_file_encoding: str = data_set.out_file_encoding
                out_file_first_line: str = data_set.out_file_first_line

                makedirs(dirname(out_file_name), exist_ok=True)

                with closing(open(out_file_name, 'w', out_file_encoding)) as out_file:
                    out_file.write(out_file_first_line)

                    total_channel_count: int = 0
                    allowed_channel_count: int = 0

                    channels: List[Channel] = ChannelHandler.fetch_channels(data_set)
                    channels = FilterHandler.replace_categories(channels, data_set)
                    channels.sort(key=lambda x: x.name)
                    channels.sort(key=lambda x: x.category)

                    if data_set.clean_filter:
                        FilterHandler.clean_filter(channels, data_set)

                    for channel in channels:
                        total_channel_count += 1

                        if FilterHandler.is_channel_allowed(channel, data_set):
                            ChannelHandler.write_entry(channel, data_set, out_file)
                            allowed_channel_count += 1

                print('Playlist', data_set.out_file_name, 'successfully generated.')
                print('Channels processed in total:', total_channel_count)
                print('Channels allowed:', allowed_channel_count)
                print('Channels denied:', total_channel_count - allowed_channel_count)

                if data_set_number < len(Config.DATA_SETS):
                    print('Sleeping for', timedelta(seconds=Config.DATA_SET_DELAY),
                          'before processing next data set...')
                    sleep(Config.DATA_SET_DELAY)

                print('')

            print('Finished at', datetime.now().strftime('%b %d %H:%M:%S'))
            print('Sleeping for', timedelta(seconds=Config.UPDATE_DELAY), 'before the new update...')
            print('-' * 45, end='\n\n\n')
            sleep(Config.UPDATE_DELAY)


# Main start point.
if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        M3UGenerator.main()
    except Exception:
        print_exc()

        if Config.MAIL_ON_CRASH:
            print('Sending notification.', file=stderr)
            Utils.send_email('M3UGenerator has crashed on ' + gethostname() + '@' + gethostbyname(gethostname()),
                             format_exc())

        if Config.PAUSE_ON_CRASH:
            input('Press <Enter> to exit...\n')

        exit(1)
