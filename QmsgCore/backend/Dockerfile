FROM golang:1.24-alpine AS builder
WORKDIR /src

COPY go.mod go.sum ./
RUN go mod download

COPY cmd ./cmd
COPY internal ./internal
COPY migrations ./migrations

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -ldflags='-s -w' -o /out/groupchat-server ./cmd/server

FROM alpine:3.21
WORKDIR /app

RUN addgroup -S groupchat && adduser -S groupchat -G groupchat

COPY --from=builder /out/groupchat-server /app/groupchat-server
COPY migrations /app/migrations

RUN chown -R groupchat:groupchat /app

USER groupchat
EXPOSE 8090

CMD ["/app/groupchat-server"]
