package config

import (
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/goccy/go-yaml"
	"github.com/stretchr/testify/assert"

	"m3u-gen-acestream/util/logger"
)

func TestInitDefault(t *testing.T) {
	log := logger.New(logger.FatalLevel, io.Discard)
	path := filepath.Join(t.TempDir(), "config.yaml")

	_, isNew, err := Init(log, path)
	assert.NoError(t, err)
	assert.True(t, isNew, "should create a new config")

	cfg, isNew, err := Init(log, path)
	assert.NoError(t, err)
	assert.False(t, isNew, "should read existing config")
	defCfg, _ := newDefCfg()
	assert.Equal(t, defCfg, cfg, "should read the same config as written")

	// Test formatting of comments in the default config.
	bytes, err := os.ReadFile(path)
	assert.NoError(t, err)
	out := string(bytes)
	assert.Contains(t, out, "engineAddr: 127.0.0.1:6878\n#\n# Playlists",
		"should separate keys with an empty comment line")
	assert.Contains(t, out, "  removeDeadWorkers: 1\n#\n# HLS format",
		"should separate playlists with an empty comment line")
	assert.Contains(t, out, "  # Example:\n  # nameRxFilter:\n  # - '.*keep", "should write examples above the key")
	assert.NotRegexp(t, `(?m)^$`, strings.TrimSuffix(out, "\n"), "should not write blank lines")
	assert.NotRegexp(t, `(?m) $`, out, "should not write trailing spaces")
}

func TestAddNewOption(t *testing.T) {
	log := logger.New(logger.FatalLevel, io.Discard)
	path := "$.playlists[0].newOption"
	defComment := yaml.HeadComment("", " New option.")
	defCommentMap := yaml.CommentMap{path: []*yaml.Comment{defComment}}

	// Missing option.
	var opt *int
	commentMap := yaml.CommentMap{}
	assert.True(t, addNewOption(log, &opt, 5, path, commentMap, defCommentMap), "should add missing option")
	assert.Equal(t, 5, *opt, "should set default value")
	assert.Equal(t, defCommentMap, commentMap, "should add default comment")

	// Present option, even with zero value.
	opt = new(0)
	commentMap = yaml.CommentMap{}
	assert.False(t, addNewOption(log, &opt, 5, path, commentMap, defCommentMap), "should not add present option")
	assert.Equal(t, 0, *opt, "should keep value")
	assert.Empty(t, commentMap, "should not add comment")
}
