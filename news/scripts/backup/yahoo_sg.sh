uuids=`curl --globoff --request \
GET "https://sg.news.yahoo.com/fp_ms/_rcv/remote?ctrl=StreamGrid&lang=en-SG&m_id=react-wafer-stream&m_mode=json&region=SG&rid=05tvio9j77jvq&partner=none&site=news" \
--header "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36" \
| sed 's/ /\n/g' | grep "data-uuid" | sed 's/data-uuid=//g' | sed 's/\\\"//g' | sort | uniq | tr '\n' ','`
echo $uuids
curl --globoff --request GET "https://sg.news.yahoo.com/caas/content/article/?uuid=$uuids" \
--header "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36" \
-o ./news/data/yahoo/yahoo_sg.json