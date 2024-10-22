curl --globoff --request \
GET "https://finance.yahoo.com/topic/latest-news/?guccounter=1" --header \
"User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36" -o \
./news/data/yahoo.html