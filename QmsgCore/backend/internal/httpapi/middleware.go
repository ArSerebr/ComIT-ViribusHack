package httpapi

import (
	"context"
	"net/http"
	"strings"

	"qgramm/groupchat/internal/services"
)

type contextKey string

const identityKey contextKey = "identity"

func withIdentity(ctx context.Context, identity services.Identity) context.Context {
	return context.WithValue(ctx, identityKey, identity)
}

func identityFromContext(ctx context.Context) (services.Identity, bool) {
	v := ctx.Value(identityKey)
	if v == nil {
		return services.Identity{}, false
	}
	identity, ok := v.(services.Identity)
	return identity, ok
}

func authMiddleware(svc *services.Service) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			token := extractAccessToken(r)
			if token == "" {
				writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "missing access token"})
				return
			}

			identity, err := svc.AuthenticateAccessToken(r.Context(), token)
			if err != nil {
				handleError(w, err)
				return
			}

			next.ServeHTTP(w, r.WithContext(withIdentity(r.Context(), identity)))
		})
	}
}

func extractAccessToken(r *http.Request) string {
	raw := strings.TrimSpace(r.Header.Get("Authorization"))
	if strings.HasPrefix(strings.ToLower(raw), "bearer ") {
		return strings.TrimSpace(raw[7:])
	}
	if q := strings.TrimSpace(r.URL.Query().Get("access_token")); q != "" {
		return q
	}
	return ""
}
