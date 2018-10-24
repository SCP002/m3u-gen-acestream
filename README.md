## m3u-gen-ttv

> A program to periodically create and refresh customized M3U files for IPTV players using input JSON data.

## How to use?
* Run `./src/m3u_gen_ttv.py` to start a program.
  When playlist(s) is generated, you can close the program
  if you do not need automatic updates.
* Run AceStream if it is not running yet.
  In default configuration, assuming that AceStream
  is listening at `127.0.0.1`.
* Open generated playlist with your favorite IPTV player.
* Done.

## Notes:
See `./src/config/config.py` to configure program behavior.

See `./src/filter/filter.json` to configure filter. See formatting in config file.

Default output folder: `./out/`.

Tested with [Python 3.7](https://www.python.org/downloads/release/python-370/).
