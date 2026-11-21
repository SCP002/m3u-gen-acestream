package logger

import (
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/cockroachdb/errors"
	"github.com/fatih/color"
	"github.com/mattn/go-isatty"
	pLog "github.com/phuslu/log"
	"github.com/samber/lo"
)

// keyValue represents phuslu log key/value pair type alias.
type keyValue = struct {
	Key       string
	Value     string
	ValueType byte
}

// Level represents log level.
type Level uint32

const (
	TraceLevel Level = Level(pLog.TraceLevel) // 1
	DebugLevel Level = Level(pLog.DebugLevel) // 2
	InfoLevel  Level = Level(pLog.InfoLevel)  // 3
	WarnLevel  Level = Level(pLog.WarnLevel)  // 4
	ErrorLevel Level = Level(pLog.ErrorLevel) // 5
	FatalLevel Level = Level(pLog.FatalLevel) // 6
	PanicLevel Level = Level(pLog.PanicLevel) // 7
)

// exitCode is an exit code of Fatal methods, the same as phuslu log uses.
const exitCode = 255

// Logger represents wrapper over logging library.
type Logger struct {
	writer *pLog.MultiEntryWriter
	logger *pLog.Logger
}

// New returns new configured logger with log level `lvl` that writes to `consoleWriter`.
//
// Output is colored if `consoleWriter` is a terminal, unless NO_COLOR environment variable is set or TERM is "dumb".
func New(lvl Level, consoleWriter io.Writer) *Logger {
	writer := pLog.MultiEntryWriter{
		&pLog.ConsoleWriter{
			Formatter: newConsoleFormatter(isColorTerminal(consoleWriter), time.DateTime),
			Writer:    consoleWriter,
		},
	}
	log := pLog.Logger{
		Level:  pLog.Level(lvl),
		Writer: &writer,
	}
	return &Logger{logger: &log, writer: &writer}
}

// SetLevel sets log level to `lvl`.
func (l Logger) SetLevel(lvl Level) {
	l.logger.SetLevel(pLog.Level(lvl))
}

// Trace prints trace level `msg`.
func (l Logger) Trace(msg any) {
	l.logger.Trace().Msg(fmt.Sprint(msg))
}

// Tracef prints trace level message from `args` in given `format`.
func (l Logger) Tracef(format string, args ...any) {
	l.logger.Trace().Msgf(format, args...)
}

// TraceFi prints trace level `msg` with formatted and colored `fields`.
func (l Logger) TraceFi(msg string, fields ...any) {
	printFields(l.logger.Trace(), msg, fields)
}

// Debug prints debug level `msg`.
func (l Logger) Debug(msg any) {
	l.logger.Debug().Msg(fmt.Sprint(msg))
}

// Debugf prints debug level message from `args` in given `format`.
func (l Logger) Debugf(format string, args ...any) {
	l.logger.Debug().Msgf(format, args...)
}

// DebugFi prints debug level `msg` with formatted and colored `fields`.
func (l Logger) DebugFi(msg string, fields ...any) {
	printFields(l.logger.Debug(), msg, fields)
}

// Info prints info level `msg`.
func (l Logger) Info(msg any) {
	l.logger.Info().Msg(fmt.Sprint(msg))
}

// Infof prints info level message from `args` in given `format`.
func (l Logger) Infof(format string, args ...any) {
	l.logger.Info().Msgf(format, args...)
}

// InfoFi prints info level `msg` with formatted and colored `fields`.
func (l Logger) InfoFi(msg string, fields ...any) {
	printFields(l.logger.Info(), msg, fields)
}

// Warn prints warning level `msg`.
func (l Logger) Warn(msg any) {
	l.logger.Warn().Msg(fmt.Sprint(msg))
}

// Warnf prints warning level message from `args` in given `format`.
func (l Logger) Warnf(format string, args ...any) {
	l.logger.Warn().Msgf(format, args...)
}

// WarnFi prints warning level `msg` with formatted and colored `fields`.
func (l Logger) WarnFi(msg string, fields ...any) {
	printFields(l.logger.Warn(), msg, fields)
}

// Error prints error level `msg`.
func (l Logger) Error(msg any) {
	l.logger.Error().Msg(fmt.Sprint(msg))
}

// Errorf prints error level message from `args` in given `format`.
func (l Logger) Errorf(format string, args ...any) {
	l.logger.Error().Msgf(format, args...)
}

// ErrorFi prints error level `msg` with formatted and colored `fields`.
func (l Logger) ErrorFi(msg string, fields ...any) {
	printFields(l.logger.Error(), msg, fields)
}

// Fatal prints fatal level `msg` and exits the program.
//
// The program exits even if fatal level is disabled and nothing is printed. The same applies to other Fatal methods.
func (l Logger) Fatal(msg any) {
	l.logger.Fatal().Msg(fmt.Sprint(msg))
	os.Exit(exitCode) // Reached only if fatal level is disabled, as phuslu log exits otherwise.
}

// Fatalf prints fatal level message from `args` in given `format` and exits the program.
func (l Logger) Fatalf(format string, args ...any) {
	l.logger.Fatal().Msgf(format, args...)
	os.Exit(exitCode)
}

// FatalFi prints fatal level `msg` with formatted and colored `fields` and exits the program.
func (l Logger) FatalFi(msg string, fields ...any) {
	printFields(l.logger.Fatal(), msg, fields)
	os.Exit(exitCode)
}

