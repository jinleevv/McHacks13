package handlers

import (
	"encoding/json"
	"log/slog"
	"net/http"
)

// Health checks if the server is running
func Health(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	_, err := w.Write([]byte("OK"))
	if err != nil {
		return
	}
}

// GetUser handles fetching a user by ID
func GetUser(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")

	resp := map[string]string{
		"id":   id,
		"name": "John Doe",
	}
	writeJSON(w, http.StatusOK, resp)
}

// CreateUser handles creating a new user
func CreateUser(w http.ResponseWriter, r *http.Request) {
	// In a real app, decode the body here
	resp := map[string]string{"status": "created"}
	writeJSON(w, http.StatusCreated, resp)
}

// Helper
func writeJSON(w http.ResponseWriter, status int, data any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if err := json.NewEncoder(w).Encode(data); err != nil {
		slog.Error("Failed to encode response", "error", err)
	}
}
