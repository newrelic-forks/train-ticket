FROM golang:1.19-alpine AS builder

# Install git (required for go mod download)
RUN apk add --no-cache git

RUN mkdir -p /app
WORKDIR /app

# Copy existing go.mod and go.sum (they're working now)
COPY go.mod go.sum* ./
RUN go mod download

# Copy source code
ADD ./src/main/main.go ./

# Build the application
RUN go build -o app main.go

# Runtime stage
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/

COPY --from=builder /app/app .
CMD ["./app"]

EXPOSE 12862