## Roadmap

In case of death of the
`http://pomoyka.win/trash/ttv-list/`
fallback to the
`https://search.acestream.net/all?api_version=1.0&api_key=test_api_key`.

Skip channel if
`'availability' < 0.8`
or
`now in seconds - 'availability_updated_at' > 8 * 86400`.

---
In case if the
`https://search.acestream.net/all?api_version=1.0&api_key=test_api_key`
becomes paid, fallback to the
`http://127.0.0.1:6878/server/api?page={0-4}&page_size=200&group_by_channels=1&show_epg=1&token={TOKEN}&method=search`.

Skip channel if
`'status' != 2`
or
`'availability' < 0.8`
or
`now in seconds - 'availability_updated_at' > 8 * 86400`.
