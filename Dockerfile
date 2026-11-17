# ── Build Stage ──
FROM golang:1.21-bookworm AS builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y git make gcc g++

# Clone Sliver and build the server binary
RUN git clone --depth 1 https://github.com/BishopFox/sliver.git .
RUN make

# ── Runtime Stage ──
FROM debian:bookworm-slim
WORKDIR /app

# Install runtime dependencies (certificates, sqlite)
RUN apt-get update && apt-get install -y ca-certificates sqlite3 && rm -rf /var/lib/apt/lists/*

# Copy the compiled binary from builder
COPY --from=builder /app/sliver-server /usr/local/bin/sliver-server
RUN chmod +x /usr/local/bin/sliver-server

# Create data directory
RUN mkdir -p /root/.sliver

# Sliver uses 31337 for gRPC (Bridge) and 8888 for mTLS (Agents)
EXPOSE 31337
EXPOSE 8888

# Start the daemon
ENTRYPOINT ["/usr/local/bin/sliver-server", "daemon"]
