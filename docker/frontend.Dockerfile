# Stage 1: Build React SPA
FROM node:20-alpine AS builder

WORKDIR /app

COPY application/frontend/package*.json ./
RUN npm ci --no-audit --no-fund

COPY application/frontend/ ./
RUN npm run build

# Stage 2: Serve with non-root Nginx
FROM nginx:1.27-alpine AS runtime

RUN rm -f /etc/nginx/conf.d/default.conf \
    && chown -R nginx:nginx /var/cache/nginx /var/log/nginx /etc/nginx/conf.d \
    && touch /var/run/nginx.pid \
    && chown nginx:nginx /var/run/nginx.pid

COPY application/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder --chown=nginx:nginx /app/dist /usr/share/nginx/html

USER nginx

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:8080/nginx-health || exit 1

CMD ["nginx", "-g", "daemon off;"]
