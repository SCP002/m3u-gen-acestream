package logger

import (
	"bufio"
	"bytes"
	"encoding/json"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"testing"
	"time"

	"github.com/cockroachdb/errors"
	pLog "github.com/phuslu/log"
	"github.com/stretchr/testify/assert"
)

var timeRx = `[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}`

func TestNew(t *testing.T) {
	var buf bytes.Buffer
	log := New(DebugLevel, &buf)
	log.Trace("message")
	log.Debug("message")
	out := buf.String()
	assert.NotRegexp(t, regexp.MustCompile(`TRACE`), out, "should not print trace messages with debug level logger")
	assert.Regexp(t, regexp.MustCompile(timeRx+` DEBUG message\n`), out)
}

func TestLevels(t *testing.T) {
	levels := []struct {
		name   string
		plain  func(Logger, any)
		format func(Logger, string, ...any)
		withFi func(Logger, string, ...any)
		panics bool
		exits  bool
	}{
		{name: "TRACE", plain: Logger.Trace, format: Logger.Tracef, withFi: Logger.TraceFi},
		{name: "DEBUG", plain: Logger.Debug, format: Logger.Debugf, withFi: Logger.DebugFi},
		{name: "INFO", plain: Logger.Info, format: Logger.Infof, withFi: Logger.InfoFi},
		{name: "WARN", plain: Logger.Warn, format: Logger.Warnf, withFi: Logger.WarnFi},
		{name: "ERROR", plain: Logger.Error, format: Logger.Errorf, withFi: Logger.ErrorFi},
		{name: "PANIC", plain: Logger.Panic, format: Logger.Panicf, withFi: Logger.PanicFi, panics: true},
		{name: "FATAL", plain: Logger.Fatal, format: Logger.Fatalf, withFi: Logger.FatalFi, exits: true},
	}
	for _, lvl := range levels {
		calls := []struct {
			name string
			call func(Logger)
			want string
		}{
			{name: "plain", call: func(l Logger) { lvl.plain(l, "message") }, want: `message`},
			{name: "format", call: func(l Logger) { lvl.format(l, "%v + %v", "message 1", "message 2") },
				want: `message 1 \+ message 2`},
			{name: "fields", call: func(l Logger) { lvl.withFi(l, "message", "a", "b", 1, 2) },
				want: `message: a "b", 1 "2"`},
			{name: "no fields", call: func(l Logger) { lvl.withFi(l, "message") }, want: `message`},
		}
		for _, c := range calls {
			t.Run(lvl.name+"/"+c.name, func(t *testing.T) {
				wantRx := regexp.MustCompile(timeRx + ` ` + lvl.name + ` ` + c.want + `\n`)
				if lvl.exits {
					assertExits(t, func() { c.call(*New(TraceLevel, os.Stderr)) }, wantRx)
					return
				}
				var buf bytes.Buffer
				log := New(TraceLevel, &buf)
				if lvl.panics {
					assert.Panics(t, func() { c.call(*log) })
				} else {
					c.call(*log)
				}
				assert.Regexp(t, wantRx, buf.String())
			})
		}
	}
}

// assertExits runs `fn` in a new process of the current test and asserts it exits with code 255 and output matching
// `wantRx`.
func assertExits(t *testing.T, fn func(), wantRx *regexp.Regexp) {
	t.Helper()
	const env = "LOGGER_TEST_EXIT"
	if os.Getenv(env) == "1" {
		fn()
		return
	}
	// Anchor every part of the name, as -test.run matches every part of the subtest name separately.
	parts := strings.Split(t.Name(), "/")
	for i, part := range parts {
		parts[i] = "^" + regexp.QuoteMeta(part) + "$"
	}
	cmd := exec.Command(os.Args[0], "-test.run="+strings.Join(parts, "/"))
	cmd.Env = append(os.Environ(), env+"=1")
	out, err := cmd.CombinedOutput()
	var exitErr *exec.ExitError
	if assert.ErrorAs(t, err, &exitErr, "should exit with error") {
		assert.Exactly(t, 255, exitErr.ExitCode())
	}
	assert.Regexp(t, wantRx, string(out))
}

func TestAddFileWriter(t *testing.T) {
	path := filepath.Join(t.TempDir(), "test.log")

	log := New(DebugLevel, os.Stderr)
	file, err := log.AddFileWriter("")
	assert.NoError(t, err, "should not return error for empty file path")
	assert.Nil(t, file, "should return nil file for empty file path")

	file, err = log.AddFileWriter(path)
	assert.NoError(t, err)
	assert.NotNil(t, file)
	assert.FileExists(t, path)

	log.InfoFi("message 1", "field1", "value 1", "field2", 2)
	log.WarnFi("message 2", "field1", "value 3", "field2", 4)

	// file.Sync() does not help, content is empty, closing and opening the file again.
	_ = file.Close()
	file, err = os.Open(path)
	assert.NoError(t, err)
	defer func() { _ = file.Close() }()
	reader := bufio.NewReader(file)

	type logEntry struct {
		Time    string `json:"time"`
		Level   string `json:"level"`
		Field1  string `json:"field1"`
		Field2  int    `json:"field2"`
		Message string `json:"message"`
	}

	var entry logEntry

	line, err := reader.ReadBytes('\n')
	assert.NoError(t, err)
	err = json.Unmarshal(line, &entry)
	assert.NoError(t, err)
	_, err = time.Parse(time.RFC3339Nano, entry.Time)
	assert.NoError(t, err, "time in entry must be in RFC3339 format with millis")
	assert.Exactly(t, "info", entry.Level, "log severity must be that level")
	assert.Exactly(t, "value 1", entry.Field1)
	assert.Exactly(t, 2, entry.Field2)
	assert.Exactly(t, "message 1", entry.Message)

	line, err = reader.ReadBytes('\n')
	assert.NoError(t, err)
	err = json.Unmarshal(line, &entry)
	assert.NoError(t, err)
	_, err = time.Parse(time.RFC3339Nano, entry.Time)
	assert.NoError(t, err, "time in entry must be in RFC3339 format with millis")
	assert.Exactly(t, "warn", entry.Level, "log severity must be that level")
	assert.Exactly(t, "value 3", entry.Field1)
	assert.Exactly(t, 4, entry.Field2)
	assert.Exactly(t, "message 2", entry.Message)
}

