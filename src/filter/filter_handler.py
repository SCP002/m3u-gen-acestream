#!/usr/bin/python3
# -*- coding: utf-8 -*-


from codecs import StreamReaderWriter, open
from contextlib import closing
from json import load, dump
from typing import List, Optional, Pattern

from channel.channel import Channel
from config.data_set import DataSet
from filter.filter import Filter, NameCatMap, FilterDecoder, FilterEncoder, CatCatMap


class FilterHandler:

    def __init__(self) -> None:
        self._data_set: Optional[DataSet] = None
        self._filter_contents: Optional[Filter] = None

    @property
    def data_set(self) -> Optional[DataSet]:
        return self._data_set

    @data_set.setter
    def data_set(self, data_set: DataSet) -> None:
        self._data_set = data_set

        filter_file_name: str = data_set.filter_file_name

        with closing(open(filter_file_name, 'r', 'utf-8')) as filter_file:  # type: StreamReaderWriter
            self._filter_contents = load(filter_file, cls=FilterDecoder, strict=False)

    def replace_categories(self, channels: List[Channel]) -> None:
        self._replace_cats_by_cats(channels)
        self._replace_cats_by_names(channels)

    def is_channel_allowed(self, channel: Channel) -> bool:
        assert self._filter_contents is not None

        exclude_cats: List[Pattern[str]] = self._filter_contents.exclude_cats

        if any(exclude_cat.match(channel.category) for exclude_cat in exclude_cats):
            return False

        exclude_names: List[Pattern[str]] = self._filter_contents.exclude_names

        if any(exclude_name.match(channel.name) for exclude_name in exclude_names):
            return False

        return True

    def clean_filter(self, src_channels: List[Channel]) -> None:
        assert self.data_set is not None
        assert self._filter_contents is not None

        cleaned: bool = False

        # Clean "replaceCatsByCats"
        replace_cats_by_cats: List[CatCatMap] = self._filter_contents.replace_cats_by_cats

        for replace_cat_by_cat in replace_cats_by_cats[:]:
            cat_in_filter: Pattern[str] = replace_cat_by_cat.k_cat

            if all(not cat_in_filter.match(src_channel.category) for src_channel in src_channels):
                replace_cats_by_cats.remove(replace_cat_by_cat)
                cleaned = True
                print('Not found any match for category by category replacement: "' + cat_in_filter.pattern +
                      '" in source, category removed from filter.')

        if cleaned:
            cleaned = False
            print('')

        # Clean "replaceCatsByNames"
        replace_cats_by_names: List[NameCatMap] = self._filter_contents.replace_cats_by_names

        for replace_cat_by_name in replace_cats_by_names[:]:
            name_in_filter: Pattern[str] = replace_cat_by_name.k_name

            if all(not name_in_filter.match(src_channel.name) for src_channel in src_channels):
                replace_cats_by_names.remove(replace_cat_by_name)
                cleaned = True
                print('Not found any match for category by name replacement: "' + name_in_filter.pattern +
                      '" in source, name removed from filter.')

        if cleaned:
            cleaned = False
            print('')

        # Clean "excludeCats"
        exclude_cats: List[Pattern[str]] = self._filter_contents.exclude_cats

        for exclude_cat in exclude_cats[:]:
            if all(not exclude_cat.match(src_channel.category) for src_channel in src_channels):
                exclude_cats.remove(exclude_cat)
                cleaned = True
                print('Not found any match for category exclusion: "' + exclude_cat.pattern + '" in source,',
                      'removed from filter.')

        if cleaned:
            cleaned = False
            print('')

        # Clean "excludeNames"
        exclude_names: List[Pattern[str]] = self._filter_contents.exclude_names

        for exclude_name in exclude_names[:]:
            if all(not exclude_name.match(src_channel.name) for src_channel in src_channels):
                exclude_names.remove(exclude_name)
                cleaned = True
                print('Not found any match for name exclusion: "' + exclude_name.pattern + '" in source,',
                      ' removed from filter.')

        if cleaned:
            print('')

        # Write changes
        filter_file_name: str = self.data_set.filter_file_name

        with closing(open(filter_file_name, 'w', 'utf-8')) as filter_file:  # type: StreamReaderWriter
            dump(self._filter_contents, filter_file, cls=FilterEncoder, indent=2, ensure_ascii=False)

    def _replace_cats_by_cats(self, channels: List[Channel]) -> None:
        assert self._filter_contents is not None

        replace_cats_by_cats: List[CatCatMap] = self._filter_contents.replace_cats_by_cats

        replaced: bool = False

        for replace_cat_by_cat in replace_cats_by_cats:
            by_target_category: Pattern[str] = replace_cat_by_cat.k_cat
            to_target_category: str = replace_cat_by_cat.v_cat

            for channel in channels:
                current_name: str = channel.name
                current_category: str = channel.category

                if not current_category == to_target_category and by_target_category.match(current_category):
                    channel.category = to_target_category
                    replaced = True
                    print('Replaced category for channel "' + current_name + '", from "' + current_category + '" to "' +
                          to_target_category + '".')

        if replaced:
            print('')

    def _replace_cats_by_names(self, channels: List[Channel]) -> None:
        assert self._filter_contents is not None

        replace_cats_by_names: List[NameCatMap] = self._filter_contents.replace_cats_by_names

        replaced: bool = False

        for replace_cat_by_name in replace_cats_by_names:
            by_target_name: Pattern[str] = replace_cat_by_name.k_name
            to_target_category: str = replace_cat_by_name.v_cat

            for channel in channels:
                current_name: str = channel.name
                current_category: str = channel.category

                if not current_category == to_target_category and by_target_name.match(current_name):
                    channel.category = to_target_category
                    replaced = True
                    print('Replaced category for channel "' + current_name + '", from "' + current_category + '" to "' +
                          to_target_category + '".')

        if replaced:
            print('')
