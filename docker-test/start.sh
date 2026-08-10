#!/usr/bin/env sh

if [ -z "${PDNS_API_KEY:-}" ]; then
    PDNS_API_KEY="changeme"
fi

if [ -z "${PDNS_PORT:-}" ]; then
    PDNS_PORT="8081"
fi

# Import schema structure
if [ -e "/data/pdns.sql" ]; then
    rm -f /data/pdns.db
    sqlite3 /data/pdns.db < /data/pdns.sql
    rm -f /data/pdns.sql
    echo "Imported schema structure"
fi

chown -R pdns:pdns /data/

/usr/sbin/pdns_server \
    --launch=gsqlite3 --gsqlite3-database=/data/pdns.db \
    --webserver=yes --webserver-address=0.0.0.0 --webserver-port="${PDNS_PORT}" \
    --api=yes --api-key="${PDNS_API_KEY}" --webserver-allow-from="${PDNS_WEBSERVER_ALLOW_FROM}"

