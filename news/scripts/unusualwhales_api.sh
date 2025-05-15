#!/bin/bash
trap 'echo "$(date +%Y-%m-%d\ %H:%M:%S) - Error unusualwhales_api: $?"' ERR

log() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ${message}"
}

log "Starting request to Unusual Whales API..."

curl --connect-timeout 10 -m 20 --globoff --request GET "https://api.unusualwhales.com/market_news/api/free_news?page=0" --header \
"User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36" \
| python3 -m json.tool > ./news/data/unusualwhales_api.json

log "Unusual Whales Request completed."
