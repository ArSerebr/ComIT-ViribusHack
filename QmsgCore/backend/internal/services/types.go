package services

import "time"

// ── Group views ──────────────────────────────────────────────────────────────

type GroupView struct {
	ID           string    `json:"id"`
	Name         string    `json:"name"`
	AvatarURL    string    `json:"avatar_url,omitempty"`
	CreatedByID  string    `json:"created_by_user_id"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
	MemberIDs    []string  `json:"member_ids"`
	UnreadCount  int       `json:"unread_count"`
}

type GroupMemberView struct {
	UserID   string    `json:"user_id"`
	Role     string    `json:"role"`
	JoinedAt time.Time `json:"joined_at"`
}

// ── Message views ─────────────────────────────────────────────────────────────

type MessageView struct {
	ID                      string                `json:"id"`
	GroupID                 string                `json:"group_id"`
	SenderUserID            *string               `json:"sender_user_id,omitempty"`
	MessageType             string                `json:"message_type"`
	BodyCiphertext          string                `json:"body_ciphertext,omitempty"`
	BodyNonce               string                `json:"body_nonce,omitempty"`
	BodyTag                 string                `json:"body_tag,omitempty"`
	QuotedCiphertext        string                `json:"quoted_ciphertext,omitempty"`
	QuotedNonce             string                `json:"quoted_nonce,omitempty"`
	QuotedTag               string                `json:"quoted_tag,omitempty"`
	ReplyToMessageID        *string               `json:"reply_to_message_id,omitempty"`
	ForwardedFromMessageID  *string               `json:"forwarded_from_message_id,omitempty"`
	ForwardedFromGroupID    *string               `json:"forwarded_from_group_id,omitempty"`
	AttachmentID            *string               `json:"attachment_id,omitempty"`
	Metadata                map[string]any        `json:"metadata,omitempty"`
	Reactions               []MessageReactionView `json:"reactions,omitempty"`
	CreatedAt               time.Time             `json:"created_at"`
	ReportCount             int                   `json:"report_count"`
}

type MessageReactionView struct {
	Emoji   string   `json:"emoji"`
	UserIDs []string `json:"user_ids"`
}

// ── Input types ───────────────────────────────────────────────────────────────

type CreateGroupInput struct {
	Name string `json:"name"`
}

type UpdateGroupInput struct {
	Name      string `json:"name"`
	AvatarURL string `json:"avatar_url"`
}

type AddMemberInput struct {
	UserID string `json:"user_id"`
}

type SendMessageInput struct {
	MessageType             string         `json:"message_type"`
	BodyCiphertext          string         `json:"body_ciphertext"`
	BodyNonce               string         `json:"body_nonce"`
	BodyTag                 string         `json:"body_tag"`
	QuotedCiphertext        string         `json:"quoted_ciphertext"`
	QuotedNonce             string         `json:"quoted_nonce"`
	QuotedTag               string         `json:"quoted_tag"`
	ReplyToMessageID        *string        `json:"reply_to_message_id"`
	ForwardedFromMessageID  *string        `json:"forwarded_from_message_id"`
	ForwardedFromGroupID    *string        `json:"forwarded_from_group_id"`
	AttachmentID            *string        `json:"attachment_id"`
	Metadata                map[string]any `json:"metadata"`
}

type ReportInput struct {
	Reason string `json:"reason"`
	Note   string `json:"note"`
}

type MarkReadInput struct {
	LastReadMessageID *string `json:"last_read_message_id"`
}
