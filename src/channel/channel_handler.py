#!/usr/bin/python3
# -*- coding: utf-8 -*-


from codecs import StreamReaderWriter
from contextlib import closing
from datetime import timedelta
from json import loads
from sys import stderr
from time import sleep
from typing import List
from urllib.error import URLError
from urllib.request import urlopen

from channel.channel import Channel, ChannelsDecoder
from config.config import Config
from config.data_set import DataSet
from utils import Utils


class ChannelHandler:

    @staticmethod
    def fetch_channels(data_set: DataSet) -> List[Channel]:
        json_url: str = data_set.json_url
        resp_encoding: str = data_set.resp_encoding

        for attempt_number in range(1, Config.JSON_SRC_MAX_ATTEMPTS):
            print('Retrieving JSON file, attempt', attempt_number, 'of', Config.JSON_SRC_MAX_ATTEMPTS, end='\n\n')

            if attempt_number > 1:
                Utils.wait_for_internet()

            try:
                with closing(urlopen(json_url, timeout=Config.CONN_TIMEOUT)) as response_raw:
                    response: str = response_raw.read().decode(resp_encoding)

                channels: List[Channel] = loads(response, cls=ChannelsDecoder)

                return channels
            except URLError as url_error:
                print('Can not retrieve JSON file.', file=stderr)
                print('Error:', url_error, file=stderr)

                if attempt_number < Config.JSON_SRC_MAX_ATTEMPTS:
                    print('Sleeping for', timedelta(seconds=Config.JSON_SRC_REQ_DELAY), 'before trying again.',
                          end='\n\n',
                          file=stderr)
                    sleep(Config.JSON_SRC_REQ_DELAY)
                else:
                    print('Raising an exception.', end='\n\n', file=stderr)
                    raise

        return [Channel('', '', '')]

    @staticmethod
    def write_entry(channel: Channel, data_set: DataSet, out_file: StreamReaderWriter) -> None:
        out_file_format: str = data_set.out_file_format

        entry: str = out_file_format \
            .replace('{CATEGORY}', channel.category) \
            .replace('{NAME}', channel.name) \
            .replace('{CONTENT_ID}', channel.content_id)

        out_file.write(entry)
