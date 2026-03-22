package services

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"fmt"
	"log"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	"qgramm/groupchat/internal/auth"
	"qgramm/groupchat/internal/config"
	"qgramm/groupchat/internal/realtime"
)

var (
	ErrUnauthorized = errors.New("unauthorized")
	ErrForbidden    = errors.New("forbidden")
	ErrNotFound     = errors.New("not found")
	ErrBadRequest   = errors.New("bad request")
)

type Identity struct {
	UserID    uuid.UUID
	SessionID uuid.UUID
	IsRoot    bool
}

type Service struct {
	pool   *pgxpool.Pool
	cfg    config.Config
	jwt    *auth.Manager
	hub    *realtime.Hub
	pulse  *PulseClient
}

func New(pool *pgxpool.Pool, cfg config.Config, jwtManager *auth.Manager, hub *realtime.Hub) *Service {
	return &Service{
		pool:  pool,
		cfg:   cfg,
		jwt:   jwtManager,
		hub:   hub,
		pulse: NewPulseClient(cfg.Pulse.BaseURL, cfg.Pulse.TaskTimeoutSec),
	}
}

func (s *Service) Hub() *realtime.Hub {
	return s.hub
}

// IssueToken issues a signed JWT for the given user ID (no DB lookup required).
func (s *Service) IssueToken(userID uuid.UUID) (string, error) {
	token, _, err := s.jwt.Issue(userID, uuid.New(), false)
	return token, err
}

// AuthenticateAccessToken validates the JWT signature only — no DB lookup.
func (s *Service) AuthenticateAccessToken(_ context.Context, token string) (Identity, error) {
	claims, err := s.jwt.Parse(token)
	if err != nil {
		return Identity{}, fmt.Errorf("%w: invalid access token", ErrUnauthorized)
	}

	userID, err := uuid.Parse(claims.UserID)
	if err != nil {
		return Identity{}, fmt.Errorf("%w: invalid user in token", ErrUnauthorized)
	}

	sessionID, _ := uuid.Parse(claims.SessionID)
	return Identity{UserID: userID, SessionID: sessionID, IsRoot: claims.IsRoot}, nil
}

// HandleRealtimeMessage is a no-op placeholder for incoming WS messages from clients.
// Extend as needed (e.g. typing indicators).
func (s *Service) HandleRealtimeMessage(_ context.Context, _ uuid.UUID, _ map[string]any) {}

// ── Helpers ───────────────────────────────────────────────────────────────────

func realtimeEvent(kind string, payload map[string]any) realtime.Event {
	return realtime.Event{
		Type:      kind,
		Timestamp: time.Now().UTC(),
		Payload:   payload,
	}
}

func cloneMetadata(in map[string]any) map[string]any {
	if len(in) == 0 {
		return map[string]any{}
	}
	out := make(map[string]any, len(in))
	for k, v := range in {
		out[k] = v
	}
	return out
}

func parseJSONMap(raw []byte) map[string]any {
	if len(raw) == 0 {
		return map[string]any{}
	}
	out := map[string]any{}
	if err := json.Unmarshal(raw, &out); err != nil {
		log.Printf("parse json map failed: %v", err)
		return map[string]any{}
	}
	return out
}

func nullableString(ns sql.NullString) *string {
	if ns.Valid {
		v := ns.String
		return &v
	}
	return nil
}

func nullableTime(nt sql.NullTime) *time.Time {
	if nt.Valid {
		v := nt.Time
		return &v
	}
	return nil
}

// ensureGroupMembership returns ErrForbidden if the user is not in the group.
func (s *Service) ensureGroupMembership(ctx context.Context, userID uuid.UUID, groupID string) error {
	var exists bool
	err := s.pool.QueryRow(ctx,
		`SELECT EXISTS (
		     SELECT 1 FROM group_members
		     WHERE group_id = $1 AND user_id = $2
		 )`,
		groupID, userID,
	).Scan(&exists)
	if err != nil {
		return err
	}
	if !exists {
		return fmt.Errorf("%w: not a member of this group", ErrForbidden)
	}
	return nil
}

// groupMemberIDs returns all member UUIDs of a group.
func (s *Service) groupMemberIDs(ctx context.Context, groupID string) ([]uuid.UUID, error) {
	rows, err := s.pool.Query(ctx,
		`SELECT user_id FROM group_members WHERE group_id = $1`,
		groupID,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	out := make([]uuid.UUID, 0)
	for rows.Next() {
		var id uuid.UUID
		if err := rows.Scan(&id); err != nil {
			return nil, err
		}
		out = append(out, id)
	}
	return out, rows.Err()
}

// ensureGroupOwner returns ErrForbidden unless the user is owner/admin of the group.
func (s *Service) ensureGroupOwner(ctx context.Context, userID uuid.UUID, groupID string) error {
	var role string
	err := s.pool.QueryRow(ctx,
		`SELECT role FROM group_members WHERE group_id = $1 AND user_id = $2`,
		groupID, userID,
	).Scan(&role)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return fmt.Errorf("%w: not a member", ErrForbidden)
		}
		return err
	}
	if role != "owner" && role != "admin" {
		return fmt.Errorf("%w: owner or admin role required", ErrForbidden)
	}
	return nil
}

// makeGroupID returns a new group ID with "gr_" prefix.
func makeGroupID() string {
	return "gr_" + uuid.NewString()
}
