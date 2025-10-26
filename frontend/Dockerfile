FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --no-audit --no-fund
COPY . .
EXPOSE 5173
ENV HOST=0.0.0.0
CMD ["npm","run","dev"]