// Panic prints panic level `msg` and panics.
//
// It panics even if panic level is disabled and nothing is printed. The same applies to other Panic methods.
func (l Logger) Panic(msg any) {
	text := fmt.Sprint(msg)
	l.logger.Panic().Msg(text)
	panic(text) // Reached only if panic level is disabled, as phuslu log panics otherwise.
}

// Panicf prints panic level message from `args` in given `format` and panics.
func (l Logger) Panicf(format string, args ...any) {
	text := fmt.Sprintf(format, args...)
	l.logger.Panic().Msg(text)
	panic(text)
}

// PanicFi prints panic level `msg` with formatted and colored `fields` and panics.
func (l Logger) PanicFi(msg string, fields ...any) {
	printFields(l.logger.Panic(), msg, fields)
	panic(msg)
}

// AddFileWriter creates log file at `filePath` and adds file writer to logger.
//
// If `filePath` is empty string, it does nothing and returns nil error.
func (l Logger) AddFileWriter(filePath string) (*os.File, error) {
	if filePath == "" {
		return nil, nil
	}

	logFile, err := os.OpenFile(filePath, os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)
	if err != nil {
		return nil, errors.Wrap(err, "Open or create log file")
	}
	*l.writer = append(*l.writer, &pLog.IOWriter{
		Writer: logFile,
	})

	return logFile, nil
}

// printFields adds message `msg` and `fields` to `entry` and prints it.
//
// Errors in field values are printed as their messages.
func printFields(entry *pLog.Entry, msg string, fields []any) {
	// Not using entry.KeysAndValues() as it will not add keys which can't be converted to string by type assertion.
	var key string
	for i, field := range fields {
		if i%2 == 0 {
			key = fmt.Sprint(field)
		} else if err, ok := field.(error); ok {
			entry.Str(key, err.Error())
		} else {
			entry.Any(key, field)
		}
	}
	entry.Msg(msg)
}

// isColorTerminal returns true if `w` is a terminal and colors are not disabled with NO_COLOR environment variable or
// TERM set to "dumb", as in github.com/fatih/color, which checks stdout only.
func isColorTerminal(w io.Writer) bool {
	if os.Getenv("NO_COLOR") != "" || os.Getenv("TERM") == "dumb" {
		return false
	}
	file, ok := w.(*os.File)
	return ok && (isatty.IsTerminal(file.Fd()) || isatty.IsCygwinTerminal(file.Fd()))
}

// newConsoleFormatter returns formatter funtion with `timeFormat` for console writer.
//
// If `colorize` is true, add colors to output.
func newConsoleFormatter(colorize bool, timeFormat string) func(io.Writer, *pLog.FormatterArgs) (int, error) {
	// paint returns function coloring its arguments with `attr` if `colorize` is true.
	paint := func(attr color.Attribute) func(a ...any) string {
		c := color.New(attr)
		if colorize {
			c.EnableColor()
		} else {
			c.DisableColor()
		}
		return c.SprintFunc()
	}
	gray, cyan := paint(color.FgHiBlack), paint(color.FgCyan)
	blue, green, yellow, red := paint(color.FgBlue), paint(color.FgGreen), paint(color.FgYellow), paint(color.FgRed)
	levels := map[string]string{
		"trace": blue("TRACE"),
		"debug": blue("DEBUG"),
		"info":  green("INFO"),
		"warn":  yellow("WARN"),
		"error": red("ERROR"),
		"fatal": red("FATAL"),
		"panic": red("PANIC"),
	}

	return func(w io.Writer, a *pLog.FormatterArgs) (int, error) {
		var messageSb strings.Builder

		// Keep time as is if it can't be parsed.
		logTime := a.Time
		if parsedTime, err := time.Parse(time.RFC3339Nano, a.Time); err == nil {
			logTime = parsedTime.Format(timeFormat)
		}
		messageSb.WriteString(gray(logTime))
		messageSb.WriteRune(' ')

		if level, ok := levels[a.Level]; ok {
			messageSb.WriteString(level)
		} else {
			messageSb.WriteString(strings.ToUpper(a.Level))
		}
		messageSb.WriteRune(' ')

		if a.Caller != "" {
			messageSb.WriteString(gray(a.Caller))
			messageSb.WriteRune(' ')
		}

		messageSb.WriteString(a.Message)

		a.KeyValues = lo.Reject(a.KeyValues, func(kv keyValue, _ int) bool {
			return kv.Key == "callerfunc"
		})
		if len(a.KeyValues) > 0 {
			messageSb.WriteString(": ")
		}
		for idx, item := range a.KeyValues {
			// Escape quotes and special characters of strings only, as other values such as JSON arrays are not
			// ambiguous and would be harder to read escaped.
			value := item.Value
			if item.ValueType == 's' {
				quoted := strconv.Quote(value)
				value = quoted[1 : len(quoted)-1]
			}
			messageSb.WriteString(item.Key)
			messageSb.WriteString(" \"")
			messageSb.WriteString(cyan(value))
			messageSb.WriteRune('"')
			if idx < len(a.KeyValues)-1 {
				messageSb.WriteString(", ")
			}
		}
		messageSb.WriteRune('\n')

		return fmt.Fprint(w, messageSb.String())
	}
}
