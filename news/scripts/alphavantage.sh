#!/bin/bash
set -e
trap 'echo "Error alphavantage: $?"' ERR

API_KEY="S8EX215RF6G6Q03Y"
URL="https://www.alphavantage.co/query"
PARAMS="apikey=${API_KEY}&function=NEWS_SENTIMENT"
USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
OUTPUT_FILE="./news/data/alphavantage.json"

log() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ${message}"
}

log "Starting request to Alpha Vantage API..."

curl --connect-timeout 10 -m 20  --globoff --request GET "${URL}?${PARAMS}" --header "User-Agent: ${USER_AGENT}" | python3 -m json.tool > "${OUTPUT_FILE}"

log "Alpha Vantage Request completed."
