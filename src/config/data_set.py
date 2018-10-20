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
        self.json_url = json_url
        self.resp_encoding = resp_encoding
        self.out_file_name = out_file_name
        self.out_file_encoding = out_file_encoding
        self.out_file_first_line = out_file_first_line
        self.out_file_format = out_file_format
        self.filter_file_name = filter_file_name
        self.filter_file_encoding = filter_file_encoding
        self.clean_filter = clean_filter
