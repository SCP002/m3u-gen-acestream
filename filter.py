#!/usr/bin/python3
# -*- coding: UTF-8 -*-


from typing import List, Dict


class ReplaceCatEntry:

    def __init__(self, for_name: str, to_cat: str) -> None:
        self.for_name = for_name
        self.to_cat = to_cat


class Filter:

    def __init__(self, replace_cats: List[ReplaceCatEntry], exclude_cats: List[str], exclude_names: List[str]) -> None:
        self.replace_cats = replace_cats
        self.exclude_cats = exclude_cats
        self.exclude_names = exclude_names


class FilterDecoder:

    @staticmethod
    def decode(input_obj: Dict[str, list]) -> Filter:
        replace_cat_entries: List[ReplaceCatEntry] = []

        for replace_cat in input_obj.get('replace_cats', []):
            for_name: str = replace_cat.get('for_name')
            to_cat: str = replace_cat.get('to_cat')

            replace_cat_entry: ReplaceCatEntry = ReplaceCatEntry(for_name, to_cat)
            replace_cat_entries.append(replace_cat_entry)

        exclude_cats: List[str] = []

        for exclude_cat in input_obj.get('exclude_cats', []):
            exclude_cats.append(exclude_cat)

        exclude_names: List[str] = []

        for exclude_name in input_obj.get('exclude_names', []):
            exclude_names.append(exclude_name)

        output_obj: Filter = Filter(replace_cat_entries, exclude_cats, exclude_names)

        return output_obj
