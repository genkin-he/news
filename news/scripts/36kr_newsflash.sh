#!/bin/bash
set -e

output_file="./news/data/36kr_newsflash.json"
url="https://gateway.36kr.com/api/mis/nav/newsflash/list"
user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
content_type="application/json"
data='{
"partner_id": "web",
"param": {
    "pageSize": 20,
    "pageEvent": 0,
    "siteId": 1,
    "type": 0,
    "platformId": 2
}
}'
trap 'echo "$(date +%Y-%m-%d\ %H:%M:%S) - Error 36kr_newsflash: $?"' ERR

log() {
    local message="$1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ${message}"
}

log "Starting request to 36kr API..."

curl --connect-timeout 10 -m 20 --globoff --request POST "$url" \
     --header "User-Agent: $user_agent" \
     --header "Content-Type: $content_type" \
     --data "$data" \
    | python3 -m json.tool > "$output_file"

log "36kr Request completed."