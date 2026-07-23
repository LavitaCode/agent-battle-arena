package httpserver_test

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/LavitaCode/agent-battle-arena/backend-live/internal/httpserver"
)

func TestHealth(t *testing.T) {
	srv := httpserver.New()
	req := httptest.NewRequest(http.MethodGet, "/api/v1/live/health", nil)
	rec := httptest.NewRecorder()

	srv.ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("status = %d, want %d", rec.Code, http.StatusOK)
	}

	var body map[string]string
	if err := json.NewDecoder(rec.Body).Decode(&body); err != nil {
		t.Fatalf("decode: %v", err)
	}

	if body["status"] != "ok" {
		t.Errorf("status = %q, want ok", body["status"])
	}
	if body["mode"] != "live-3d" {
		t.Errorf("mode = %q, want live-3d", body["mode"])
	}
	if body["service"] != "backend-live" {
		t.Errorf("service = %q, want backend-live", body["service"])
	}
}
