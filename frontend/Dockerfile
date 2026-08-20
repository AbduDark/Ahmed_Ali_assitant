# Frontend Dockerfile
# Multi-stage build

# ── Development Stage ────────────────────────────────────────
FROM node:20-alpine AS development

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ── Build Stage ──────────────────────────────────────────────
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

# ── Production Stage ─────────────────────────────────────────
FROM nginx:alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
