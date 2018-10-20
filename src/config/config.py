#!/usr/bin/python3
# -*- coding: UTF-8 -*-


from typing import Tuple

from config.data_set import DataSet


class Config:
    # Address used to check internet connection:
    CONN_CHECK_ADDR: str = 'http://google.com'

    # Delay between requests to the internet connection check address (in seconds):
    CONN_CHECK_REQ_DELAY: int = 30

    # Delay between processing each data set (in seconds):
    DATA_SET_DELAY: int = 5

    # Delay between playlist updates (in seconds):
    UPDATE_DELAY: int = 60 * 60

    # Delay between requests to the JSON source host if it is currently down (in seconds):
    JSON_SRC_REQ_DELAY: int = 60 * 10

    # Amount of requests to the JSON source host before throw an exception if it is currently down:
    JSON_SRC_MAX_ATTEMPTS: int = 10

    # Time to wait before consider that destination is unreachable (in seconds):
    CONN_TIMEOUT: int = 10

    # Send email on program crash or not:
    MAIL_ON_CRASH: bool = False

    # Send email from:
    # Note: To use this feature with gmail, enable 'less secure apps' on the sender account.
    # See: https://myaccount.google.com/lesssecureapps
    MAIL_FROM: str = 'from.email.address@domain.com'

    # Send email to:
    MAIL_TO: str = 'to.email.address@domain.com'

    # SMTP server address:
    SMTP_ADDR: str = 'smtp.gmail.com:587'

    # SMTP server login:
    SMTP_LOGIN: str = 'my.email.login'

    # SMTP server password:
    SMTP_PWD: str = 'my.email.password'

    # Ask to press <Enter> on program crash to exit or not:
    PAUSE_ON_CRASH: bool = True

    # noinspection SpellCheckingInspection
    # Data sets used to generate m3u files:
    DATA_SETS: Tuple[DataSet] = (
        # TTV, all:
        DataSet(
            # Source JSON file URL:
            # Response example:
            # {
            #   "channels": [
            #     {
            #       "name": "2x2 (+2)",
            #       "url": "55025502b66f3a1d637fe22ed1ca54cfa2b255c3",
            #       "cat": "Развлекательные"
            #     },
            #     {
            #       "name": "AMC",
            #       "url": "adee14686e77e169b3622d10cc0e66ac84f09e1d",
            #       "cat": "Фильмы"
            #     },
            #
            #     ...
            #
            #     {
            #       "name": "Super Tennis HD",
            #       "url": "4468f2698f66674f30044903fc8cadc80ebe181f",
            #       "cat": "Спорт"
            #     }
            #   ]
            # }
            'http://91.92.66.82/trash/ttv-list/ttv.json',

            # JSON response encoding:
            'UTF-8-SIG',

            # Output file name:
            '../out/acestream-ttv-all.m3u',

            # Output file encoding:
            'UTF-8',

            # Output file first line:
            '#EXTM3U url-tvg="http://1ttvapi.top/ttv.xmltv.xml.gz" tvg-shift=0 deinterlace=1 m3uautoload=1 '
            'cache=3000\r\n',

            # Output file format:
            '#EXTINF:-1 group-title="{CATEGORY}",{NAME}\r\n'
            'http://127.0.0.1:6878/ace/getstream?id={CONTENT_ID}\r\n',

            # Filter file name:
            # Contents example (Note: Comments '//' disallowed in JSON. They used below just for clarity):
            # {
            #
            #   // Categories that needs to be changed (channel names uses regex):
            #   "replace_cats": [
            #     {
            #       "for_name": ".*some channel name 1.*",
            #       "to_cat": "some category 1"
            #     },
            #     {
            #       "for_name": "some channel name 2",
            #       "to_cat": "some category 2"
            #     }
            #   ],
            #
            #   // Categories blacklist (uses regex):
            #   "exclude_cats": [
            #     "some category 1",
            #     "some category 2"
            #   ],
            #
            #   // Channel names blacklist (uses regex):
            #   "exclude_names": [
            #     ".*some channel name 1.*",
            #     "some channel name 2"
            #   ]
            #
            # }
            './filter.json',

            # Filter file encoding:
            'UTF-8',

            # Remove entry from filter file if it is not found in source JSON or not:
            False,
        ),

        # Feel free to insert another data sets (like above) here to generate multiple playlists each iteration.
    )
