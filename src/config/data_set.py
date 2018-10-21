#!/usr/bin/python3
# -*- coding: UTF-8 -*-


class DataSet:

    def __init__(self,
                 json_url: str,
                 resp_encoding: str,
                 out_file_name: str,
                 out_file_encoding: str,
                 out_file_first_line: str,
                 out_file_format: str,
                 filter_file_name: str,
                 filter_file_encoding: str,
                 clean_filter: bool) -> None:
        self._json_url = json_url
        self._resp_encoding = resp_encoding
        self._out_file_name = out_file_name
        self._out_file_encoding = out_file_encoding
        self._out_file_first_line = out_file_first_line
        self._out_file_format = out_file_format
        self._filter_file_name = filter_file_name
        self._filter_file_encoding = filter_file_encoding
        self._clean_filter = clean_filter

    @property
    def json_url(self) -> str:
        return self._json_url

    @property
    def resp_encoding(self) -> str:
        return self._resp_encoding

    @property
    def out_file_name(self) -> str:
        return self._out_file_name

    @property
    def out_file_encoding(self) -> str:
        return self._out_file_encoding

    @property
    def out_file_first_line(self) -> str:
        return self._out_file_first_line

    @property
    def out_file_format(self) -> str:
        return self._out_file_format

    @property
    def filter_file_name(self) -> str:
        return self._filter_file_name

    @property
    def filter_file_encoding(self) -> str:
        return self._filter_file_encoding

    @property
    def clean_filter(self) -> bool:
        return self._clean_filter