func TestDisabledFatalAndPanic(t *testing.T) {
	// Fatal level is disabled by panic level, but the program should exit anyway.
	calls := []struct {
		name string
		call func(Logger)
	}{
		{name: "plain", call: func(l Logger) { l.Fatal("message") }},
		{name: "format", call: func(l Logger) { l.Fatalf("%v", "message") }},
		{name: "fields", call: func(l Logger) { l.FatalFi("message", "a", "b") }},
	}
	for _, c := range calls {
		t.Run("fatal/"+c.name, func(t *testing.T) {
			assertExits(t, func() { c.call(*New(PanicLevel, os.Stderr)) }, regexp.MustCompile(`^$`))
		})
	}

	// Panic level is disabled by any higher level, but the program should panic anyway.
	var buf bytes.Buffer
	log := New(PanicLevel+1, &buf)
	assert.PanicsWithValue(t, "message", func() { log.Panic("message") })
	assert.PanicsWithValue(t, "message 1", func() { log.Panicf("message %v", 1) })
	assert.PanicsWithValue(t, "message", func() { log.PanicFi("message", "a", "b") })
	assert.Empty(t, buf.String(), "should not print disabled messages")
}

func TestSetLevel(t *testing.T) {
	var buf bytes.Buffer
	log := New(InfoLevel, &buf)
	log.Debug("message 1")
	log.SetLevel(DebugLevel)
	log.Debug("message 2")
	assert.NotContains(t, buf.String(), "message 1")
	assert.Contains(t, buf.String(), "DEBUG message 2")
}

func TestFields(t *testing.T) {
	var buf bytes.Buffer
	log := New(InfoLevel, &buf)

	log.InfoFi("message", "quoted", `say "hi"`, "multiline", "a\nb", "cyrillic", "Канал")
	assert.Contains(t, buf.String(), `message: quoted "say \"hi\"", multiline "a\nb", cyrillic "Канал"`+"\n",
		"should escape quotes and special characters only")

	buf.Reset()
	log.InfoFi("message", "list", []string{"a", "b"}, "number", 1, "flag", true)
	assert.Contains(t, buf.String(), `message: list "["a","b"]", number "1", flag "true"`,
		"should not escape values other than strings")

	buf.Reset()
	log.InfoFi("message", "error", errors.Wrap(errors.New("cause"), "context"))
	assert.Contains(t, buf.String(), `message: error "context: cause"`, "should print error message")
}

func TestColors(t *testing.T) {
	var buf bytes.Buffer
	New(InfoLevel, &buf).InfoFi("message", "a", "b")
	assert.NotContains(t, buf.String(), "\x1b[", "should not color output which is not a terminal")

	assert.False(t, isColorTerminal(&buf), "should not color writers other than files")
	t.Setenv("NO_COLOR", "1")
	assert.False(t, isColorTerminal(os.Stderr), "should not color output with NO_COLOR set")

	format := func(colorize bool) string {
		var out bytes.Buffer
		args := pLog.FormatterArgs{
			Time:      "2026-01-02T03:04:05.678Z",
			Level:     "info",
			Message:   "message",
			KeyValues: []keyValue{{Key: "a", Value: "b", ValueType: 's'}},
		}
		_, err := newConsoleFormatter(colorize, time.DateTime)(&out, &args)
		assert.NoError(t, err)
		return out.String()
	}
	assert.Exactly(t, "2026-01-02 03:04:05 INFO message: a \"b\"\n", format(false))
	colored := format(true)
	assert.Contains(t, colored, "\x1b[", "should color output regardless of stdout")
	assert.Contains(t, colored, "\x1b[32mINFO\x1b[0m", "should color level")
	assert.Contains(t, colored, "a \"\x1b[36mb\x1b[0m\"", "should color value without quotes")
}

func TestFormatterBadTime(t *testing.T) {
	var out bytes.Buffer
	args := pLog.FormatterArgs{Time: "not a time", Level: "info", Message: "message"}
	_, err := newConsoleFormatter(false, time.DateTime)(&out, &args)
	assert.NoError(t, err)
	assert.Exactly(t, "not a time INFO message\n", out.String(), "should keep message with unparsable time")
}
