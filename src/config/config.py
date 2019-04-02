#!/usr/bin/python3
# -*- coding: utf-8 -*-


from typing import Sequence

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

    # Delay between requests to the channels source host if it is currently down (in seconds):
    CHANN_SRC_REQ_DELAY: int = 60 * 10

    # Amount of requests to the channels source host before throw an exception if it is currently down:
    CHANN_SRC_MAX_ATTEMPTS: int = 10

    # Time to wait before consider that destination is unreachable (in seconds):
    CONN_TIMEOUT: int = 10

    # Send email on program crash or not:
    MAIL_ON_CRASH: bool = False

    # Send email from:
    #
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

    # Data sets used to generate m3u files:
    DATA_SETS: Sequence[DataSet] = (
        # AceStream search, all channels, for AceStream:
        DataSet(
            # Source channels file URL:
            #
            # List of acceptable sources:
            # http://91.92.66.82/trash/ttv-list/allfon.json
            # http://91.92.66.82/trash/ttv-list/as.json
            # http://91.92.66.82/trash/ttv-list/ace.json
            # http://91.92.66.82/trash/ttv-list/acelive.json
            #
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
            'http://91.92.66.82/trash/ttv-list/as.json',

            # Channels injection file name:
            #
            # Contents example:
            # [
            #   {
            #     "name": "Sample Name To Add 1",
            #     "category": "Sample Category To Add 1",
            #     "contentId": "Sample Content ID To Add 1"
            #   },
            #   {
            #     "name": "Sample Name To Add 2",
            #     "category": "Sample Category To Add 2",
            #     "contentId": "Sample Content ID To Add 2"
            #   }
            # ]
            './channel/injection.json',

            # Output file name:
            '../out/acestream-all.m3u',

            # Output file encoding:
            #
            # See https://docs.python.org/3/library/codecs.html#standard-encodings
            'utf-8',

            # Output file first line:
            '#EXTM3U url-tvg="http://www.teleguide.info/download/new3/jtv.zip" tvg-shift=0 deinterlace=1 '
            'm3uautoload=1\r\n',

            # Output file format:
            '#EXTINF:-1 group-title="{CATEGORY}",{NAME}\r\n'
            'http://127.0.0.1:6878/ace/getstream?id={CONTENT_ID}\r\n',

            # Filter file name:
            #
            # Contents example (Note: Comments '//' disallowed in JSON. They used below just for clarity):
            # {
            #
            #   // Categories that needs to be changed (channel names uses regex):
            #   "replaceCats": [
            #     {
            #       "forName": ".*some channel name 1.*",
            #       "toCat": "some category 1"
            #     },
            #     {
            #       "forName": "some channel name 2",
            #       "toCat": "some category 2"
            #     }
            #   ],
            #
            #   // Categories blacklist (uses regex):
            #   "excludeCats": [
            #     "some category 1",
            #     "some category 2"
            #   ],
            #
            #   // Channel names blacklist (uses regex):
            #   "excludeNames": [
            #     ".*some channel name 1.*",
            #     "some channel name 2"
            #   ]
            #
            # }
            './filter/filter.json',

            # Remove entry from filter file if it is not found in channels source or not:
            False,
        ),
        # --------------------------------------------------------------------------------------------------------------
        # AceStream search, all channels, for HttpAceProxy (https://github.com/pepsik-kiev/HTTPAceProxy):
        DataSet(
            # Source channels file URL:
            #
            # List of acceptable sources:
            # http://91.92.66.82/trash/ttv-list/allfon.json
            # http://91.92.66.82/trash/ttv-list/as.json
            # http://91.92.66.82/trash/ttv-list/ace.json
            # http://91.92.66.82/trash/ttv-list/acelive.json
            #
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
            'http://91.92.66.82/trash/ttv-list/as.json',

            # Channels injection file name:
            #
            # Contents example:
            # [
            #   {
            #     "name": "Sample Name To Add 1",
            #     "category": "Sample Category To Add 1",
            #     "contentId": "Sample Content ID To Add 1"
            #   },
            #   {
            #     "name": "Sample Name To Add 2",
            #     "category": "Sample Category To Add 2",
            #     "contentId": "Sample Content ID To Add 2"
            #   }
            # ]
            './channel/injection.json',

            # Output file name:
            '../out/aceproxy-all.m3u',

            # Output file encoding:
            #
            # See https://docs.python.org/3/library/codecs.html#standard-encodings
            'utf-8',

            # Output file first line:
            '#EXTM3U url-tvg="http://www.teleguide.info/download/new3/jtv.zip" tvg-shift=0 deinterlace=1 '
            'm3uautoload=1\r\n',

            # Output file format:
            '#EXTINF:-1 group-title="{CATEGORY}",{NAME}\r\n'
            'http://127.0.0.1:8000/pid/{CONTENT_ID}/stream.mp4\r\n',

            # Filter file name:
            #
            # Contents example (Note: Comments '//' disallowed in JSON. They used below just for clarity):
            # {
            #
            #   // Categories that needs to be changed (channel names uses regex):
            #   "replaceCats": [
            #     {
            #       "forName": ".*some channel name 1.*",
            #       "toCat": "some category 1"
            #     },
            #     {
            #       "forName": "some channel name 2",
            #       "toCat": "some category 2"
            #     }
            #   ],
            #
            #   // Categories blacklist (uses regex):
            #   "excludeCats": [
            #     "some category 1",
            #     "some category 2"
            #   ],
            #
            #   // Channel names blacklist (uses regex):
            #   "excludeNames": [
            #     ".*some channel name 1.*",
            #     "some channel name 2"
            #   ]
            #
            # }
            './filter/filter.json',

            # Remove entry from filter file if it is not found in channels source or not:
            False,
        ),

        # Feel free to insert another data sets (like above) here to generate multiple playlists each iteration.
    )
