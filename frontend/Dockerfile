# Build stage
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production — static files via nginx (upstream из переменных окружения)
FROM nginx:1.27-alpine

RUN apk add --no-cache gettext

COPY nginx/templates/default.conf.template /etc/nginx/templates/default.conf.template
COPY docker-entrypoint.sh /docker-entrypoint.sh
# Windows CRLF в репо ломает shebang в Alpine → «no such file or directory»
RUN sed -i 's/\r$//' /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

COPY --from=build /app/dist /usr/share/nginx/html
COPY --from=build /app/img /usr/share/nginx/html/img

EXPOSE 80

ENTRYPOINT ["/docker-entrypoint.sh"]
