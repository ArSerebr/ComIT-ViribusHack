package httpapi

import (
	"net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"

	"qgramm/groupchat/internal/services"
)

func NewRouter(svc *services.Service) http.Handler {
	h := &Handler{svc: svc}

	r := chi.NewRouter()
	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Timeout(60 * time.Second))
	r.Use(cors.Handler(cors.Options{
		AllowedOrigins:   []string{"*"},
		AllowedMethods:   []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type"},
		ExposedHeaders:   []string{"Link"},
		AllowCredentials: false,
		MaxAge:           300,
	}))

	r.Get("/healthz", h.health)

	r.Route("/v1", func(r chi.Router) {
		// Public — no auth required
		r.Post("/auth/token", h.issueToken)

		r.Group(func(r chi.Router) {
			r.Use(authMiddleware(svc))

			// WebSocket
			r.Get("/ws", h.websocket)

			// Groups
			r.Post("/groups", h.createGroup)
			r.Get("/groups", h.listGroups)
			r.Get("/groups/{groupID}", h.getGroup)
			r.Patch("/groups/{groupID}", h.updateGroup)
			r.Delete("/groups/{groupID}", h.deleteGroup)

			// Members
			r.Get("/groups/{groupID}/members", h.listMembers)
			r.Post("/groups/{groupID}/members", h.addMember)
			r.Delete("/groups/{groupID}/members/{userID}", h.removeMember)

			// Messages
			r.Get("/groups/{groupID}/messages", h.listMessages)
			r.Post("/groups/{groupID}/messages", h.sendMessage)
			r.Post("/groups/{groupID}/messages/{messageID}/reactions", h.addReaction)
			r.Delete("/groups/{groupID}/messages/{messageID}/reactions/{emoji}", h.removeReaction)
			r.Post("/groups/{groupID}/messages/{messageID}/report", h.reportMessage)

			// Read cursor
			r.Post("/groups/{groupID}/read", h.markRead)
		})
	})

	return r
}
