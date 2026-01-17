package handlers

import (
	"log/slog"
	"net/http"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin: func(r *http.Request) bool {
		return true
	},
}

func HandleStreaming(w http.ResponseWriter, r *http.Request) {

}

func HandleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		slog.Error("Failed to create connection")
	}
	defer conn.Close()
	slog.Info("New connection to websocket established")

	for {
		// ReadMessage blocks until a message is received
		messageType, message, err := conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				slog.Error("WebSocket error", "error", err)
			}
			break // Exit the loop to close connection
		}

		// 3. Log the Data
		// messageType is usually websocket.BinaryMessage (2) for images/video
		if messageType == websocket.BinaryMessage {
			slog.Info("Received video frame",
				"size_bytes", len(message),
				"type", "binary",
			)
		} else if messageType == websocket.TextMessage {
			slog.Info("Received text message", "content", string(message))
		}
	}

	slog.Info("Client disconnected")
}
