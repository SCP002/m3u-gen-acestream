package cli

import (
	"os"
	"testing"

	goFlags "github.com/jessevdk/go-flags"
	"github.com/stretchr/testify/assert"

	"m3u-gen-acestream/util/logger"
)

func TestParseLogLevel(t *testing.T) {
	args := os.Args
	t.Cleanup(func() { os.Args = args })

	os.Args = []string{""}
	flags, err := Parse()
	assert.NoError(t, err)
	assert.Exactly(t, logger.InfoLevel, flags.LogLevel, "should be info level by default")

	os.Args = []string{"", "--logLevel=1"}
	flags, err = Parse()
	assert.NoError(t, err)
	assert.Exactly(t, logger.TraceLevel, flags.LogLevel)

	os.Args = []string{"", "--logLevel=7"}
	flags, err = Parse()
	assert.NoError(t, err)
	assert.Exactly(t, logger.PanicLevel, flags.LogLevel)

	for _, lvl := range []string{"0", "8", "999"} {
		os.Args = []string{"", "--logLevel=" + lvl}
		_, err = Parse()
		assert.ErrorContains(t, err, "invalid log level "+lvl+", must be from 1 to 7")
		assert.True(t, IsErrOfType(err, goFlags.ErrMarshal))
	}

	os.Args = []string{"", "--logLevel=-1"}
	_, err = Parse()
	assert.True(t, IsErrOfType(err, goFlags.ErrMarshal), "should return error for negative log level")
}
