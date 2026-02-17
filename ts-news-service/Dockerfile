FROM golang:1.19-alpine AS builder

RUN mkdir -p /app
WORKDIR /app

# Copy go mod files
COPY go.mod go.sum* ./
RUN go mod download

# Copy source code
ADD ./src/main/main.go ./
RUN go build -o app main.go

# Runtime stage
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/

COPY --from=builder /app/app .
CMD ["./app"]

EXPOSE 12862