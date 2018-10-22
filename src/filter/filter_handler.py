#!/usr/bin/python3
# -*- coding: utf-8 -*-


from codecs import open
from contextlib import closing
from json import load, dump
from re import match, IGNORECASE
from typing import List

from channel.channel import Channel
from config.data_set import DataSet
from filter.filter import Filter, ReplaceCat, FilterDecoder, FilterEncoder


class FilterHandler:  # TODO: Assign required variables before 'with' statements

    def __init__(self) -> None:
        self._data_set = None

    @property
    def data_set(self) -> DataSet:
        return self._data_set

    @data_set.setter
    def data_set(self, data_set: DataSet) -> None:
        self._data_set = data_set

    def replace_categories(self, channels: List[Channel]) -> List[Channel]:
        with closing(open(self.data_set.filter_file_name, 'r', self.data_set.filter_file_encoding)) as filter_file:
            filter_contents: Filter = load(filter_file, cls=FilterDecoder)

        replace_cats: List[ReplaceCat] = filter_contents.replace_cats

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

        return channels

    def is_channel_allowed(self, channel: Channel) -> bool:
        with closing(open(self.data_set.filter_file_name, 'r', self.data_set.filter_file_encoding)) as filter_file:
            filter_contents: Filter = load(filter_file, cls=FilterDecoder)

        exclude_cats: List[str] = filter_contents.exclude_cats

        if len(exclude_cats) > 0:
            categories_filter: str = '(' + ')|('.join(exclude_cats) + ')'

            if match(categories_filter, channel.category, IGNORECASE):
                return False

        exclude_names: List[str] = filter_contents.exclude_names

        if len(exclude_names) > 0:
            names_filter: str = '(' + ')|('.join(exclude_names) + ')'

            if match(names_filter, channel.name, IGNORECASE):
                return False

        return True

    def clean_filter(self, src_channels: List[Channel]) -> None:
        with closing(open(self.data_set.filter_file_name, 'r', self.data_set.filter_file_encoding)) as filter_file:
            filter_contents: Filter = load(filter_file, cls=FilterDecoder)

        cleaned: bool = False

        # Clean "replace_cats"
        replace_cats: List[ReplaceCat] = filter_contents.replace_cats

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

        # Clean "exclude_cats"
        exclude_cats: List[str] = filter_contents.exclude_cats

        for exclude_cat in exclude_cats[:]:
            if all(not match(exclude_cat, src_channel.category, IGNORECASE) for src_channel in src_channels):
                exclude_cats.remove(exclude_cat)
                cleaned = True
                print('Not found any match for category exclusion: "' + exclude_cat + '" in source,',
                      'removed from filter.')

        if cleaned:
            cleaned = False
            print('')

        # Clean "exclude_names"
        exclude_names: List[str] = filter_contents.exclude_names

        for exclude_name in exclude_names[:]:
            if all(not match(exclude_name, src_channel.name, IGNORECASE) for src_channel in src_channels):
                exclude_names.remove(exclude_name)
                cleaned = True
                print('Not found any match for name exclusion: "' + exclude_name + '" in source, removed from filter.')

        if cleaned:
            print('')

        # Write changes
        with closing(open(self.data_set.filter_file_name, 'w', self.data_set.filter_file_encoding)) as filter_file:
            dump(filter_contents, filter_file, cls=FilterEncoder, indent=2, ensure_ascii=False)
