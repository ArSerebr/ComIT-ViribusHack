package services

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// PulseClient interacts with the PulseAI backend.
type PulseClient struct {
	baseURL    string
	timeoutSec int
	http       *http.Client
}

func NewPulseClient(baseURL string, timeoutSec int) *PulseClient {
	return &PulseClient{
		baseURL:    baseURL,
		timeoutSec: timeoutSec,
		http:       &http.Client{Timeout: 30 * time.Second},
	}
}

type pulseTaskResponse struct {
	TaskID string `json:"task_id"`
}

type pulseTaskStatus struct {
	TaskID string         `json:"task_id"`
	Status string         `json:"status"`
	Result map[string]any `json:"result"`
}

// AskQuestion sends a plaintext message to PulseAI and blocks until the task
// is READY or FAILED (or the context deadline is exceeded).
// uid identifies the conversation session on the PulseAI side; use the group ID.
func (p *PulseClient) AskQuestion(ctx context.Context, uid, text string) (map[string]any, error) {
	taskID, err := p.submitChat(ctx, uid, text)
	if err != nil {
		return nil, fmt.Errorf("pulse submit: %w", err)
	}

	deadline := time.Now().Add(time.Duration(p.timeoutSec) * time.Second)
	for time.Now().Before(deadline) {
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		case <-time.After(1 * time.Second):
		}

		status, pollErr := p.pollTask(ctx, taskID)
		if pollErr != nil {
			return nil, fmt.Errorf("pulse poll: %w", pollErr)
		}

		switch status.Status {
		case "READY":
			return status.Result, nil
		case "FAILED":
			if status.Result != nil {
				if errMsg, ok := status.Result["error"].(string); ok {
					return nil, fmt.Errorf("pulse task failed: %s", errMsg)
				}
			}
			return nil, fmt.Errorf("pulse task failed")
		}
		// PENDING — keep polling
	}

	return nil, fmt.Errorf("pulse task timeout after %d seconds", p.timeoutSec)
}

func (p *PulseClient) submitChat(ctx context.Context, uid, text string) (string, error) {
	body, _ := json.Marshal(map[string]string{"message": text})
	url := fmt.Sprintf("%s/api/comit/chat?uid=%s", p.baseURL, uid)

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := p.http.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		raw, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("pulse chat returned HTTP %d: %s", resp.StatusCode, string(raw))
	}

	var result pulseTaskResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", fmt.Errorf("decode pulse chat response: %w", err)
	}
	if result.TaskID == "" {
		return "", fmt.Errorf("pulse returned empty task_id")
	}

	return result.TaskID, nil
}

func (p *PulseClient) pollTask(ctx context.Context, taskID string) (pulseTaskStatus, error) {
	url := fmt.Sprintf("%s/api/task/%s", p.baseURL, taskID)

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return pulseTaskStatus{}, err
	}

	resp, err := p.http.Do(req)
	if err != nil {
		return pulseTaskStatus{}, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		raw, _ := io.ReadAll(resp.Body)
		return pulseTaskStatus{}, fmt.Errorf("pulse task poll HTTP %d: %s", resp.StatusCode, string(raw))
	}

	var status pulseTaskStatus
	if err := json.NewDecoder(resp.Body).Decode(&status); err != nil {
		return pulseTaskStatus{}, fmt.Errorf("decode pulse task: %w", err)
	}

	return status, nil
}
