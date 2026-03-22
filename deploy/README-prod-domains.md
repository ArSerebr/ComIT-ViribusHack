# Деплой: домены и HTTPS

## DNS (robofirst.ru)

| Запись | Тип | Значение |
|--------|-----|---------|
| `comit` | A | IP сервера |
| `api.comit` | A | тот же IP |
| `admin.comit` | A | тот же IP |
| `analytics.comit` | A | тот же IP |

## Firewall

```bash
sudo ufw allow 22/tcp && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw enable
```

Порты `8000/8080/8010/8081` не нужно открывать наружу — трафик идёт через nginx.

## Let's Encrypt

```bash
sudo certbot --nginx \
  -d comit.robofirst.ru \
  -d api.comit.robofirst.ru \
  -d admin.comit.robofirst.ru \
  -d analytics.comit.robofirst.ru
```

## Nginx

```bash
sudo cp deploy/nginx-comit.conf /etc/nginx/sites-available/comit
sudo ln -sf /etc/nginx/sites-available/comit /etc/nginx/sites-enabled/comit
sudo nginx -t && sudo systemctl reload nginx
```

## Ключевые переменные .env на сервере

```env
VITE_API_BASE_URL=https://api.comit.robofirst.ru   # задать ДО docker compose build
DJANGO_ALLOWED_HOSTS=admin.comit.robofirst.ru,127.0.0.1
```

> `VITE_API_BASE_URL` вшивается в сборку — после смены нужен ребилд образа `frontend`.

## Чеклист после деплоя

1. `docker compose ps` — все контейнеры `Up`
2. `curl -s http://127.0.0.1:8000/health` — backend отвечает
3. `curl -s https://api.comit.robofirst.ru/health` — nginx проксирует
4. Открыть `https://comit.robofirst.ru` и проверить запросы в DevTools → Network
