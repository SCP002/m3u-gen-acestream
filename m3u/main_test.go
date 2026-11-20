package m3u

import (
	"testing"

	"go.uber.org/goleak"
)

func TestMain(m *testing.M) {
	// Clock of regexp2 match timeouts runs in background for a while after matching and stops by itself.
	goleak.VerifyTestMain(m, goleak.IgnoreAnyFunction("github.com/dlclark/regexp2.runClock"))
}
