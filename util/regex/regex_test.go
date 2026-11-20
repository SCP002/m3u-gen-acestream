package regex

import (
	"bytes"
	"strings"
	"testing"
	"time"

	"github.com/dlclark/regexp2"
	"github.com/stretchr/testify/assert"

	"m3u-gen-acestream/util/logger"
)

func TestMatchString(t *testing.T) {
	var out bytes.Buffer
	log := logger.New(logger.DebugLevel, &out)

	assert.True(t, MatchString(log, `^a(?!b)`, "ac"))
	assert.False(t, MatchString(log, `^a(?!b)`, "ab"))
	assert.True(t, MatchString(log, `^(?P<name>a)\d$`, "a1"), "should support syntax of regexp package")
	assert.False(t, MatchString(log, `^\d$`, "٣"), `\d should match only ASCII digits, as in regexp package`)
	assert.Empty(t, out.String())
}

func TestMatchStringTimeout(t *testing.T) {
	var out bytes.Buffer
	log := logger.New(logger.DebugLevel, &out)

	// Catastrophic backtracking, with timeout shorter than default to keep the test fast.
	rx := regexp2.MustCompile(`^(a+)+$`, regexp2.RE2)
	rx.MatchTimeout = time.Millisecond * 100

	assert.False(t, matchString(log, rx, strings.Repeat("a", 40)+"b"), "should not match on timeout")
	assert.Contains(t, out.String(),
		`Matching regular expression timed out, considering it not matched: regexp "^(a+)+$"`)
}
