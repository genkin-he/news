# -*- coding: UTF-8 -*-
from util.spider_util import SpiderUtil
from util.bing_news import collect

util = SpiderUtil()


def run():
    collect(
        util,
        site="theedgesingapore.com",
        link_prefix="https://www.theedgesingapore.com/",
        source="theedgesingapore",
        filename="./news/data/theedgesingapore/list.json",
    )


if __name__ == "__main__":
    util.execute_with_timeout(run)
