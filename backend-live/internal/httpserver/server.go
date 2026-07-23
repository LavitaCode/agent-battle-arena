package httpserver

import (
	"encoding/json"
	"net/http"
)

// New returns the Modo B HTTP mux (prefix /api/v1/live).
func New() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /api/v1/live/health", handleHealth)
	return mux
}

type healthResponse struct {
	Status  string `json:"status"`
	Mode    string `json:"mode"`
	Service string `json:"service"`
}

func handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(healthResponse{
		Status:  "ok",
		Mode:    "live-3d",
		Service: "backend-live",
	})
}
