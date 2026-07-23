FROM node:22-slim
WORKDIR /sandbox
RUN useradd -m -u 10001 runner
USER runner
ENV NODE_ENV=production
CMD ["node", "--version"]
