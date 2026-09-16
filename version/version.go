package version

// Version is the current program version.
// It is overridden at build time via -ldflags "-X m3u-gen-acestream/version.Version=vX.Y.Z".
var Version = "dev"
