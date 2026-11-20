package updater

import (
	"fmt"
	"io"
	"net/http"
	"runtime"

	"github.com/cockroachdb/errors"
	"github.com/fynelabs/selfupdate"
	"github.com/goccy/go-json"
	"github.com/samber/lo"
	"golang.org/x/mod/semver"

	"m3u-gen-acestream/util/logger"
	"m3u-gen-acestream/version"
)

// latestReleaseUrl is the github API endpoint returning latest release info.
const latestReleaseUrl = "https://api.github.com/repos/SCP002/m3u-gen-acestream/releases/latest"

// Updater represents update handler for this program.
type Updater struct {
	log              *logger.Logger
	httpClient       *http.Client
	currentVersion   string
	latestReleaseUrl string
	// Empty value means the running executable. Set only in tests.
	targetPath string
}

// New returns new updater.
func New(log *logger.Logger, httpClient *http.Client) *Updater {
	return &Updater{
		log:              log,
		httpClient:       httpClient,
		currentVersion:   version.Version,
		latestReleaseUrl: latestReleaseUrl,
	}
}

// Release represents github release.
type Release struct {
	TagName string  `json:"tag_name"`
	Assets  []Asset `json:"assets"`
}

// Asset represents github release asset.
type Asset struct {
	Name               string `json:"name"`
	BrowserDownloadURL string `json:"browser_download_url"`
}

// Update replaces the executable with the latest release if it is newer than the current version. The new version
// takes effect on the next start of this program.
//
// It returns error if the current version is not a semantic version, such as a development build.
func (u Updater) Update() error {
	if !semver.IsValid(u.currentVersion) {
		return errors.Newf("Current version %q is not a release, download a release manually", u.currentVersion)
	}

	release, err := u.getLatestRelease()
	if err != nil {
		return errors.Wrap(err, "Get latest release info")
	}

	if semver.Compare(release.TagName, u.currentVersion) <= 0 {
		u.log.InfoFi("No update available", "current version", u.currentVersion, "latest version", release.TagName)
		return nil
	}

	u.log.InfoFi("Update is available", "new version", release.TagName)

	downloadUrl, err := getDownloadUrl(release.Assets)
	if err != nil {
		return errors.Wrap(err, "Get download URL")
	}

	u.log.InfoFi("Found binary", "URL", downloadUrl)

	if err := u.doUpdate(downloadUrl); err != nil {
		return err
	}

	u.log.InfoFi("Update installed, please start this program again", "old version", u.currentVersion, "new version",
		release.TagName)

	return nil
}

// doUpdate updates executable to the binary provided at `url`.
func (u Updater) doUpdate(url string) error {
	u.log.Info("Downloading and installing update")
	resp, err := u.get(url)
	if err != nil {
		return errors.Wrap(err, "Download binary")
	}
	defer func() { _ = resp.Body.Close() }()

	err = selfupdate.Apply(resp.Body, selfupdate.Options{TargetPath: u.targetPath})
	if rollbackErr := selfupdate.RollbackError(err); rollbackErr != nil {
		return errors.Wrapf(rollbackErr, "Update failed (%v), reinstall manually, restore old executable", err)
	}
	if err != nil {
		return errors.Wrap(err, "Update executable")
	}

	return nil
}

// getLatestRelease returns latest release info.
func (u Updater) getLatestRelease() (Release, error) {
	resp, err := u.get(u.latestReleaseUrl)
	if err != nil {
		return Release{}, err
	}
	defer func() { _ = resp.Body.Close() }()
	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return Release{}, errors.Wrap(err, "Read response body")
	}
	var release Release
	err = json.Unmarshal(respBody, &release)
	if err != nil {
		return Release{}, errors.Wrap(err, "Decode response body as JSON")
	}
	if release.TagName == "" {
		return Release{}, errors.New("Release tag name is empty")
	}
	return release, nil
}

// get sends get request to `url` and returns response if its status is 200 OK.
func (u Updater) get(url string) (*http.Response, error) {
	resp, err := u.httpClient.Get(url)
	if err != nil {
		return nil, errors.Wrap(err, "Send get request")
	}
	if resp.StatusCode != http.StatusOK {
		_ = resp.Body.Close()
		return nil, errors.Newf("Unexpected response status for %v: %v", url, resp.Status)
	}
	return resp, nil
}

// getBinaryName returns release asset name of a binary for the current OS and architecture.
func getBinaryName() string {
	name := fmt.Sprintf("m3u-gen-acestream-%v-%v", runtime.GOOS, runtime.GOARCH)
	if runtime.GOOS == "windows" {
		name += ".exe"
	}
	return name
}

// getDownloadUrl returns proper URL to download a binary in `assets`.
func getDownloadUrl(assets []Asset) (string, error) {
	requiredName := getBinaryName()
	asset, found := lo.Find(assets, func(asset Asset) bool {
		return asset.Name == requiredName
	})
	if found {
		return asset.BrowserDownloadURL, nil
	}
	return "", errors.Newf("No URL found for binary matching the name: %v", requiredName)
}
