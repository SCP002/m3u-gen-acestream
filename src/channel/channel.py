#!/usr/bin/python3
# -*- coding: UTF-8 -*-


from json import JSONDecoder
from typing import List, Dict


class Channel:

    def __init__(self, name: str, category: str, content_id: str) -> None:
        self._name = name
        self._category = category
        self._content_id = content_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def category(self) -> str:
        return self._category

    @category.setter
    def category(self, category: str) -> None:
        self._category = category

    @property
    def content_id(self) -> str:
        return self._content_id


class ChannelsDecoder(JSONDecoder):

    def decode(self, s: str, **kwargs: bool) -> List[Channel]:
        input_obj: Dict[str, list] = super().decode(s)

        return self._convert(input_obj)

    @staticmethod
    def _convert(input_obj: Dict[str, list]) -> List[Channel]:
        output_obj: List[Channel] = []

        channels_raw: List[dict] = input_obj.get('channels', [])

        for channel_raw in channels_raw:
            name: str = channel_raw.get('name', '')
            category: str = channel_raw.get('cat', '')
            content_id: str = channel_raw.get('url', '')

            channel: Channel = Channel(name, category, content_id)

            output_obj.append(channel)

        return output_obj