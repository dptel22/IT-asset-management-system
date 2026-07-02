FROM node:22-bookworm-slim AS dependencies
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force

FROM node:22-bookworm-slim AS runtime
ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000 \
    DB_PATH=/data/database.sqlite
WORKDIR /app
RUN groupadd --system --gid 10001 cognix \
    && useradd --system --uid 10001 --gid cognix --home-dir /app cognix \
    && mkdir -p /data \
    && chown cognix:cognix /data
COPY --from=dependencies --chown=cognix:cognix /app/node_modules ./node_modules
COPY --chown=cognix:cognix package.json server.js db.js ./
COPY --chown=cognix:cognix templates ./templates
COPY --chown=cognix:cognix static ./static
USER cognix
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD node -e "fetch('http://127.0.0.1:3000/api/health').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))"
CMD ["node", "server.js"]
