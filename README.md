## m3u-gen-acestream

> M3U playlist generator for AceStream.

## How to use?
* Run `./src/m3u_gen_acestream.py` to start a program.
  When playlist(s) is generated, you can close the program
  if you do not need automatic updates.
* Run AceStream if it is not running yet.
  In default configuration, assuming that AceStream
  is listening at `127.0.0.1:6878`.
* Open generated playlist with your favorite IPTV player.
* Done.

## Notes:
See `./src/config/config.py` to configure program behavior.

See `./src/filter/filter.json` to configure filter. See formatting in config file.

Default output folder: `./out/`.

Tested with [Python 3.7](https://www.python.org/downloads/release/python-370/).

---
Check other generators:
* [m3u-gen-aceproxy](https://github.com/SCP002/m3u-gen-aceproxy) - for HTTPAceProxy.
* [m3u-gen-noxbit](https://github.com/SCP002/m3u-gen-noxbit) - for Noxbit.
