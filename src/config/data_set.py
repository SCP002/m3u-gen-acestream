#!/usr/bin/python3
# -*- coding: utf-8 -*-


class DataSet:

    def __init__(self,
                 src_channels_url: str,
                 injection_file_name: str,
                 out_file_name: str,
                 out_file_encoding: str,
                 out_file_first_line: str,
                 out_file_format: str,
                 filter_file_name: str,
                 clean_filter: bool) -> None:
        self._src_channels_url: str = src_channels_url
        self._injection_file_name: str = injection_file_name
        self._out_file_name: str = out_file_name
        self._out_file_encoding: str = out_file_encoding
        self._out_file_first_line: str = out_file_first_line
        self._out_file_format: str = out_file_format
        self._filter_file_name: str = filter_file_name
        self._clean_filter: bool = clean_filter

    @property
    def src_channels_url(self) -> str:
        return self._src_channels_url

    @property
    def injection_file_name(self) -> str:
        return self._injection_file_name

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
    def clean_filter(self) -> bool:
        return self._clean_filter
