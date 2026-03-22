package httpapi

import (
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"
	"github.com/gorilla/websocket"

	"qgramm/groupchat/internal/services"
)

type Handler struct {
	svc *services.Service
}

func (h *Handler) health(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, http.StatusOK, map[string]any{"status": "ok", "service": "qgramm-groupchat"})
}

// ── Auth ──────────────────────────────────────────────────────────────────────

func (h *Handler) issueToken(w http.ResponseWriter, r *http.Request) {
	var req struct {
		UID string `json:"uid"`
	}
	if err := readJSON(r, &req); err != nil {
		handleError(w, err)
		return
	}

	userID, err := uuid.Parse(req.UID)
	if err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]any{"error": "invalid uid: must be a UUID"})
		return
	}

	token, err := h.svc.IssueToken(userID)
	if err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusOK, map[string]any{"access_token": token})
}

// ── Groups ────────────────────────────────────────────────────────────────────

func (h *Handler) createGroup(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	var req services.CreateGroupInput
	if err := readJSON(r, &req); err != nil {
		handleError(w, err)
		return
	}

	out, err := h.svc.CreateGroup(r.Context(), identity.UserID, req)
	if err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusCreated, out)
}

func (h *Handler) listGroups(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	out, err := h.svc.ListGroups(r.Context(), identity.UserID)
	if err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusOK, out)
}

func (h *Handler) getGroup(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	groupID := chi.URLParam(r, "groupID")
	out, err := h.svc.GetGroup(r.Context(), identity.UserID, groupID)
	if err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusOK, out)
}

func (h *Handler) updateGroup(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	groupID := chi.URLParam(r, "groupID")

	var req services.UpdateGroupInput
	if err := readJSON(r, &req); err != nil {
		handleError(w, err)
		return
	}

	out, err := h.svc.UpdateGroup(r.Context(), identity.UserID, groupID, req)
	if err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusOK, out)
}

func (h *Handler) deleteGroup(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	groupID := chi.URLParam(r, "groupID")
	if err := h.svc.DeleteGroup(r.Context(), identity.UserID, groupID); err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusOK, map[string]any{"ok": true})
}

// ── Members ───────────────────────────────────────────────────────────────────

func (h *Handler) listMembers(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	groupID := chi.URLParam(r, "groupID")
	out, err := h.svc.ListMembers(r.Context(), identity.UserID, groupID)
	if err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusOK, out)
}

func (h *Handler) addMember(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	groupID := chi.URLParam(r, "groupID")

	var req services.AddMemberInput
	if err := readJSON(r, &req); err != nil {
		handleError(w, err)
		return
	}

	if err := h.svc.AddMember(r.Context(), identity.UserID, groupID, req); err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusOK, map[string]any{"ok": true})
}

func (h *Handler) removeMember(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	groupID := chi.URLParam(r, "groupID")
	targetUserID := chi.URLParam(r, "userID")

	if err := h.svc.RemoveMember(r.Context(), identity.UserID, groupID, targetUserID); err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusOK, map[string]any{"ok": true})
}

// ── Messages ──────────────────────────────────────────────────────────────────

func (h *Handler) listMessages(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	groupID := chi.URLParam(r, "groupID")
	limit := parseIntDefault(r.URL.Query().Get("limit"), 100)

	var before *time.Time
	if raw := strings.TrimSpace(r.URL.Query().Get("before")); raw != "" {
		parsed, err := time.Parse(time.RFC3339Nano, raw)
		if err == nil {
			before = &parsed
		}
	}

	out, err := h.svc.ListMessages(r.Context(), identity.UserID, groupID, limit, before)
	if err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusOK, out)
}

func (h *Handler) sendMessage(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	groupID := chi.URLParam(r, "groupID")

	var req services.SendMessageInput
	if err := readJSON(r, &req); err != nil {
		handleError(w, err)
		return
	}

	out, err := h.svc.SendMessage(r.Context(), identity.UserID, groupID, req)
	if err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusCreated, out)
}

func (h *Handler) addReaction(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	groupID := chi.URLParam(r, "groupID")
	messageID := chi.URLParam(r, "messageID")

	var req struct {
		Emoji string `json:"emoji"`
	}
	if err := readJSON(r, &req); err != nil {
		handleError(w, err)
		return
	}

	if err := h.svc.AddReaction(r.Context(), identity.UserID, groupID, messageID, req.Emoji); err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusOK, map[string]any{"ok": true})
}

func (h *Handler) removeReaction(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	groupID := chi.URLParam(r, "groupID")
	messageID := chi.URLParam(r, "messageID")
	emoji := chi.URLParam(r, "emoji")

	if err := h.svc.RemoveReaction(r.Context(), identity.UserID, groupID, messageID, emoji); err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusOK, map[string]any{"ok": true})
}

func (h *Handler) reportMessage(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	groupID := chi.URLParam(r, "groupID")
	messageID := chi.URLParam(r, "messageID")

	var req services.ReportInput
	if err := readJSON(r, &req); err != nil {
		handleError(w, err)
		return
	}

	if err := h.svc.ReportMessage(r.Context(), identity.UserID, groupID, messageID, req); err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusCreated, map[string]any{"ok": true})
}

func (h *Handler) markRead(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	groupID := chi.URLParam(r, "groupID")

	var req services.MarkReadInput
	_ = readJSON(r, &req)

	if err := h.svc.MarkRead(r.Context(), identity.UserID, groupID, req); err != nil {
		handleError(w, err)
		return
	}

	writeJSON(w, http.StatusOK, map[string]any{"ok": true})
}

// ── WebSocket ─────────────────────────────────────────────────────────────────

func (h *Handler) websocket(w http.ResponseWriter, r *http.Request) {
	identity, ok := identityFromContext(r.Context())
	if !ok {
		writeJSON(w, http.StatusUnauthorized, map[string]any{"error": "unauthorized"})
		return
	}

	upgrader := websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool { return true },
	}

	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		handleError(w, err)
		return
	}

	connection := h.svc.Hub().Register(conn, identity.UserID)
	connection.Run(
		func(payload map[string]any) {
			h.svc.HandleRealtimeMessage(r.Context(), identity.UserID, payload)
		},
		func() {},
	)
}

// ── Helpers ───────────────────────────────────────────────────────────────────

func parseIntDefault(s string, def int) int {
	s = strings.TrimSpace(s)
	if s == "" {
		return def
	}
	n, err := strconv.Atoi(s)
	if err != nil {
		return def
	}
	return n
}

