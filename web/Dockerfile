FROM node:22-alpine

WORKDIR /app

# Copy dependency files first
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Tell Nuxt to bind to all network interfaces so Windows can see it
ENV HOST=0.0.0.0
ENV PORT=3000
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

# Expose Nuxt's web port and Vite's HMR (Hot Reloading) port
EXPOSE 3000
EXPOSE 24678

CMD ["npm", "run", "dev"]