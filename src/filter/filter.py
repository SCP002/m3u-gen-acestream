#!/usr/bin/python3
# -*- coding: utf-8 -*-


from json import JSONEncoder, JSONDecoder
from typing import List, Dict


class ReplaceCat:

    def __init__(self, for_name: str, to_cat: str) -> None:
        self._for_name: str = for_name
        self._to_cat: str = to_cat

    @property
    def for_name(self) -> str:
        return self._for_name

    @property
    def to_cat(self) -> str:
        return self._to_cat


class Filter:

    def __init__(self, replace_cats: List[ReplaceCat], exclude_cats: List[str], exclude_names: List[str]) -> None:
        self._replace_cats: List[ReplaceCat] = replace_cats
        self._exclude_cats: List[str] = exclude_cats
        self._exclude_names: List[str] = exclude_names

    @property
    def replace_cats(self) -> List[ReplaceCat]:
        return self._replace_cats

    @property
    def exclude_cats(self) -> List[str]:
        return self._exclude_cats

    @property
    def exclude_names(self) -> List[str]:
        return self._exclude_names


class FilterDecoder(JSONDecoder):

    def decode(self, s: str, **kwargs: bool) -> Filter:
        input_obj: Dict[str, list] = super().decode(s)

        return self._convert(input_obj)

    @staticmethod
    def _convert(input_obj: Dict[str, list]) -> Filter:
        replace_cats: List[ReplaceCat] = []

        for replace_cat_raw in input_obj.get('replace_cats', []):
            for_name: str = replace_cat_raw.get('for_name')
            to_cat: str = replace_cat_raw.get('to_cat')

            replace_cat: ReplaceCat = ReplaceCat(for_name, to_cat)
            replace_cats.append(replace_cat)

        exclude_cats: List[str] = []

        for exclude_cat in input_obj.get('exclude_cats', []):
            exclude_cats.append(exclude_cat)

        exclude_names: List[str] = []

        for exclude_name in input_obj.get('exclude_names', []):
            exclude_names.append(exclude_name)

        output_obj: Filter = Filter(replace_cats, exclude_cats, exclude_names)

        return output_obj


class FilterEncoder(JSONEncoder):

    def default(self, input_obj: Filter) -> Dict[str, list]:
        output_obj: Dict[str, list] = {}

        replace_cats_raw: List[Dict[str, str]] = []
        replace_cats: List[ReplaceCat] = input_obj.replace_cats

        for replace_cat in replace_cats:
            replace_cat_raw: Dict[str, str] = {
                'for_name': replace_cat.for_name,
                'to_cat': replace_cat.to_cat
            }

            replace_cats_raw.append(replace_cat_raw)

        exclude_cats: List[str] = input_obj.exclude_cats
        exclude_names: List[str] = input_obj.exclude_names

        output_obj['replace_cats'] = replace_cats_raw
        output_obj['exclude_cats'] = exclude_cats
        output_obj['exclude_names'] = exclude_names

        return output_obj
