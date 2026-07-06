FROM golang:1.22-alpine
WORKDIR /sandbox
RUN adduser -D -u 10001 runner
USER runner
CMD ["go", "version"]
