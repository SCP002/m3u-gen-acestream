#!/usr/bin/python3
# -*- coding: UTF-8 -*-


from contextlib import closing
from datetime import timedelta
from smtplib import SMTP
from sys import stderr
from time import sleep
from urllib.error import URLError
from urllib.request import urlopen

import config as cfg


def wait_for_internet():
    while True:
        try:
            with closing(urlopen(cfg.CONN_CHECK_ADDR, timeout=cfg.CONN_TIMEOUT)):
                print('Internet connection is up.', end='\n\n')
                break
        except URLError as url_error:
            print('Internet connection is down.', file=stderr)
            print('Can not reach', cfg.CONN_CHECK_ADDR, file=stderr)
            print('Error:', url_error, file=stderr)
            print('Sleeping for', timedelta(seconds=cfg.CONN_CHECK_REQ_DELAY), 'before trying again.',
                  end='\n\n', file=stderr)
            sleep(cfg.CONN_CHECK_REQ_DELAY)


def send_email(subject, text):
    message = 'Subject: {}\n\n{}'.format(subject, text)

    server = SMTP(cfg.SMTP_ADDR)
    server.ehlo()
    server.starttls()
    server.login(cfg.SMTP_LOGIN, cfg.SMTP_PWD)
    server.sendmail(cfg.NOTIFY_FROM, cfg.NOTIFY_TO, message)
    server.quit()
