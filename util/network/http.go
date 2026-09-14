package network

import (
	"net/http"
	"time"
)

// NewHTTPClient returns new HTTP client with a time limit for requests set to `timeout`.
// The proxy is taken from the environment variables HTTP_PROXY, HTTPS_PROXY and NO_PROXY.
func NewHTTPClient(timeout time.Duration) *http.Client {
	return &http.Client{
		Timeout: timeout,
		Transport: &http.Transport{
			Proxy: http.ProxyFromEnvironment,
		},
	}
}
