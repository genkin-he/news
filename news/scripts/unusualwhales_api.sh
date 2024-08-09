#!/bin/bash
trap 'echo "Error unusualwhales_api: "' ERR

curl --globoff --request GET "https://api.unusualwhales.com/market_news/api/free_news?page=0" --header \
"User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36" -o \
./news/data/unusualwhales_api.json
