package main

import (
	"context"
	"fmt"
	"os"
	"time"

	"github.com/adampresley/sigint"
	"github.com/cockroachdb/errors"
	goFlags "github.com/jessevdk/go-flags"

	"m3u-gen-acestream/acestream"
	"m3u-gen-acestream/cli"
	"m3u-gen-acestream/config"
	"m3u-gen-acestream/m3u"
	"m3u-gen-acestream/updater"
	"m3u-gen-acestream/util/logger"
	"m3u-gen-acestream/util/network"
	"m3u-gen-acestream/version"
)

func main() {
	log := logger.New(logger.FatalLevel, os.Stderr)

	flags, err := cli.Parse()
	if flags.Version {
		fmt.Println(version.Version)
		os.Exit(0)
	}
	if cli.IsErrOfType(err, goFlags.ErrHelp) {
		// Help message will be prined by go-flags.
		os.Exit(0)
	}
	if err != nil {
		log.Fatal(err)
	}

	log.SetLevel(flags.LogLevel)
	logFile, err := log.AddFileWriter(flags.LogFile)
	if err == nil {
		// Closing nil file does not panic.
		defer logFile.Close()
	} else {
		log.Error(err)
	}

	sigint.Listen(func() {
		log.Warn("SIGINT or SIGTERM signal received, shutting down")
		os.Exit(0)
	})

	if flags.Update {
		updaterHttpClient := network.NewHTTPClient(time.Second * 5)
		updater := updater.New(log, updaterHttpClient)

		if err := updater.Update(); err != nil {
			log.Fatal(errors.Wrap(err, "Self update failed"))
		}
	}

	log.Info("Starting")

	cfg, isNewCfg, err := config.Init(log, flags.CfgPath)
	if err != nil {
		log.Fatal(errors.Wrap(err, "Initialize config"))
	}
	if isNewCfg {
		log.InfoFi("Created default config, please verify it and start this program again", "path", flags.CfgPath)
		os.Exit(0)
	}

	engineHttpClient := network.NewHTTPClient(time.Second * 5)
	engine := acestream.NewEngine(log, engineHttpClient, cfg.EngineAddr)
	engine.WaitForConnection(context.Background())

	results, err := engine.SearchAll(context.Background())
	if err != nil {
		log.Error(errors.Wrap(err, "Search for available ace stream channels"))
	}

	if err := m3u.Generate(log, results, cfg); err != nil {
		log.Error(errors.Wrap(err, "Generate M3U file"))
	}
}
