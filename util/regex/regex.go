package regex

import (
	"time"

	"github.com/dlclark/regexp2"

	"m3u-gen-acestream/util/logger"
)

// matchTimeout stops matching which takes too long, such as with catastrophic backtracking.
const matchTimeout = time.Second

// MatchString returns true if regular expression `pattern` matches `s`.
//
// `pattern` is compiled in RE2 compatibility mode and should be valid, as config validates it.
//
// On timeout of matching it logs error to `log` and returns false.
func MatchString(log *logger.Logger, pattern string, s string) bool {
	rx := regexp2.MustCompile(pattern, regexp2.RE2)
	rx.MatchTimeout = matchTimeout
	return matchString(log, rx, s)
}

// matchString returns true if `rx` matches `s`, logging timeout of matching to `log`.
func matchString(log *logger.Logger, rx *regexp2.Regexp, s string) bool {
	match, err := rx.MatchString(s)
	if err != nil {
		log.ErrorFi("Matching regular expression timed out, considering it not matched", "regexp", rx.String(),
			"input", s, "timeout", rx.MatchTimeout)
	}
	return match
}
