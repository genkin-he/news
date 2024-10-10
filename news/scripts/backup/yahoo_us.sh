uuids=`curl --globoff --request \
GET "https://news.yahoo.com/fp_ms/_rcv/remote?ctrl=StreamGrid&lang=en-US&m_id=react-wafer-stream&m_mode=json&region=US&rid=4c18971j77t3g&partner=none&site=news" \
--header "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36" \
| sed 's/ /\n/g' | grep "data-uuid" | sed 's/data-uuid=//g' | sed 's/\\\"//g' | sort | uniq | tr '\n' ','`
echo $uuids
curl --globoff --request GET "https://news.yahoo.com/caas/content/article/?uuid=$uuids&appid=news_web&device=desktop&lang=en-US&region=US&site=news&partner=none&bucket=news-dweb-nca-blog-test-2,seamless&features=enableEVPlayer,contentFeedbackEnabled,enableAdFeedbackV2,enableInArticleAd,enableOpinionLabel,enableSingleSlotting,enableVideoDocking,outStream,showCommentsIconWithDynamicCount,enableStickyAds,showCommentsIconInShareSec,enableInlineConsent,enableAdSlotsNewMap,enableGAMAds,enableGAMAdsOnLoad,enableFinancePremiumTicker,enableAdLiteUpSellFeedback,enableRRAtTop,enableCommentsCountInViewCommentsCta,enableRRAdsSlots,enableRRAdsSlotsWithJAC,newsModal,enableViewCommentsCTA&rid=2ndsttpj77ta5" \
--header "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36" \
-o ./news/data/yahoo/yahoo_us.json