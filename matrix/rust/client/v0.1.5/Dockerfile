FROM rust:1.75-slim

WORKDIR /app

# Copy template files first (these will be overwritten by version-specific files if they exist)
COPY matrix/templates/rust/client /app

# Copy version-specific files (these will overwrite templates if needed)
COPY matrix/rust/client/v0.1.5 /app

# Build the project
RUN cargo build --release

# Set environment variables
ENV PORT=8000

# Command to run the client
CMD ["cargo", "run", "--example", "basic_client"] 