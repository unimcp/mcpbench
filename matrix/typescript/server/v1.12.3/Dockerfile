FROM node:20-slim

WORKDIR /app

# Copy template files first (these will be overwritten by version-specific files if they exist)
COPY matrix/templates/typescript/server /app

# Copy version-specific files (these will overwrite templates if needed)
COPY matrix/typescript/server/v1.12.3 /app

# Install dependencies
RUN npm install

# Set environment variables
ENV NODE_ENV=development
ENV PORT=8000

# Expose the port
EXPOSE 8000

# Command to run the server
CMD ["npm", "run", "start:server"] 