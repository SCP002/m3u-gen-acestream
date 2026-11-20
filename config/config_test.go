package config

import (
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"testing"

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
	assert.Contains(t, out, "engineAddr: 127.0.0.1:6878\n#\n# Playlists", "should separate keys with an empty comment line")
	assert.Contains(t, out, "  removeDeadWorkers: 1\n#\n# HLS format",
		"should separate playlists with an empty comment line")
	assert.Contains(t, out, "  # Example:\n  # nameRxFilter:\n  # - '.*keep", "should write examples above the key")
	assert.NotRegexp(t, `(?m)^$`, strings.TrimSuffix(out, "\n"), "should not write blank lines")
	assert.NotRegexp(t, `(?m) $`, out, "should not write trailing spaces")
}

func TestInitAddNewOptions(t *testing.T) {
	log := logger.New(logger.FatalLevel, io.Discard)
	path := filepath.Join(t.TempDir(), "config.yaml")

	_, _, err := Init(log, path)
	assert.NoError(t, err)
	defBytes, err := os.ReadFile(path)
	assert.NoError(t, err)

	// Remove an option with its comment to make it added back.
	rx := regexp.MustCompile(`\n  #\n(  # .*\n)*  removeDeadWorkers: 1\n`)
	assert.Len(t, rx.FindAllIndex(defBytes, -1), 1)
	err = os.WriteFile(path, rx.ReplaceAll(defBytes, []byte("\n")), 0644)
	assert.NoError(t, err)

	cfg, isNew, err := Init(log, path)
	assert.NoError(t, err)
	assert.False(t, isNew, "should not create a new config")
	assert.Equal(t, 1, *cfg.Playlists[0].RemoveDeadWorkers, "should add removed option")

	bytes, err := os.ReadFile(path)
	assert.NoError(t, err)
	// goccy/go-yaml joins the line after "- " with the next comment line on rewrite.
	expected := strings.Replace(string(defBytes), "- #\n  # Destination", "- # Destination", 1)
	assert.Equal(t, expected, string(bytes), "should keep comments on rewrite")
}
