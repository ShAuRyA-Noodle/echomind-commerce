# Echomind Commerce - Frontend (Next.js dev mode)
FROM node:26-alpine

# libc compat for some Next.js native deps
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Install deps first for cache reuse
COPY package*.json ./
RUN npm ci

# Copy app source
COPY . .

EXPOSE 3000

# Dev mode - hot reload via mounted volume in docker-compose.
# For production, build a separate Dockerfile.prod that runs `npm run build && npm start`.
CMD ["npm", "run", "dev"]
