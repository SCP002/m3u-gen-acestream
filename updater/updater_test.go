package updater

import (
	"bytes"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strconv"
	"sync/atomic"
	"testing"
	"time"

	"github.com/goccy/go-json"
	"github.com/stretchr/testify/assert"

	"m3u-gen-acestream/util/logger"
	"m3u-gen-acestream/util/network"
)

var (
	oldBinary = []byte("old binary")
	newBinary = []byte("new binary")
)

// fakeGithub represents a fake github server with a release available.
type fakeGithub struct {
	*httptest.Server
	tagName        string
	binary         []byte
	omitBinary     bool
	truncateBinary bool
	releaseStatus  int
	binaryStatus   int
	binaryRequests atomic.Int32
}

// newFakeGithub returns new started server with release `v2.0.0` containing `newBinary`.
func newFakeGithub(t *testing.T) *fakeGithub {
	f := &fakeGithub{
		tagName:       "v2.0.0",
		binary:        newBinary,
		releaseStatus: http.StatusOK,
		binaryStatus:  http.StatusOK,
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/latest", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(f.releaseStatus)
		assets := []Asset{}
		if !f.omitBinary {
			assets = append(assets, Asset{Name: getBinaryName(), BrowserDownloadURL: f.URL + "/binary"})
		}
		_ = json.NewEncoder(w).Encode(Release{TagName: f.tagName, Assets: assets})
	})
	mux.HandleFunc("/binary", func(w http.ResponseWriter, _ *http.Request) {
		f.binaryRequests.Add(1)
		if f.truncateBinary {
			// Promise more than is sent, so the connection breaks in the middle of the body.
			w.Header().Set("Content-Length", strconv.Itoa(len(f.binary)*2))
		}
		w.WriteHeader(f.binaryStatus)
		_, _ = w.Write(f.binary)
	})
	f.Server = httptest.NewServer(mux)
	t.Cleanup(f.Close)

	return f
}

// newTestUpdater returns new updater of version `currentVersion` which works with `github` and a temporary executable.
func newTestUpdater(t *testing.T, github *fakeGithub, currentVersion string) *Updater {
	targetPath := filepath.Join(t.TempDir(), "program")
	assert.NoError(t, os.WriteFile(targetPath, oldBinary, 0o755))

	httpClient := network.NewHTTPClient(time.Second * 5)
	t.Cleanup(httpClient.CloseIdleConnections)

	u := New(logger.New(logger.DebugLevel, &bytes.Buffer{}), httpClient)
	u.currentVersion = currentVersion
	u.latestReleaseUrl = github.URL + "/latest"
	u.targetPath = targetPath
	return u
}

// assertExecutable asserts that the executable of `u` has content of `expected` and no temporary files are left.
func assertExecutable(t *testing.T, u *Updater, expected []byte) {
	actual, err := os.ReadFile(u.targetPath)
	assert.NoError(t, err)
	assert.Equal(t, string(expected), string(actual))

	entries, err := os.ReadDir(filepath.Dir(u.targetPath))
	assert.NoError(t, err)
	names := []string{}
	for _, entry := range entries {
		names = append(names, entry.Name())
	}
	assert.Equal(t, []string{filepath.Base(u.targetPath)}, names)
}

func TestUpdateReplacesExecutable(t *testing.T) {
	github := newFakeGithub(t)
	u := newTestUpdater(t, github, "v1.0.0")

	assert.NoError(t, u.Update())

	assertExecutable(t, u, newBinary)
}

func TestUpdateDoesNothingIfOnLatest(t *testing.T) {
	github := newFakeGithub(t)
	u := newTestUpdater(t, github, "v2.0.0")

	assert.NoError(t, u.Update())

	assertExecutable(t, u, oldBinary)
	assert.Zero(t, github.binaryRequests.Load())
}

func TestUpdateRefusesDevelopmentBuild(t *testing.T) {
	github := newFakeGithub(t)
	u := newTestUpdater(t, github, "dev")

	assert.ErrorContains(t, u.Update(), `Current version "dev" is not a release`)

	assertExecutable(t, u, oldBinary)
	assert.Zero(t, github.binaryRequests.Load())
}

func TestUpdateFailsOnReleaseRequestError(t *testing.T) {
	github := newFakeGithub(t)
	github.releaseStatus = http.StatusForbidden
	u := newTestUpdater(t, github, "v1.0.0")

	assert.ErrorContains(t, u.Update(), "Unexpected response status")

	assertExecutable(t, u, oldBinary)
}

func TestUpdateFailsIfReleaseHasNoBinary(t *testing.T) {
	github := newFakeGithub(t)
	github.omitBinary = true
	u := newTestUpdater(t, github, "v1.0.0")

	assert.ErrorContains(t, u.Update(), "No URL found for binary")

	assertExecutable(t, u, oldBinary)
}

func TestUpdateKeepsExecutableOnDownloadError(t *testing.T) {
	github := newFakeGithub(t)
	github.binaryStatus = http.StatusNotFound
	github.binary = []byte("<!DOCTYPE html>")
	u := newTestUpdater(t, github, "v1.0.0")

	assert.ErrorContains(t, u.Update(), "Unexpected response status")

	assertExecutable(t, u, oldBinary)
}

func TestUpdateKeepsExecutableOnInterruptedDownload(t *testing.T) {
	github := newFakeGithub(t)
	github.truncateBinary = true
	u := newTestUpdater(t, github, "v1.0.0")

	assert.ErrorContains(t, u.Update(), "Update executable")

	assertExecutable(t, u, oldBinary)
}
