# m3u-gen-acestream

## What is this?

> M3U playlist generator for Ace Stream.

## How does it work?

It fetches available channels from Ace Stream Engine using its API, filters and transforms them, and writes
M3U playlists using templates defined in the config.

## Notes

A VPN or proxy might be required, as some ISPs block connections to Ace Stream servers.

## Requirements

[Ace Stream](https://docs.acestream.net/products/) running locally or remotely.

## Command line flags

| Command argument     | Description                                                                               |
| -------------------- | ----------------------------------------------------------------------------------------- |
| -h, --help           | Print help message                                                                        |
| -v, --version        | Print the program version                                                                 |
| -u, --update         | Check for updates, update and exit                                                        |
| -l, --logLevel       | Logging level. Can be from `1` (most verbose) to `7` (least verbose) [default: `3`]       |
| -f, --logFile        | Log file. If set, writes structured log to a file at the specified path                   |
| -c, --cfgPath        | Config file path to read from or initialize a default [default: `m3u-gen-acestream.yaml`] |

If the config does not exist, on the first run it creates a default one at `--cfgPath` and exits.
Tweak it to suit your needs and start the program again.

## Downloads

See the [releases page](https://github.com/SCP002/m3u-gen-acestream/releases).

## Docker

> [!NOTE]
> Only x86-64 (amd64) is supported by the engine in the setup below.

### Usage

* Run the program once to initialize config:

```sh
docker compose --file compose.yaml run --rm --detach gen
```

* Change `engineAddr`, `entryTemplate` and `removeDeadLinkTemplate` in the `./data/config/m3u-gen-acestream.yaml`
  file like so:

```yaml
engineAddr: engine:6878
```

```yaml
  entryTemplate: |
    #EXTINF:-1 group-title="{{.Categories}}",{{.Name}}
    http://192.168.0.100:8080/ace/getstream?infohash={{.Infohash}}
```

```yaml
  removeDeadLinkTemplate: http://192.168.0.100:8080/ace/getstream?infohash={{.Infohash}}
```

Replace `192.168.0.100` with your actual IP address.

* Start Ace Stream Engine and acexy, and generate playlists:

```sh
docker compose --file compose.yaml up --detach
```

Playlists will be available under `./data/out/`.
Streams will point to your acexy server in Docker.
The default acexy port for incoming connections is `8080`.

To run on an interval, uncomment this block of the `gen` service in `compose.yaml` and run the command above again:

```yaml
    # environment:
    #  - INTERVAL=6h
```

### Development

Open the project in Visual Studio Code with the `Dev Containers` extension installed, or enter the dev container
manually:

```sh
docker compose --file compose.dev.yaml up --detach
docker compose --file compose.dev.yaml exec dev bash
```

To build in a container environment:

```sh
docker compose --file compose.dev.yaml run --rm --build dev bash ./build.sh
```

## Default config

```yaml
# Ace Stream Engine address in host:port format.
engineAddr: 127.0.0.1:6878
#
# Playlists to generate.
playlists:
#
# MPEG-TS format, all.
# Change any non-default category to 'other'.
- #
  # Destination file path to write the playlist to.
  outputPath: ./out/playlist-mpegts-all.m3u8
  #
  # Template for the header of the M3U file.
  headerTemplate: |
    #EXTM3U url-tvg="http://epg.one/epg2.xml.gz" tvg-shift=0 deinterlace=1 m3uautoload=1
  #
  # Template for each channel. Available variables are:
  # {{.Name}}
  # {{.Infohash}}
  # {{.Categories}}
  # {{.Countries}}
  # {{.Languages}}
  # {{.EngineAddr}}
  # {{.TVGName}}
  # {{.IconURL}}
  entryTemplate: |
    #EXTINF:-1 group-title="{{.Categories}}",{{.Name}}
    http://{{.EngineAddr}}/ace/getstream?infohash={{.Infohash}}
  #
  # Change categories matching regular expressions (keys) to strings (values).
  # Use the '^$' regular expression to match unset categories.
  # Example:
  # categoryRxToCategoryMap:
  #   '^category regexp A$': 'becomes category B'
  #   '^category regexp C$': 'becomes category D'
  categoryRxToCategoryMap:
    ^(?!.*(informational|entertaining|educational|movies|documentaries|sport|fashion|music|regional|ethnic|religion|teleshop|erotic_18_plus|other_18_plus|cyber_games|amateur|webcam)).*: other
  #
  # Set categories of channels whose name matches regular expressions (keys) to lists of strings (values).
  # Example:
  # nameRxToCategoriesMap:
  #   '^name regexp A$':
  #   - 'will have category B'
  #   - 'and category C'
  #   '^name regexp D$':
  #   - 'will have category E'
  #   - 'and category F'
  nameRxToCategoriesMap: {}
  #
  # Only keep channels whose name matches any of these regular expressions.
  # Example:
  # nameRxFilter:
  # - '.*keep channels matching name A.*'
  # - '.*keep channels matching name B.*'
  nameRxFilter: []
  #
  # Remove channels whose name matches any of these regular expressions.
  # Example:
  # nameRxBlacklist:
  # - '.*remove channels matching name A.*'
  # - '.*remove channels matching name B.*'
  nameRxBlacklist: []
  #
  # Only keep channels whose category equals any of these.
  # See https://docs.acestream.net/developers/knowledge-base/list-of-categories/
  # for the list of known (but not all possible) categories.
  # Use an empty string to include results with unset category.
  # Example:
  # categoriesFilter:
  # - 'keep channels with category A'
  # - 'keep channels with category B'
  categoriesFilter: []
  #
  # If true, only keep channels with categories that are in the filter and no others.
  categoriesFilterStrict: false
  #
  # Remove channels whose category equals any of these.
  # See https://docs.acestream.net/developers/knowledge-base/list-of-categories/
  # for the list of known (but not all possible) categories.
  # Use an empty string to exclude results with unset category.
  # Example:
  # categoriesBlacklist:
  # - 'remove channels with category A'
  # - 'remove channels with category B'
  categoriesBlacklist: []
  #
  # Only keep channels whose language equals any of these.
  # Languages are 3-character lowercase strings, such as 'eng', 'rus', etc.
  # Use an empty string to include results with unset language.
  # Example:
  # languagesFilter:
  # - 'keep channels with language A'
  # - 'keep channels with language B'
  languagesFilter: []
  #
  # If true, only keep channels with languages that are in the filter and no others.
  languagesFilterStrict: false
  #
  # Remove channels whose language equals any of these.
  # Languages are 3-character lowercase strings, such as 'eng', 'rus', etc.
  # Use an empty string to exclude results with unset language.
  # Example:
  # languagesBlacklist:
  # - 'remove channels with language A'
  # - 'remove channels with language B'
  languagesBlacklist: []
  #
  # Only keep channels whose country equals any of these.
  # Countries are 2-character lowercase strings, such as 'us', 'ru', etc., and 'int' for international.
  # Use an empty string to include results with unset country.
  # Example:
  # countriesFilter:
  # - 'keep channels with country A'
  # - 'keep channels with country B'
  countriesFilter: []
  #
  # If true, only keep channels with countries that are in the filter and no others.
  countriesFilterStrict: false
  #
  # Remove channels whose country equals any of these.
  # Countries are 2-character lowercase strings, such as 'us', 'ru', etc., and 'int' for international.
  # Use an empty string to exclude results with unset country.
  # Example:
  # countriesBlacklist:
  # - 'remove channels with country A'
  # - 'remove channels with country B'
  countriesBlacklist: []
  #
  # Only keep channels whose status equals any of these.
  # Can be 1 (no guarantee that the channel is working) or 2 (the channel is available).
  # Example:
  # statusFilter:
  # - 1
  # - 2
  statusFilter:
  - 2
  #
  # Only keep channels whose availability is equal to or greater than this.
  # Can be between 0.0 (zero availability) and 1.0 (full availability).
  # The lower this value is, the fewer channels get removed.
  availabilityThreshold: 1.0
  #
  # Only keep channels whose availability was updated no longer ago than this.
  # The lower this value is, the more channels get removed.
  availabilityUpdatedThreshold: 36h0m0s
  #
  # Remove sources that do not respond with any content.
  removeDeadSources: false
  #
  # Try to read TS packets when removing dead sources.
  useMpegTsAnalyzer: false
  #
  # Timeout for reading the Ace Stream Engine response when removing dead sources.
  checkRespTimeout: 20s
  #
  # Template of the link to check when removing dead sources.
  # Available variables are:
  # {{.Infohash}}
  # {{.EngineAddr}}
  removeDeadLinkTemplate: http://{{.EngineAddr}}/ace/getstream?infohash={{.Infohash}}
  #
  # Number of simultaneous availability checks when removing dead sources.
  # Do not set above 1 if using the default Ace Stream Engine without a proxy.
  # If using a proxy, change `removeDeadLinkTemplate` accordingly.
  removeDeadWorkers: 1
#
# HLS format, only keep 'tv', 'music' and empty categories.
# Change category 'tv' to 'television' and empty category to 'unknown'.
- outputPath: ./out/playlist-hls-tv-+-music-+-no-category.m3u8
  headerTemplate: |
    #EXTM3U url-tvg="http://epg.one/epg2.xml.gz" tvg-shift=0 deinterlace=1 m3uautoload=1
  entryTemplate: |
    #EXTINF:-1 group-title="{{.Categories}}",{{.Name}}
    http://{{.EngineAddr}}/ace/manifest.m3u8?infohash={{.Infohash}}
  categoryRxToCategoryMap:
    (?i)^tv$: television
    ^$: unknown
  nameRxToCategoriesMap: {}
  nameRxFilter: []
  nameRxBlacklist: []
  categoriesFilter:
  - tv
  - music
  - unknown
  categoriesFilterStrict: false
  categoriesBlacklist: []
  languagesFilter: []
  languagesFilterStrict: false
  languagesBlacklist: []
  countriesFilter: []
  countriesFilterStrict: false
  countriesBlacklist: []
  statusFilter:
  - 2
  availabilityThreshold: 1.0
  availabilityUpdatedThreshold: 36h0m0s
  removeDeadSources: false
  useMpegTsAnalyzer: false
  checkRespTimeout: 20s
  removeDeadLinkTemplate: http://{{.EngineAddr}}/ace/getstream?infohash={{.Infohash}}
  removeDeadWorkers: 1
#
# https://github.com/pepsik-kiev/HTTPAceProxy format, all but erotic channels.
- outputPath: ./out/playlist-httpaceproxy-all-but-porn.m3u8
  headerTemplate: |
    #EXTM3U url-tvg="http://epg.one/epg2.xml.gz" tvg-shift=0 deinterlace=1 m3uautoload=1
  entryTemplate: |
    #EXTINF:-1 group-title="{{.Categories}}",{{.Name}}
    http://127.0.0.1:8000/infohash/{{.Infohash}}/stream.mp4
  categoryRxToCategoryMap: {}
  nameRxToCategoriesMap: {}
  nameRxFilter: []
  nameRxBlacklist:
  - (?i).*erotic.*
  - (?i).*porn.*
  - '(?i).*18\+.*'
  categoriesFilter: []
  categoriesFilterStrict: false
  categoriesBlacklist:
  - erotic_18_plus
  - 18+
  languagesFilter: []
  languagesFilterStrict: false
  languagesBlacklist: []
  countriesFilter: []
  countriesFilterStrict: false
  countriesBlacklist: []
  statusFilter:
  - 2
  availabilityThreshold: 1.0
  availabilityUpdatedThreshold: 36h0m0s
  removeDeadSources: false
  useMpegTsAnalyzer: false
  checkRespTimeout: 20s
  removeDeadLinkTemplate: http://{{.EngineAddr}}/ace/getstream?infohash={{.Infohash}}
  removeDeadWorkers: 1
```

## Build from source code [Go / Golang]

1. Install [Golang](https://golang.org/) 1.27.3 or newer.

2. Download the source code:

    ```sh
    git clone https://github.com/SCP002/m3u-gen-acestream.git
    ```

3. Install dependencies:

    ```sh
    cd m3u-gen-acestream
    go get ./...
    ```

    Or:

    ```sh
    cd m3u-gen-acestream
    go mod tidy
    ```

4. Update dependencies (optional):

    ```sh
    go get -u ./...
    ```

5. To build a binary for the current OS / architecture into the `./build/` folder:

    ```sh
    go build -trimpath -ldflags "-s -w" -o build/ .
    ```

    Or run `./build.sh` to build binaries for every OS / architecture pair.
