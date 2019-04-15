#!/usr/bin/python3
# -*- coding: utf-8 -*-


from json import JSONEncoder, JSONDecoder
from re import compile, IGNORECASE
from typing import List, Dict, Pattern


class NameCatMap:

    def __init__(self, for_name: Pattern[str], to_cat: str) -> None:
        self._for_name: Pattern[str] = for_name
        self._to_cat: str = to_cat

    @property
    def for_name(self) -> Pattern[str]:
        return self._for_name

    @property
    def to_cat(self) -> str:
        return self._to_cat


class Filter:

    def __init__(self,
                 replace_cats: List[NameCatMap],
                 exclude_cats: List[Pattern[str]],
                 exclude_names: List[Pattern[str]]) -> None:
        self._replace_cats: List[NameCatMap] = replace_cats
        self._exclude_cats: List[Pattern[str]] = exclude_cats
        self._exclude_names: List[Pattern[str]] = exclude_names

    @property
    def replace_cats(self) -> List[NameCatMap]:
        return self._replace_cats

    @property
    def exclude_cats(self) -> List[Pattern[str]]:
        return self._exclude_cats

    @property
    def exclude_names(self) -> List[Pattern[str]]:
        return self._exclude_names


class FilterDecoder(JSONDecoder):

    def decode(self, s: str, **kwargs: bool) -> Filter:
        input_obj: Dict[str, list] = super().decode(s)

        return self._convert(input_obj)

    @staticmethod
    def _convert(input_obj: Dict[str, list]) -> Filter:
        replace_cats: List[NameCatMap] = []

        for replace_cat_raw in input_obj.get('replaceCats', []):
            for_name: Pattern[str] = compile(replace_cat_raw.get('forName'), IGNORECASE)
            to_cat: str = replace_cat_raw.get('toCat')

            replace_cat: NameCatMap = NameCatMap(for_name, to_cat)
            replace_cats.append(replace_cat)

        exclude_cats: List[Pattern[str]] = []

        for exclude_cat in input_obj.get('excludeCats', []):
            exclude_cats.append(compile(exclude_cat, IGNORECASE))

        exclude_names: List[Pattern[str]] = []

        for exclude_name in input_obj.get('excludeNames', []):
            exclude_names.append(compile(exclude_name, IGNORECASE))

        output_obj: Filter = Filter(replace_cats, exclude_cats, exclude_names)

        return output_obj


class FilterEncoder(JSONEncoder):

    def default(self, input_obj: Filter) -> Dict[str, list]:
        output_obj: Dict[str, list] = {}

        replace_cats_raw: List[Dict[str, str]] = []
        replace_cats: List[NameCatMap] = input_obj.replace_cats

        for replace_cat in replace_cats:
            replace_cat_raw: Dict[str, str] = {
                'forName': replace_cat.for_name.pattern,
                'toCat': replace_cat.to_cat
            }

            replace_cats_raw.append(replace_cat_raw)

        exclude_cats_raw: List[str] = []
        exclude_cats: List[Pattern[str]] = input_obj.exclude_cats

        for exclude_cat in exclude_cats:
            exclude_cats_raw.append(exclude_cat.pattern)

        exclude_names_raw: List[str] = []
        exclude_names: List[Pattern[str]] = input_obj.exclude_names

        for exclude_name in exclude_names:
            exclude_names_raw.append(exclude_name.pattern)

        output_obj['replaceCats'] = replace_cats_raw
        output_obj['excludeCats'] = exclude_cats_raw
        output_obj['excludeNames'] = exclude_names_raw

        return output_obj
