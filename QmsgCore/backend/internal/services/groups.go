package services

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
)

// ── Group CRUD ────────────────────────────────────────────────────────────────

func (s *Service) CreateGroup(ctx context.Context, creatorID uuid.UUID, in CreateGroupInput) (GroupView, error) {
	name := strings.TrimSpace(in.Name)
	if name == "" {
		return GroupView{}, fmt.Errorf("%w: name is required", ErrBadRequest)
	}

	groupID := makeGroupID()
	now := time.Now().UTC()

	tx, err := s.pool.BeginTx(ctx, pgx.TxOptions{})
	if err != nil {
		return GroupView{}, err
	}
	defer func() {
		if err != nil {
			_ = tx.Rollback(ctx)
		}
	}()

	_, err = tx.Exec(ctx,
		`INSERT INTO group_chats (id, name, created_by_user_id, created_at, updated_at)
		 VALUES ($1, $2, $3, $4, $4)`,
		groupID, name, creatorID, now,
	)
	if err != nil {
		return GroupView{}, err
	}

	_, err = tx.Exec(ctx,
		`INSERT INTO group_members (group_id, user_id, role, joined_at)
		 VALUES ($1, $2, 'owner', $3)`,
		groupID, creatorID, now,
	)
	if err != nil {
		return GroupView{}, err
	}

	if err = tx.Commit(ctx); err != nil {
		return GroupView{}, err
	}

	return GroupView{
		ID:          groupID,
		Name:        name,
		CreatedByID: creatorID.String(),
		CreatedAt:   now,
		UpdatedAt:   now,
		MemberIDs:   []string{creatorID.String()},
		UnreadCount: 0,
	}, nil
}

func (s *Service) GetGroup(ctx context.Context, userID uuid.UUID, groupID string) (GroupView, error) {
	if err := s.ensureGroupMembership(ctx, userID, groupID); err != nil {
		return GroupView{}, err
	}
	return s.loadGroup(ctx, userID, groupID)
}

func (s *Service) UpdateGroup(ctx context.Context, userID uuid.UUID, groupID string, in UpdateGroupInput) (GroupView, error) {
	if err := s.ensureGroupOwner(ctx, userID, groupID); err != nil {
		return GroupView{}, err
	}

	name := strings.TrimSpace(in.Name)
	if name == "" {
		return GroupView{}, fmt.Errorf("%w: name is required", ErrBadRequest)
	}

	avatarURL := strings.TrimSpace(in.AvatarURL)

	_, err := s.pool.Exec(ctx,
		`UPDATE group_chats SET name = $2, avatar_url = NULLIF($3,''), updated_at = NOW()
		 WHERE id = $1`,
		groupID, name, avatarURL,
	)
	if err != nil {
		return GroupView{}, err
	}

	view, err := s.loadGroup(ctx, userID, groupID)
	if err != nil {
		return GroupView{}, err
	}

	memberIDs, _ := s.groupMemberIDs(ctx, groupID)
	s.hub.BroadcastToUsers(memberIDs, realtimeEvent("group.updated", map[string]any{
		"group": view,
	}))

	return view, nil
}

func (s *Service) DeleteGroup(ctx context.Context, userID uuid.UUID, groupID string) error {
	if err := s.ensureGroupOwner(ctx, userID, groupID); err != nil {
		return err
	}

	memberIDs, _ := s.groupMemberIDs(ctx, groupID)

	_, err := s.pool.Exec(ctx, `DELETE FROM group_chats WHERE id = $1`, groupID)
	if err != nil {
		return err
	}

	s.hub.BroadcastToUsers(memberIDs, realtimeEvent("group.deleted", map[string]any{
		"group_id": groupID,
	}))

	return nil
}

