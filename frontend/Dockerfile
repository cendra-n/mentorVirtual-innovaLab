# ── Build de producción (multi-stage) ────────
FROM node:22-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# La imagen final solo tiene el dist/
# Nginx lo sirve directamente via volumen,
# pero podés usar esta imagen si preferís
FROM nginx:1.27-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
