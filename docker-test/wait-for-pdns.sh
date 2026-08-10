#!/bin/sh

set -e

LOOPS=10
until curl -H "X-API-Key: ${PDNS_API_KEY}" "${PDNS_PROTO}://${PDNS_HOST}:${PDNS_PORT}/api/v1/servers"; do
  >&2 echo "PDNS is unavailable - sleeping"
  sleep 1
  if [ "${LOOPS}" -eq 10 ]
  then
    break
  fi
done

sleep 5

>&2 echo "PDNS is up - executing command"
exec "$@"