func (s *Service) ListGroups(ctx context.Context, userID uuid.UUID) ([]GroupView, error) {
	rows, err := s.pool.Query(ctx,
		`SELECT g.id, g.name, COALESCE(g.avatar_url, ''), g.created_by_user_id::text,
		        g.created_at, g.updated_at,
		        COALESCE(me.unread_count, 0),
		        ARRAY(
		            SELECT gm2.user_id::text
		            FROM group_members gm2
		            WHERE gm2.group_id = g.id
		            ORDER BY gm2.joined_at ASC
		        ) AS member_ids
		 FROM group_chats g
		 JOIN group_members me ON me.group_id = g.id AND me.user_id = $1
		 ORDER BY g.updated_at DESC`,
		userID,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	out := make([]GroupView, 0)
	for rows.Next() {
		var v GroupView
		if scanErr := rows.Scan(
			&v.ID, &v.Name, &v.AvatarURL, &v.CreatedByID,
			&v.CreatedAt, &v.UpdatedAt, &v.UnreadCount, &v.MemberIDs,
		); scanErr != nil {
			return nil, scanErr
		}
		out = append(out, v)
	}
	return out, rows.Err()
}

func (s *Service) loadGroup(ctx context.Context, userID uuid.UUID, groupID string) (GroupView, error) {
	var v GroupView
	var avatarURL sql.NullString

	err := s.pool.QueryRow(ctx,
		`SELECT g.id, g.name, g.avatar_url, g.created_by_user_id::text,
		        g.created_at, g.updated_at,
		        COALESCE(me.unread_count, 0),
		        ARRAY(
		            SELECT gm2.user_id::text
		            FROM group_members gm2
		            WHERE gm2.group_id = g.id
		            ORDER BY gm2.joined_at ASC
		        ) AS member_ids
		 FROM group_chats g
		 JOIN group_members me ON me.group_id = g.id AND me.user_id = $2
		 WHERE g.id = $1`,
		groupID, userID,
	).Scan(
		&v.ID, &v.Name, &avatarURL, &v.CreatedByID,
		&v.CreatedAt, &v.UpdatedAt, &v.UnreadCount, &v.MemberIDs,
	)
	if err != nil {
		if err == pgx.ErrNoRows {
			return GroupView{}, ErrNotFound
		}
		return GroupView{}, err
	}

	if avatarURL.Valid {
		v.AvatarURL = avatarURL.String
	}

	return v, nil
}

// ── Membership ────────────────────────────────────────────────────────────────

func (s *Service) ListMembers(ctx context.Context, userID uuid.UUID, groupID string) ([]GroupMemberView, error) {
	if err := s.ensureGroupMembership(ctx, userID, groupID); err != nil {
		return nil, err
	}

	rows, err := s.pool.Query(ctx,
		`SELECT user_id::text, role, joined_at
		 FROM group_members WHERE group_id = $1 ORDER BY joined_at ASC`,
		groupID,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	out := make([]GroupMemberView, 0)
	for rows.Next() {
		var m GroupMemberView
		if err := rows.Scan(&m.UserID, &m.Role, &m.JoinedAt); err != nil {
			return nil, err
		}
		out = append(out, m)
	}
	return out, rows.Err()
}

func (s *Service) AddMember(ctx context.Context, requestorID uuid.UUID, groupID string, in AddMemberInput) error {
	if err := s.ensureGroupOwner(ctx, requestorID, groupID); err != nil {
		return err
	}

	targetID, err := uuid.Parse(in.UserID)
	if err != nil {
		return fmt.Errorf("%w: invalid user_id", ErrBadRequest)
	}

	_, err = s.pool.Exec(ctx,
		`INSERT INTO group_members (group_id, user_id, role, joined_at)
		 VALUES ($1, $2, 'member', NOW())
		 ON CONFLICT (group_id, user_id) DO NOTHING`,
		groupID, targetID,
	)
	if err != nil {
		return err
	}

	memberIDs, _ := s.groupMemberIDs(ctx, groupID)
	s.hub.BroadcastToUsers(memberIDs, realtimeEvent("member.joined", map[string]any{
		"group_id": groupID,
		"user_id":  targetID.String(),
	}))

	return nil
}

func (s *Service) RemoveMember(ctx context.Context, requestorID uuid.UUID, groupID, targetIDStr string) error {
	targetID, err := uuid.Parse(targetIDStr)
	if err != nil {
		return fmt.Errorf("%w: invalid user_id", ErrBadRequest)
	}

	// Allow self-removal (leave) or owner/admin kicking others.
	if requestorID != targetID {
		if err := s.ensureGroupOwner(ctx, requestorID, groupID); err != nil {
			return err
		}
	}

	memberIDs, _ := s.groupMemberIDs(ctx, groupID)

	_, err = s.pool.Exec(ctx,
		`DELETE FROM group_members WHERE group_id = $1 AND user_id = $2`,
		groupID, targetID,
	)
	if err != nil {
		return err
	}

	s.hub.BroadcastToUsers(memberIDs, realtimeEvent("member.left", map[string]any{
		"group_id": groupID,
		"user_id":  targetID.String(),
	}))

	return nil
}

// ── Messages ──────────────────────────────────────────────────────────────────

func (s *Service) ListMessages(ctx context.Context, userID uuid.UUID, groupID string, limit int, before *time.Time) ([]MessageView, error) {
	if err := s.ensureGroupMembership(ctx, userID, groupID); err != nil {
		return nil, err
	}

	if limit <= 0 || limit > 200 {
		limit = 100
	}

	query := `
SELECT id::text,
       group_id,
       sender_user_id::text,
       message_type,
       COALESCE(body_ciphertext, ''),
       COALESCE(body_nonce, ''),
       COALESCE(body_tag, ''),
       COALESCE(quoted_ciphertext, ''),
       COALESCE(quoted_nonce, ''),
       COALESCE(quoted_tag, ''),
       reply_to_message_id::text,
       forwarded_from_message_id::text,
       forwarded_from_group_id,
       attachment_id::text,
       metadata,
       created_at,
       report_count
FROM group_messages
WHERE group_id = $1`

	args := []any{groupID}
	if before != nil {
		query += " AND created_at < $2"
		args = append(args, before.UTC())
	}
	query += fmt.Sprintf(" ORDER BY created_at DESC LIMIT %d", limit)

	rows, err := s.pool.Query(ctx, query, args...)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	out := make([]MessageView, 0, limit)
	for rows.Next() {
		var m MessageView
		var senderID, replyTo, fwdMsg, fwdGroup, attachID sql.NullString
		var metaRaw []byte

		if scanErr := rows.Scan(
			&m.ID, &m.GroupID,
			&senderID,
			&m.MessageType,
			&m.BodyCiphertext, &m.BodyNonce, &m.BodyTag,
			&m.QuotedCiphertext, &m.QuotedNonce, &m.QuotedTag,
			&replyTo, &fwdMsg, &fwdGroup, &attachID,
			&metaRaw,
			&m.CreatedAt, &m.ReportCount,
		); scanErr != nil {
			return nil, scanErr
		}

		m.SenderUserID = nullableString(senderID)
		m.ReplyToMessageID = nullableString(replyTo)
		m.ForwardedFromMessageID = nullableString(fwdMsg)
		m.ForwardedFromGroupID = nullableString(fwdGroup)
		m.AttachmentID = nullableString(attachID)
		m.Metadata = parseJSONMap(metaRaw)
		out = append(out, m)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}

	// Reverse to oldest→newest.
	for i, j := 0, len(out)-1; i < j; i, j = i+1, j-1 {
		out[i], out[j] = out[j], out[i]
	}

	reactions, err := s.loadMessageReactions(ctx, out)
	if err != nil {
		return nil, err
	}
	for i := range out {
		out[i].Reactions = reactions[out[i].ID]
	}

	return out, nil
}

func (s *Service) SendMessage(ctx context.Context, senderID uuid.UUID, groupID string, in SendMessageInput) (MessageView, error) {
	if err := s.ensureGroupMembership(ctx, senderID, groupID); err != nil {
		return MessageView{}, err
	}

	msgType := strings.TrimSpace(in.MessageType)
	switch msgType {
	case "text", "voice_note", "circular_video", "media", "file", "system", "ai_request":
	default:
		return MessageView{}, fmt.Errorf("%w: invalid message_type", ErrBadRequest)
	}

	if msgType == "text" && strings.TrimSpace(in.BodyCiphertext) == "" {
		return MessageView{}, fmt.Errorf("%w: body_ciphertext is required for text messages", ErrBadRequest)
	}

	if msgType == "ai_request" {
		// Plaintext must be provided in metadata.text
		txt, _ := in.Metadata["text"].(string)
		if strings.TrimSpace(txt) == "" {
			return MessageView{}, fmt.Errorf("%w: metadata.text is required for ai_request", ErrBadRequest)
		}
	}

	tx, err := s.pool.BeginTx(ctx, pgx.TxOptions{})
	if err != nil {
		return MessageView{}, err
	}
	defer func() {
		if err != nil {
			_ = tx.Rollback(ctx)
		}
	}()

	messageID := uuid.New()
	metadata := cloneMetadata(in.Metadata)
	metadataBytes, _ := json.Marshal(metadata)

	var replyToID, fwdMsgID *uuid.UUID
	var fwdGroupID *string

	if in.ReplyToMessageID != nil && *in.ReplyToMessageID != "" {
		parsed, parseErr := uuid.Parse(*in.ReplyToMessageID)
		if parseErr != nil {
			return MessageView{}, fmt.Errorf("%w: invalid reply_to_message_id", ErrBadRequest)
		}
		replyToID = &parsed
	}
	if in.ForwardedFromMessageID != nil && *in.ForwardedFromMessageID != "" {
		parsed, parseErr := uuid.Parse(*in.ForwardedFromMessageID)
		if parseErr != nil {
			return MessageView{}, fmt.Errorf("%w: invalid forwarded_from_message_id", ErrBadRequest)
		}
		fwdMsgID = &parsed
	}
	if in.ForwardedFromGroupID != nil && *in.ForwardedFromGroupID != "" {
		v := *in.ForwardedFromGroupID
		fwdGroupID = &v
	}

	var createdAt time.Time
	err = tx.QueryRow(ctx,
		`INSERT INTO group_messages (
		     id, group_id, sender_user_id, message_type,
		     body_ciphertext, body_nonce, body_tag,
		     quoted_ciphertext, quoted_nonce, quoted_tag,
		     reply_to_message_id, forwarded_from_message_id, forwarded_from_group_id,
		     metadata
		 ) VALUES (
		     $1, $2, $3, $4,
		     NULLIF($5,''), NULLIF($6,''), NULLIF($7,''),
		     NULLIF($8,''), NULLIF($9,''), NULLIF($10,''),
		     $11, $12, $13,
		     COALESCE($14::jsonb, '{}'::jsonb)
		 ) RETURNING created_at`,
		messageID, groupID, senderID, msgType,
		in.BodyCiphertext, in.BodyNonce, in.BodyTag,
		in.QuotedCiphertext, in.QuotedNonce, in.QuotedTag,
		replyToID, fwdMsgID, fwdGroupID,
		string(metadataBytes),
	).Scan(&createdAt)
	if err != nil {
		return MessageView{}, err
	}

	_, err = tx.Exec(ctx,
		`UPDATE group_chats SET updated_at = NOW() WHERE id = $1`,
		groupID,
	)
	if err != nil {
		return MessageView{}, err
	}

	_, err = tx.Exec(ctx,
		`UPDATE group_members
		 SET unread_count = CASE WHEN user_id = $2 THEN unread_count ELSE unread_count + 1 END
		 WHERE group_id = $1`,
		groupID, senderID,
	)
	if err != nil {
		return MessageView{}, err
	}

	if err = tx.Commit(ctx); err != nil {
		return MessageView{}, err
	}

	senderIDStr := senderID.String()
	result := MessageView{
		ID:                     messageID.String(),
		GroupID:                groupID,
		SenderUserID:           &senderIDStr,
		MessageType:            msgType,
		BodyCiphertext:         in.BodyCiphertext,
		BodyNonce:              in.BodyNonce,
		BodyTag:                in.BodyTag,
		QuotedCiphertext:       in.QuotedCiphertext,
		QuotedNonce:            in.QuotedNonce,
		QuotedTag:              in.QuotedTag,
		ReplyToMessageID:       in.ReplyToMessageID,
		ForwardedFromMessageID: in.ForwardedFromMessageID,
		ForwardedFromGroupID:   fwdGroupID,
		Metadata:               metadata,
		Reactions:              []MessageReactionView{},
		CreatedAt:              createdAt,
	}

	memberIDs, membersErr := s.groupMemberIDs(ctx, groupID)
	if membersErr == nil {
		s.hub.BroadcastToUsers(memberIDs, realtimeEvent("message.created", map[string]any{
			"message": result,
		}))
	}

	// Kick off async PulseAI handling when message_type == "ai_request".
	if msgType == "ai_request" {
		go s.handleAIRequest(context.Background(), groupID, in.Metadata, memberIDs)
	}

	return result, nil
}

// handleAIRequest calls PulseAI and persists the AI response as a new message.
func (s *Service) handleAIRequest(ctx context.Context, groupID string, metadata map[string]any, memberIDs []uuid.UUID) {
	text, _ := metadata["text"].(string)
	if strings.TrimSpace(text) == "" {
		return
	}

	// Broadcast "ai.thinking" so clients can show a spinner.
	s.hub.BroadcastToUsers(memberIDs, realtimeEvent("ai.thinking", map[string]any{
		"group_id": groupID,
	}))

	result, err := s.pulse.AskQuestion(ctx, groupID, text)
	if err != nil {
		// Deliver an error message back to the group.
		s.saveAIMessage(ctx, groupID, map[string]any{
			"ai_error": err.Error(),
			"ai_type":  "error",
		}, memberIDs)
		return
	}

	// Flatten the PulseAI result into the metadata of the ai_message.
	aiMeta := map[string]any{
		"ai_type": "response",
	}

	if content, ok := result["content"]; ok {
		switch v := content.(type) {
		case string:
			aiMeta["ai_content"] = v
		case map[string]any:
			// Task response: explanation + to_show actions
			if exp, ok := v["explanation"].(string); ok {
				aiMeta["ai_content"] = exp
			}
			if show, ok := v["to_show"]; ok {
				aiMeta["ai_actions"] = show
			}
		}
	}

	if buttons, ok := result["buttons"]; ok {
		aiMeta["ai_buttons"] = buttons
	}

	s.saveAIMessage(ctx, groupID, aiMeta, memberIDs)
}

// saveAIMessage persists an ai_message and broadcasts it to the group.
func (s *Service) saveAIMessage(ctx context.Context, groupID string, meta map[string]any, memberIDs []uuid.UUID) {
	messageID := uuid.New()
	metaBytes, _ := json.Marshal(meta)

	var createdAt time.Time
	err := s.pool.QueryRow(ctx,
		`INSERT INTO group_messages (id, group_id, sender_user_id, message_type, metadata)
		 VALUES ($1, $2, NULL, 'ai_message', COALESCE($3::jsonb, '{}'::jsonb))
		 RETURNING created_at`,
		messageID, groupID, string(metaBytes),
	).Scan(&createdAt)
	if err != nil {
		return
	}

	_, _ = s.pool.Exec(ctx,
		`UPDATE group_chats SET updated_at = NOW() WHERE id = $1`, groupID,
	)
	_, _ = s.pool.Exec(ctx,
		`UPDATE group_members SET unread_count = unread_count + 1 WHERE group_id = $1`, groupID,
	)

	msg := MessageView{
		ID:          messageID.String(),
		GroupID:     groupID,
		MessageType: "ai_message",
		Metadata:    meta,
		Reactions:   []MessageReactionView{},
		CreatedAt:   createdAt,
	}

	s.hub.BroadcastToUsers(memberIDs, realtimeEvent("message.created", map[string]any{
		"message": msg,
	}))
}

// ── Reactions ─────────────────────────────────────────────────────────────────

func (s *Service) AddReaction(ctx context.Context, userID uuid.UUID, groupID, messageIDStr, emoji string) error {
	if err := s.ensureGroupMembership(ctx, userID, groupID); err != nil {
		return err
	}

	emoji = strings.TrimSpace(emoji)
	if emoji == "" {
		return fmt.Errorf("%w: emoji is required", ErrBadRequest)
	}

	messageID, err := uuid.Parse(messageIDStr)
	if err != nil {
		return fmt.Errorf("%w: invalid message_id", ErrBadRequest)
	}

	_, err = s.pool.Exec(ctx,
		`INSERT INTO group_message_reactions (message_id, emoji, user_id)
		 VALUES ($1, $2, $3)
		 ON CONFLICT (message_id, emoji, user_id) DO NOTHING`,
		messageID, emoji, userID,
	)
	if err != nil {
		return err
	}

	memberIDs, _ := s.groupMemberIDs(ctx, groupID)
	s.hub.BroadcastToUsers(memberIDs, realtimeEvent("reaction.updated", map[string]any{
		"group_id":   groupID,
		"message_id": messageIDStr,
		"emoji":      emoji,
		"user_id":    userID.String(),
		"action":     "add",
	}))

	return nil
}

func (s *Service) RemoveReaction(ctx context.Context, userID uuid.UUID, groupID, messageIDStr, emoji string) error {
	if err := s.ensureGroupMembership(ctx, userID, groupID); err != nil {
		return err
	}

	messageID, err := uuid.Parse(messageIDStr)
	if err != nil {
		return fmt.Errorf("%w: invalid message_id", ErrBadRequest)
	}

	_, err = s.pool.Exec(ctx,
		`DELETE FROM group_message_reactions WHERE message_id = $1 AND emoji = $2 AND user_id = $3`,
		messageID, strings.TrimSpace(emoji), userID,
	)
	if err != nil {
		return err
	}

	memberIDs, _ := s.groupMemberIDs(ctx, groupID)
	s.hub.BroadcastToUsers(memberIDs, realtimeEvent("reaction.updated", map[string]any{
		"group_id":   groupID,
		"message_id": messageIDStr,
		"emoji":      emoji,
		"user_id":    userID.String(),
		"action":     "remove",
	}))

	return nil
}

func (s *Service) loadMessageReactions(ctx context.Context, messages []MessageView) (map[string][]MessageReactionView, error) {
	reactions := make(map[string][]MessageReactionView, len(messages))
	if len(messages) == 0 {
		return reactions, nil
	}

	ids := make([]uuid.UUID, 0, len(messages))
	for _, m := range messages {
		id, err := uuid.Parse(m.ID)
		if err == nil {
			ids = append(ids, id)
		}
	}
	if len(ids) == 0 {
		return reactions, nil
	}

	rows, err := s.pool.Query(ctx,
		`SELECT message_id::text, emoji, ARRAY_AGG(user_id::text ORDER BY created_at ASC) AS user_ids
		 FROM group_message_reactions
		 WHERE message_id = ANY($1)
		 GROUP BY message_id, emoji
		 ORDER BY message_id, emoji`,
		ids,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var msgID, emoji string
		var userIDs []string
		if err := rows.Scan(&msgID, &emoji, &userIDs); err != nil {
			return nil, err
		}
		reactions[msgID] = append(reactions[msgID], MessageReactionView{Emoji: emoji, UserIDs: userIDs})
	}
	return reactions, rows.Err()
}

// ── Mark read ─────────────────────────────────────────────────────────────────

func (s *Service) MarkRead(ctx context.Context, userID uuid.UUID, groupID string, in MarkReadInput) error {
	if err := s.ensureGroupMembership(ctx, userID, groupID); err != nil {
		return err
	}

	if in.LastReadMessageID != nil && *in.LastReadMessageID != "" {
		msgID, err := uuid.Parse(*in.LastReadMessageID)
		if err != nil {
			return fmt.Errorf("%w: invalid last_read_message_id", ErrBadRequest)
		}

		var exists bool
		if err := s.pool.QueryRow(ctx,
			`SELECT EXISTS (SELECT 1 FROM group_messages WHERE id = $1 AND group_id = $2)`,
			msgID, groupID,
		).Scan(&exists); err != nil {
			return err
		}
		if !exists {
			return fmt.Errorf("%w: message not in this group", ErrBadRequest)
		}

		_, err = s.pool.Exec(ctx,
			`UPDATE group_members SET unread_count = 0, last_read_message_id = $3
			 WHERE group_id = $1 AND user_id = $2`,
			groupID, userID, msgID,
		)
		return err
	}

	_, err := s.pool.Exec(ctx,
		`UPDATE group_members SET unread_count = 0 WHERE group_id = $1 AND user_id = $2`,
		groupID, userID,
	)
	return err
}

// ── Report ────────────────────────────────────────────────────────────────────

func (s *Service) ReportMessage(ctx context.Context, userID uuid.UUID, groupID, messageIDStr string, in ReportInput) error {
	if err := s.ensureGroupMembership(ctx, userID, groupID); err != nil {
		return err
	}

	reason := strings.TrimSpace(in.Reason)
	validReasons := map[string]bool{"spam": true, "insult": true, "virus": true, "scam": true, "other": true}
	if !validReasons[reason] {
		return fmt.Errorf("%w: reason must be one of: spam, insult, virus, scam, other", ErrBadRequest)
	}

	messageID, err := uuid.Parse(messageIDStr)
	if err != nil {
		return fmt.Errorf("%w: invalid message_id", ErrBadRequest)
	}

	// Increment report count on the message.
	_, err = s.pool.Exec(ctx,
		`UPDATE group_messages SET report_count = report_count + 1 WHERE id = $1 AND group_id = $2`,
		messageID, groupID,
	)
	return err
}
