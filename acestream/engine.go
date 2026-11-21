package acestream

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"

	"github.com/cockroachdb/errors"
	"github.com/goccy/go-json"
	"github.com/samber/lo"

	"m3u-gen-acestream/util/logger"
)

// Engine respresents handler for Ace Stream Engine to interract with it using REST API.
type Engine struct {
	log        *logger.Logger
	httpClient *http.Client
	addr       string
	pageSize   int
}

// SearchResult represents available channels response to search request to engine.
type SearchResult struct {
	Items []Item `json:"items"`
	Name  AnyStr `json:"name"`
	Icons []Icon `json:"icons"`
}

// AnyStr made to deal with problematic 'name' field which can be both number or string.
type AnyStr string

// UnmarshalJSON implements json.Unmarshaller for custom string type.
func (s *AnyStr) UnmarshalJSON(b []byte) error {
	// Try to unmarshal as string first.
	var str string
	if err := json.Unmarshal(b, &str); err == nil {
		*s = AnyStr(str)
		return nil
	}

	// Fallback: treat anything else as string.
	*s = AnyStr(b)
	return nil
}

// Item represents item in SearchResult.
type Item struct {
	Status                int      `json:"status"`
	Languages             []string `json:"languages"`
	Name                  string   `json:"name"`
	Countries             []string `json:"countries"`
	Infohash              string   `json:"infohash"`
	ChannelID             int      `json:"channel_id"`
	AvailabilityUpdatedAt int64    `json:"availability_updated_at"`
	Availability          float64  `json:"availability"`
	Categories            []string `json:"categories"`
}

// Icon represents icon in SearchResult.
type Icon struct {
	URL  string `json:"url"`
	Type int    `json:"type"`
}

// versionResp represents response to version request to engine.
type versionResp struct {
	Result struct {
		Code     int    `json:"code"`
		Platform string `json:"platform"`
		Version  string `json:"version"`
	} `json:"result"`
	Error any `json:"error"`
}

// searchResp represents response to search request to engine.
type searchResp struct {
	Result struct {
		Total   int            `json:"total"`
		Results []SearchResult `json:"results"`
		Time    float64        `json:"time"`
	} `json:"result"`
}

// NewEngine returns new engine handler with it's address at `addr`, which should be in format of 'host:port'.
func NewEngine(log *logger.Logger, httpClient *http.Client, addr string) *Engine {
	return &Engine{log: log, httpClient: httpClient, addr: addr, pageSize: 200}
}

// WaitForConnection blocks current goroutine until engine responds with version info or until `ctx` is done.
// Returns error only if `ctx` is done before engine responded.
func (e Engine) WaitForConnection(ctx context.Context) error {
	e.log.Info("Connecting to engine")

	ticker := time.NewTicker(time.Second * 5)
	defer ticker.Stop()

	for {
		err := e.getVersion(ctx)
		if err == nil {
			e.log.Info("Engine is running")
			return nil
		}
		if ctx.Err() != nil {
			return errors.Wrap(ctx.Err(), "Connect to engine")
		}
		e.log.Error(errors.Wrap(err, "Connect to engine"))
		e.log.Debug("Sleeping before reconnect")
		select {
		case <-ctx.Done():
			return errors.Wrap(ctx.Err(), "Connect to engine")
		case <-ticker.C:
		}
	}
}

// getVersion requests version info from engine and returns error if engine did not respond properly.
func (e Engine) getVersion(ctx context.Context) error {
	params := url.Values{}
	params.Set("method", "get_version")
	url := url.URL{Scheme: "http", Host: e.addr, Path: "webui/api/service", RawQuery: params.Encode()}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url.String(), nil)
	if err != nil {
		return errors.Wrap(err, "Create get_version request")
	}
	resp, err := e.httpClient.Do(req)
	if err != nil {
		return errors.Wrap(err, "Send get_version request")
	}
	body, err := io.ReadAll(resp.Body)
	_ = resp.Body.Close()
	if err != nil {
		return errors.Wrap(err, "Read get_version response body")
	}
	var version versionResp
	if err := json.Unmarshal(body, &version); err != nil {
		return errors.Wrap(err, "Decode get_version response body as JSON")
	}
	if version.Result.Code == 0 || version.Error != nil {
		return errors.Newf("Bad engine response: %+v", version)
	}
	return nil
}

// SearchAll returns all currently available ace stream channels.
func (e Engine) SearchAll(ctx context.Context) ([]SearchResult, error) {
	e.log.Info("Searching for channels")
	results := []SearchResult{}
	for page := 0; ; page++ {
		currResults, err := e.searchAtPage(ctx, page)
		if err != nil {
			return results, errors.Wrapf(err, "Search at page %v", page)
		}
		results = append(results, currResults...)
		if len(currResults) < e.pageSize {
			return results, nil
		}
	}
}

// searchAtPage returns ace stream channels at page `page` with page size defined in engine instance.
func (e Engine) searchAtPage(ctx context.Context, page int) ([]SearchResult, error) {
	params := url.Values{}
	params.Set("page_size", fmt.Sprint(e.pageSize))
	params.Set("page", fmt.Sprint(page))
	url := url.URL{Scheme: "http", Host: e.addr, Path: "search", RawQuery: params.Encode()}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url.String(), nil)
	if err != nil {
		return []SearchResult{}, errors.Wrap(err, "Create search request")
	}
	resp, err := e.httpClient.Do(req)
	if err != nil {
		return []SearchResult{}, errors.Wrap(err, "Send search request")
	}
	defer func() { _ = resp.Body.Close() }()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return []SearchResult{}, errors.Wrap(err, "Read search response body")
	}
	var out searchResp
	err = json.Unmarshal(body, &out)
	if err != nil {
		return []SearchResult{}, errors.Wrap(err, "Decode search response body as JSON")
	}
	e.log.InfoFi("Received", "channels", len(out.Result.Results), "sources", GetSourcesAmount(out.Result.Results),
		"page", page)
	return out.Result.Results, nil
}

// GetSourcesAmount returns total amount of Item's in `searchResults`.
func GetSourcesAmount(searchResults []SearchResult) int {
	return lo.SumBy(searchResults, func(sr SearchResult) int {
		return len(sr.Items)
	})
}
