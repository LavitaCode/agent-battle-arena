package main

import (
	"log"
	"net/http"
	"os"

	"github.com/LavitaCode/agent-battle-arena/backend-live/internal/httpserver"
)

func main() {
	addr := envOr("LIVE_API_ADDR", ":8080")
	srv := httpserver.New()

	log.Printf("backend-live (Modo B) listening on %s", addr)
	if err := http.ListenAndServe(addr, srv); err != nil {
		log.Fatalf("listen: %v", err)
	}
}

func envOr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
