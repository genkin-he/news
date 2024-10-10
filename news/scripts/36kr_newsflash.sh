#!/bin/bash
trap 'echo "Error 36kr_newsflash: "' ERR
curl --globoff --request POST "https://gateway.36kr.com/api/mis/nav/newsflash/list" --header \
"User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36" \
--header "Content-Type: application/json" \
--data '{
"partner_id": "web",
"param": {
    "pageSize": 20,
    "pageEvent": 0,
    "siteId": 1,
    "type": 0,
    "platformId": 2
}
}' -o \
./news/data/36kr_newsflash.json