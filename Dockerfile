FROM nginx:1.27-alpine

LABEL org.opencontainers.image.title="Quellberg Invoice Review" \
      org.opencontainers.image.description="Browser invoice review agent served by nginx" \
      org.opencontainers.image.source="https://github.com/Shyam-Gupta-Chiliveri/invoice-review-agent"

COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
COPY vendor /usr/share/nginx/html/vendor
COPY data /usr/share/nginx/html/data

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=5 \
    CMD wget -q -O /dev/null http://127.0.0.1/healthz || exit 1
