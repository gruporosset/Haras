FROM node:24
WORKDIR /app

COPY package*.json ./
COPY quasar.config.js ./

RUN npm install -g @quasar/cli && \
    npm install

COPY . .

EXPOSE 9000
CMD ["quasar", "dev"]