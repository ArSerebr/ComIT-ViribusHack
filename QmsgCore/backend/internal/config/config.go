package config

import (
	"errors"
	"os"
	"strconv"
	"time"
)

type Config struct {
	Env      string
	Server   ServerConfig
	Database DatabaseConfig
	Security SecurityConfig
	Pulse    PulseConfig
}

type ServerConfig struct {
	Host string
	Port int
}

type DatabaseConfig struct {
	DSN string
}

type SecurityConfig struct {
	JWTSecret      string
	JWTIssuer      string
	AccessTokenTTL time.Duration
}

// PulseConfig holds PulseAI backend settings.
type PulseConfig struct {
	BaseURL string
	// Timeout for polling a single task, seconds.
	TaskTimeoutSec int
}

func Load() (Config, error) {
	cfg := Config{}
	cfg.Env = getEnv("GC_ENV", "development")
	cfg.Server.Host = getEnv("GC_SERVER_HOST", "0.0.0.0")
	cfg.Server.Port = getEnvAsInt("GC_SERVER_PORT", 8090)

	cfg.Database.DSN = os.Getenv("GC_DATABASE_DSN")
	if cfg.Database.DSN == "" {
		return Config{}, errors.New("GC_DATABASE_DSN is required")
	}

	cfg.Security.JWTSecret = os.Getenv("GC_JWT_SECRET")
	if cfg.Security.JWTSecret == "" {
		return Config{}, errors.New("GC_JWT_SECRET is required (must match QGramm backend secret)")
	}
	cfg.Security.JWTIssuer = getEnv("GC_JWT_ISSUER", "qgramm-backend")
	cfg.Security.AccessTokenTTL = time.Duration(getEnvAsInt("GC_ACCESS_TOKEN_TTL_HOURS", 168)) * time.Hour

	cfg.Pulse.BaseURL = getEnv("GC_PULSE_BASE_URL", "http://chat.droidje-cloud.ru")
	cfg.Pulse.TaskTimeoutSec = getEnvAsInt("GC_PULSE_TASK_TIMEOUT_SEC", 120)

	return cfg, nil
}

func getEnv(key, defaultValue string) string {
	if value, ok := os.LookupEnv(key); ok {
		return value
	}
	return defaultValue
}

func getEnvAsInt(key string, defaultValue int) int {
	v := os.Getenv(key)
	if v == "" {
		return defaultValue
	}
	n, err := strconv.Atoi(v)
	if err != nil {
		return defaultValue
	}
	return n
}
