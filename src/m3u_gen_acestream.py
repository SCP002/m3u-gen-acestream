#!/usr/bin/python3
# -*- coding: utf-8 -*-


from datetime import datetime, timedelta
from os import chdir
from socket import gethostname, gethostbyname
from sys import stderr, path
from time import sleep
from traceback import print_exc, format_exc

from channel.channel_handler import ChannelHandler
from config.config import Config
from utils import Utils


class M3UGenAceStream:

    @staticmethod
    def main() -> None:
        channel_handler: ChannelHandler = ChannelHandler()

        while True:
            print('Started at', datetime.now().strftime('%b %d %H:%M:%S'), end='\n\n')

            Utils.wait_for_internet()

            data_sets_amount: int = len(Config.DATA_SETS)

            for data_set_index, data_set in enumerate(Config.DATA_SETS):
                print('Processing data set', data_set_index + 1, 'of', data_sets_amount)

                channel_handler.data_set = data_set
                channel_handler.write_playlist()

                # If remain at least one DataSet to process
                if data_set_index + 1 < data_sets_amount:
                    next_data_set_url: str = Config.DATA_SETS[data_set_index + 1].src_channels_url

                    # If do not have cached channels for the next DataSet
                    if not channel_handler.get_cached_channels_for_url(next_data_set_url):
                        print('Sleeping for', timedelta(seconds=Config.CHANN_SRC_REQ_DELAY_UP),
                              'before processing next data set...')
                        sleep(Config.CHANN_SRC_REQ_DELAY_UP)

                print('')

            channel_handler.clear_cached_channels()

            print('Finished at', datetime.now().strftime('%b %d %H:%M:%S'))
            print('Sleeping for', timedelta(seconds=Config.UPDATE_DELAY), 'before the new update...')
            print('-' * 45, end='\n\n\n')
            sleep(Config.UPDATE_DELAY)


# Main start point.
if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        chdir(path[0])

        M3UGenAceStream.main()
    except Exception:
        print_exc()

        if Config.MAIL_ON_CRASH:
            print('Sending notification.', file=stderr)

            subject: str = 'm3u-gen-acestream has crashed on ' + gethostname() + '@' + gethostbyname(gethostname())
            Utils.send_email(subject, format_exc())

        if Config.PAUSE_ON_CRASH:
            input('Press <Enter> to exit...\n')

        exit(1)
