# Stage 1: build the static bundle with Node
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY index.html vite.config.js ./
COPY src ./src
RUN npm run build

# Stage 2: serve it with nginx, running as the unprivileged nginx image's user
FROM nginxinc/nginx-unprivileged:1.29-alpine
# pull in the base image's security updates (Trivy flagged openssl and c-ares in the older tag)
USER root
RUN apk upgrade --no-cache
USER 101
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
