#!/usr/bin/python3
# -*- coding: utf-8 -*-


from codecs import open, StreamReaderWriter
from contextlib import closing
from datetime import timedelta
from gzip import decompress
from http.client import HTTPResponse
from json import load, loads
from os import makedirs
from os.path import dirname
from sys import stderr
from time import sleep
from typing import List, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

from channel.channel import Channel, ChannelsDecoder, InjectionDecoder, UrlChannelsMap
from config.config import Config
from config.data_set import DataSet
from filter.filter_handler import FilterHandler
from utils import Utils


class ChannelHandler:

    def __init__(self) -> None:
        self._data_set: Optional[DataSet] = None
        self._filter_handler: FilterHandler = FilterHandler()
        self._cached_channels_maps: List[UrlChannelsMap] = []

    @property
    def data_set(self) -> Optional[DataSet]:
        return self._data_set

    @data_set.setter
    def data_set(self, data_set: DataSet) -> None:
        self._data_set = data_set
        self._filter_handler.data_set = data_set

    def get_cached_channels_for_url(self, url: str) -> List[Channel]:
        channels: List[Channel] = []

        for cached_channels_map in self._cached_channels_maps:
            if cached_channels_map.url == url:
                channels = cached_channels_map.channels

                return channels

        return channels

    def clear_cached_channels(self) -> None:
        self._cached_channels_maps = []

    def write_playlist(self) -> None:
        assert self.data_set is not None

        channels: List[Channel] = self._fetch_channels()

        self._inject_channels(channels)

        if self.data_set.clean_filter:
            self._filter_handler.clean_filter(channels)

        self._filter_handler.replace_categories(channels)

        channels.sort(key=lambda x: x.name)
        channels.sort(key=lambda x: x.category)

        out_file_name: str = self.data_set.out_file_name
        out_file_encoding: str = self.data_set.out_file_encoding
        out_file_first_line: str = self.data_set.out_file_first_line

        makedirs(dirname(out_file_name), exist_ok=True)

        with closing(open(out_file_name, 'w', out_file_encoding)) as out_file:  # type: StreamReaderWriter
            out_file.write(out_file_first_line)

            total_channel_count: int = 0
            allowed_channel_count: int = 0

            for channel in channels:
                total_channel_count += 1

                if self._filter_handler.is_channel_allowed(channel):
                    self._write_entry(channel, out_file)
                    allowed_channel_count += 1

        print('Playlist', self.data_set.out_file_name, 'successfully generated.')
        print('Channels processed in total:', total_channel_count)
        print('Channels allowed:', allowed_channel_count)
        print('Channels denied:', total_channel_count - allowed_channel_count)

    # TODO: In case of death of the 'http://pomoyka.win/trash/ttv-list/'
    #  fallback to the 'https://search.acestream.net/all?api_version=1.0&api_key=test_api_key'.
    #  Skip if ('availability' < 0.8) or (now in seconds - 'availability_updated_at' > 8 * 86400).
    def _fetch_channels(self) -> List[Channel]:
        assert self.data_set is not None

        src_channels_url: str = self.data_set.src_channels_url

        # Check cached channels.
        channels: List[Channel] = self.get_cached_channels_for_url(src_channels_url)

        if channels:
            print('Using cached channels from previous requests in current iteration', end='\n\n')

            return channels

        # Fetch new channels.
        for attempt_number in range(1, Config.CHANN_SRC_MAX_ATTEMPTS):
            print('Retrieving channels file, attempt', attempt_number, 'of', Config.CHANN_SRC_MAX_ATTEMPTS, end='\n\n')

            if attempt_number > 1:
                Utils.wait_for_internet()

            try:
                req: Request = Request(src_channels_url)
                req.add_header('Accept-Encoding', 'gzip')

                # noinspection Mypy
                with closing(urlopen(req, timeout=Config.CONN_TIMEOUT)) as response_raw:  # type: HTTPResponse
                    response_decompressed: bytes = decompress(response_raw.read())
                    encoding: str = response_raw.info().get_content_charset()

                response: str = response_decompressed.decode(encoding)

                channels = loads(response, cls=ChannelsDecoder)

                cached_channel_map: UrlChannelsMap = UrlChannelsMap(src_channels_url, channels)
                self._cached_channels_maps.append(cached_channel_map)

                return channels
            except URLError as url_error:
                print('Can not retrieve channels file.', file=stderr)
                print('Error:', url_error, file=stderr)

                if attempt_number < Config.CHANN_SRC_MAX_ATTEMPTS:
                    print('Sleeping for', timedelta(seconds=Config.CHANN_SRC_REQ_DELAY_DOWN), 'before trying again.',
                          end='\n\n', file=stderr)
                    sleep(Config.CHANN_SRC_REQ_DELAY_DOWN)
                else:
                    print('Raising an exception.', end='\n\n', file=stderr)
                    raise

        return channels

    def _inject_channels(self, channels: List[Channel]) -> None:
        assert self.data_set is not None

        injection_file_name: str = self.data_set.injection_file_name

        with closing(open(injection_file_name, 'r', 'utf-8')) as injection_file:  # type: StreamReaderWriter
            injection: List[Channel] = load(injection_file, cls=InjectionDecoder)

        channels.extend(injection)

    def _write_entry(self, channel: Channel, out_file: StreamReaderWriter) -> None:
        assert self.data_set is not None

        out_file_format: str = self.data_set.out_file_format

        entry: str = out_file_format \
            .replace('{CATEGORY}', channel.category) \
            .replace('{NAME}', channel.name) \
            .replace('{CONTENT_ID}', channel.content_id) \
            .replace('{TVG_NAME}', channel.tvg_name)

        out_file.write(entry)
