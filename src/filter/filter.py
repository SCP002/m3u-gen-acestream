#!/usr/bin/python3
# -*- coding: utf-8 -*-


from json import JSONEncoder, JSONDecoder
from re import compile, IGNORECASE
from typing import List, Dict, Pattern


class NameCatMap:

    def __init__(self, k_name: Pattern[str], v_cat: str) -> None:
        self._k_name: Pattern[str] = k_name
        self._v_cat: str = v_cat

    @property
    def k_name(self) -> Pattern[str]:
        return self._k_name

    @property
    def v_cat(self) -> str:
        return self._v_cat


class Filter:

    def __init__(self,
                 replace_cats_by_names: List[NameCatMap],
                 exclude_cats: List[Pattern[str]],
                 exclude_names: List[Pattern[str]]) -> None:
        self._replace_cats_by_names: List[NameCatMap] = replace_cats_by_names
        self._exclude_cats: List[Pattern[str]] = exclude_cats
        self._exclude_names: List[Pattern[str]] = exclude_names

    @property
    def replace_cats_by_names(self) -> List[NameCatMap]:
        return self._replace_cats_by_names

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
        replace_cats_by_names: List[NameCatMap] = []

        for replace_cat_by_name_raw in input_obj.get('replaceCatsByNames', []):
            by_name: Pattern[str] = compile(replace_cat_by_name_raw.get('byName'), IGNORECASE)
            to_cat: str = replace_cat_by_name_raw.get('toCat')

            replace_cat_by_name: NameCatMap = NameCatMap(by_name, to_cat)
            replace_cats_by_names.append(replace_cat_by_name)

        exclude_cats: List[Pattern[str]] = []

        for exclude_cat in input_obj.get('excludeCats', []):
            exclude_cats.append(compile(exclude_cat, IGNORECASE))

        exclude_names: List[Pattern[str]] = []

        for exclude_name in input_obj.get('excludeNames', []):
            exclude_names.append(compile(exclude_name, IGNORECASE))

        output_obj: Filter = Filter(replace_cats_by_names, exclude_cats, exclude_names)

        return output_obj


class FilterEncoder(JSONEncoder):

    def default(self, input_obj: Filter) -> Dict[str, list]:
        output_obj: Dict[str, list] = {}

        replace_cats_by_names_raw: List[Dict[str, str]] = []
        replace_cats_by_names: List[NameCatMap] = input_obj.replace_cats_by_names

        for replace_cat_by_name in replace_cats_by_names:
            replace_cat_by_name_raw: Dict[str, str] = {
                'byName': replace_cat_by_name.k_name.pattern,
                'toCat': replace_cat_by_name.v_cat
            }

            replace_cats_by_names_raw.append(replace_cat_by_name_raw)

        exclude_cats_raw: List[str] = []
        exclude_cats: List[Pattern[str]] = input_obj.exclude_cats

        for exclude_cat in exclude_cats:
            exclude_cats_raw.append(exclude_cat.pattern)

        exclude_names_raw: List[str] = []
        exclude_names: List[Pattern[str]] = input_obj.exclude_names

        for exclude_name in exclude_names:
            exclude_names_raw.append(exclude_name.pattern)

        output_obj['replaceCatsByNames'] = replace_cats_by_names_raw
        output_obj['excludeCats'] = exclude_cats_raw
        output_obj['excludeNames'] = exclude_names_raw

        return output_obj
