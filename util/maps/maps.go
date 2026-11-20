package maps

import (
	"m3u-gen-acestream/util/logger"
	"m3u-gen-acestream/util/regex"
)

// ForEveryMatchingRx funs `cb` for every regular expression (keys in `rxMap`) matching `match`, logging to `log`.
//
// `cb` argument is a `rxMap` value.
func ForEveryMatchingRx[T any](log *logger.Logger, rxMap map[string]T, match string, cb func(mapVal T)) {
	for rx, mapVal := range rxMap {
		if regex.MatchString(log, rx, match) {
			cb(mapVal)
		}
	}
}
