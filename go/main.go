package main

import (
	"context"
	"errors"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"mchack13.com/go/handlers"
	"mchack13.com/go/middleware"
)

func main() {
	// Logger set up
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
	slog.SetDefault(logger)

	// 2. Setup Configuration
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	mux := http.NewServeMux()

	// Use handlers from the 'handlers' package
	mux.HandleFunc("GET /health", handlers.Health)
	mux.HandleFunc("GET /api/v1/users/{id}", handlers.GetUser)
	mux.HandleFunc("POST /api/v1/users", handlers.CreateUser)

	// Create the Server
	// Wrap mux with the middleware from the 'middleware' package
	srv := &http.Server{
		Addr:         ":" + port,
		Handler:      middleware.Logging(mux),
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	// Graceful Shutdown Context
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	// Start Server
	go func() {
		logger.Info("Starting server", "port", port, "go_version", "1.25")
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			logger.Error("Could not start server", "error", err)
			os.Exit(1)
		}
	}()

	// Wait for Signal
	<-ctx.Done()
	logger.Info("Shutting down gracefully...")

	//  Shutdown with Timeout
	shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(shutdownCtx); err != nil {
		logger.Error("Server forced to shutdown", "error", err)
	}

	logger.Info("Server exited")
}
