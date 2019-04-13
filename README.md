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

See `./src/filter/filter.json` to configure filter.
See formatting in the config file.

See `./src/channel/injection.json` to configure channel injections.
See formatting in the config file.

Default output folder: `./out/`.

Tested with [Python 3.7.1](https://www.python.org/downloads/release/python-371/).

---
If you want to serve generated files over http, you can use
python built-in http server module, for example:

```sh
cd out
python -m http.server 7999
```

The command above will serve output directory on port `7999`.

So generated files can be accessed via local network and you can
open links like `<your-local-ip>:7999/<playlist-file-name>` in
IPTV player directly.
