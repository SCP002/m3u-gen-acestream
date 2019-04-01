#!/usr/bin/python3
# -*- coding: utf-8 -*-


from codecs import StreamReaderWriter, open
from contextlib import closing
from json import load, dump
from re import match, IGNORECASE
from typing import List

from channel.channel import Channel
from config.data_set import DataSet
from filter.filter import Filter, ReplaceCat, FilterDecoder, FilterEncoder


class FilterHandler:

    def __init__(self) -> None:
        self._data_set: DataSet = None
        self._filter_contents: Filter = None

    @property
    def data_set(self) -> DataSet:
        return self._data_set

    @data_set.setter
    def data_set(self, data_set: DataSet) -> None:
        self._data_set = data_set

        filter_file_name: str = data_set.filter_file_name

        with closing(open(filter_file_name, 'r', 'utf-8')) as filter_file:  # type: StreamReaderWriter
            self._filter_contents = load(filter_file, cls=FilterDecoder)

    # TODO: Add category to category replacing.
    def replace_categories(self, channels: List[Channel]) -> None:
        replace_cats: List[ReplaceCat] = self._filter_contents.replace_cats

        replaced: bool = False

        for replace_cat in replace_cats:
            target_name: str = replace_cat.for_name
            target_category: str = replace_cat.to_cat

            for channel in channels:
                current_name: str = channel.name
                current_category: str = channel.category

                if match(target_name, current_name, IGNORECASE) and not current_category == target_category:
                    channel.category = target_category
                    replaced = True
                    print('Replaced category for channel "' + current_name + '", from "' + current_category + '" to "' +
                          target_category + '".')

        if replaced:
            print('')

    def is_channel_allowed(self, channel: Channel) -> bool:
        exclude_cats: List[str] = self._filter_contents.exclude_cats

        if len(exclude_cats) > 0:
            categories_filter: str = '(' + ')|('.join(exclude_cats) + ')'

            if match(categories_filter, channel.category, IGNORECASE):
                return False

        exclude_names: List[str] = self._filter_contents.exclude_names

        if len(exclude_names) > 0:
            names_filter: str = '(' + ')|('.join(exclude_names) + ')'

            if match(names_filter, channel.name, IGNORECASE):
                return False

        return True

    def clean_filter(self, src_channels: List[Channel]) -> None:
        cleaned: bool = False

        # Clean "replaceCats"
        replace_cats: List[ReplaceCat] = self._filter_contents.replace_cats

        for replace_cat in replace_cats[:]:
            name_in_filter: str = replace_cat.for_name

            if all(not match(name_in_filter, src_channel.name, IGNORECASE) for src_channel in src_channels):
                replace_cats.remove(replace_cat)
                cleaned = True
                print('Not found any match for category replacement: "' + name_in_filter + '" in source,',
                      'removed from filter.')

        if cleaned:
            cleaned = False
            print('')

        # Clean "excludeCats"
        exclude_cats: List[str] = self._filter_contents.exclude_cats

        for exclude_cat in exclude_cats[:]:
            if all(not match(exclude_cat, src_channel.category, IGNORECASE) for src_channel in src_channels):
                exclude_cats.remove(exclude_cat)
                cleaned = True
                print('Not found any match for category exclusion: "' + exclude_cat + '" in source,',
                      'removed from filter.')

        if cleaned:
            cleaned = False
            print('')

        # Clean "excludeNames"
        exclude_names: List[str] = self._filter_contents.exclude_names

        for exclude_name in exclude_names[:]:
            if all(not match(exclude_name, src_channel.name, IGNORECASE) for src_channel in src_channels):
                exclude_names.remove(exclude_name)
                cleaned = True
                print('Not found any match for name exclusion: "' + exclude_name + '" in source, removed from filter.')

        if cleaned:
            print('')

        # Write changes
        filter_file_name: str = self.data_set.filter_file_name

        with closing(open(filter_file_name, 'w', 'utf-8')) as filter_file:  # type: StreamReaderWriter
            dump(self._filter_contents, filter_file, cls=FilterEncoder, indent=2, ensure_ascii=False)
