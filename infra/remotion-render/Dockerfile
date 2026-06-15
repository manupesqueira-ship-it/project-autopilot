FROM node:20-bookworm-slim

RUN apt-get update && apt-get install -y \
    chromium \
    libnss3 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    libgbm1 \
    ffmpeg \
    fonts-liberation \
    fonts-noto-core \
    fonts-noto-color-emoji \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV REMOTION_CHROME_EXECUTABLE=/usr/bin/chromium

WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev

COPY . .

EXPOSE 3000
CMD ["node", "server.js"]
