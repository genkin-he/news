import unittest
import json
import os
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, mock_open, MagicMock

# 导入要测试的模块
from news.scripts.util.spider_util import SpiderUtil


class TestSpiderUtil(unittest.TestCase):

    def setUp(self):
        """每个测试方法执行前的设置"""
        self.spider_util = SpiderUtil(notify=False)
        # 创建临时目录用于测试
        os.makedirs("./tmp", exist_ok=True)

    def tearDown(self):
        """每个测试方法执行后的清理"""
        # 如果创建了临时文件，可以在这里删除
        if os.path.exists("./tmp/action_errors.log"):
            with open("./tmp/action_errors.log", "w") as file:
                file.write("")

    def test_fix_text(self):
        """测试 fix_text 方法，确保它能正确修复编码问题"""
        # 测试单引号
        text1 = """
<p>The S&amp;P 500<a href="https://www.tipranks.com/index/spx"> (SPX),</a> the worldâs leading index comprising the biggest 500 traded companies, is now lagging. In one of its worst weeks in decades, <a href="https://www.tipranks.com/news/sp-500-plunges-alongside-trade-war-worries">the index dropped 3.1%, erasing over $3 trillion</a> in value since its February peak. Meanwhile, global markets have performed better, which might be signaling a shift in investor confidence. The U.S. share of global market capitalization has also fallen below 50%, marking a decline in dominance.</p>
<p>Several factors are driving this downturn. The U.S. economy shows signs of weakness, with declining home sales, rising unemployment claims, and slowing consumer spending. These concerns have created a solid infrastructure for investors&#8217; hesitance, leading to market pullback. Nevertheless, the overall reaction to President Trump&#8217;s ongoing trade wars has had an adverse effect on the market and is considered a primary catalyst to the index&#8217;s recent slump. </p>
<h2 class="wp-block-heading"><strong>Tariffs Uncertainty and Tech Stocks Decline</strong></h2>
<p>Trade policy uncertainty has added to the pressure. <a href="https://www.tipranks.com/news/wall-street-braces-for-impact-as-canada-hits-back-with-25-tariffs-on-us-goods">President Trumpâs tariffs, including a 25% tariff on Canadian and Mexican goods</a> that has now been delayed to April, have clearly unsettled markets. Also, the ongoing trade tensions with China and threats of further tariffs on other nations have only worsened investor sentiment. With global trade facing potential disruptions, companies that rely on international markets could suffer, further weighing on stock performance.</p>
<p>amounted to roughly $854 billion. The technology sector, a major driver of the S&amp;P 500, has been hit hard. Giants like Nvidia <a data-ticker="NVDA" href="https://www.tipranks.com/stocks/nvda">(NVDA)</a> and Tesla <a data-ticker="TSLA" href="https://www.tipranks.com/stocks/tsla">(TSLA)</a> have lost hundreds of billions in market value, dragging the index down. For example, <a href="https://www.tipranks.com/news/will-nvidia-stock-crash-to-45-this-investor-sounds-the-alarm">Nvidia has lost $35 in stock value since Jan. 23</a>, which amounted to roughly $854 billion. Tesla has shed over $160 in stock value during the same time frame, accumulating over $500 billion in losses. A staggering numbers by all accounts.</p>
<p>Given its heavy tech weighting, the S&amp;P 500 has struggled more than its global counterparts that are less reliant on this sector.</p>
<h2 class="wp-block-heading"><strong>Investing Elsewhere?</strong></h2>
<p>The question now is whether this trend will continue. Historically, when the S&amp;P 500 falls behind early in the year, it rarely recovers to outperform global markets. U.S. stocks may struggle if economic conditions and trade tensions donât improve. This raises an important question for American investors: Should they stick with U.S. stocks or start looking at global opportunities? If the current trends persist, diversification outside the U.S. could become an increasingly attractive option.</p>
<h2 class="wp-block-heading"><strong>Tipranks&#8217; Comparison Tool</strong></h2>
<p>Using Tipranks&#8217; Comparison Tool, we can examine notable S&amp;P 500 Index <a data-autolink="true" href="https://www.tipranks.com/etf">ETFs</a> and how they perform and their near-term outlook. </p>
<figure class="wp-block-image size-large"><a href="https://www.tipranks.com/compare-etfs/sp-500-index-etfs"><img decoding="async" loading="lazy" width="1024" height="550" src="https://blog.tipranks.com/wp-content/uploads/2025/03/image-413-1024x550.png" alt="" class="wp-image-1815158" srcset="https://blog.tipranks.com/wp-content/uploads/2025/03/image-413-1024x550.png 1024w, https://blog.tipranks.com/wp-content/uploads/2025/03/image-413-300x161.png 300w, https://blog.tipranks.com/wp-content/uploads/2025/03/image-413-768x412.png 768w, https://blog.tipranks.com/wp-content/uploads/2025/03/image-413.png 1051w" sizes="(max-width: 1024px) 100vw, 1024px" /></a></figure>
"""
        expected1 = """
<p>The S&amp;P 500<a href="https://www.tipranks.com/index/spx"> (SPX),</a> the world's leading index comprising the biggest 500 traded companies, is now lagging. In one of its worst weeks in decades, <a href="https://www.tipranks.com/news/sp-500-plunges-alongside-trade-war-worries">the index dropped 3.1%, erasing over $3 trillion</a> in value since its February peak. Meanwhile, global markets have performed better, which might be signaling a shift in investor confidence. The U.S. share of global market capitalization has also fallen below 50%, marking a decline in dominance.</p>
<p>Several factors are driving this downturn. The U.S. economy shows signs of weakness, with declining home sales, rising unemployment claims, and slowing consumer spending. These concerns have created a solid infrastructure for investors&#8217; hesitance, leading to market pullback. Nevertheless, the overall reaction to President Trump&#8217;s ongoing trade wars has had an adverse effect on the market and is considered a primary catalyst to the index&#8217;s recent slump. </p>
<h2 class="wp-block-heading"><strong>Tariffs Uncertainty and Tech Stocks Decline</strong></h2>
<p>Trade policy uncertainty has added to the pressure. <a href="https://www.tipranks.com/news/wall-street-braces-for-impact-as-canada-hits-back-with-25-tariffs-on-us-goods">President Trump's tariffs, including a 25% tariff on Canadian and Mexican goods</a> that has now been delayed to April, have clearly unsettled markets. Also, the ongoing trade tensions with China and threats of further tariffs on other nations have only worsened investor sentiment. With global trade facing potential disruptions, companies that rely on international markets could suffer, further weighing on stock performance.</p>
<p>amounted to roughly $854 billion. The technology sector, a major driver of the S&amp;P 500, has been hit hard. Giants like Nvidia <a data-ticker="NVDA" href="https://www.tipranks.com/stocks/nvda">(NVDA)</a> and Tesla <a data-ticker="TSLA" href="https://www.tipranks.com/stocks/tsla">(TSLA)</a> have lost hundreds of billions in market value, dragging the index down. For example, <a href="https://www.tipranks.com/news/will-nvidia-stock-crash-to-45-this-investor-sounds-the-alarm">Nvidia has lost $35 in stock value since Jan. 23</a>, which amounted to roughly $854 billion. Tesla has shed over $160 in stock value during the same time frame, accumulating over $500 billion in losses. A staggering numbers by all accounts.</p>
<p>Given its heavy tech weighting, the S&amp;P 500 has struggled more than its global counterparts that are less reliant on this sector.</p>
<h2 class="wp-block-heading"><strong>Investing Elsewhere?</strong></h2>
<p>The question now is whether this trend will continue. Historically, when the S&amp;P 500 falls behind early in the year, it rarely recovers to outperform global markets. U.S. stocks may struggle if economic conditions and trade tensions don't improve. This raises an important question for American investors: Should they stick with U.S. stocks or start looking at global opportunities? If the current trends persist, diversification outside the U.S. could become an increasingly attractive option.</p>
<h2 class="wp-block-heading"><strong>Tipranks&#8217; Comparison Tool</strong></h2>
<p>Using Tipranks&#8217; Comparison Tool, we can examine notable S&amp;P 500 Index <a data-autolink="true" href="https://www.tipranks.com/etf">ETFs</a> and how they perform and their near-term outlook. </p>
<figure class="wp-block-image size-large"><a href="https://www.tipranks.com/compare-etfs/sp-500-index-etfs"><img decoding="async" loading="lazy" width="1024" height="550" src="https://blog.tipranks.com/wp-content/uploads/2025/03/image-413-1024x550.png" alt="" class="wp-image-1815158" srcset="https://blog.tipranks.com/wp-content/uploads/2025/03/image-413-1024x550.png 1024w, https://blog.tipranks.com/wp-content/uploads/2025/03/image-413-300x161.png 300w, https://blog.tipranks.com/wp-content/uploads/2025/03/image-413-768x412.png 768w, https://blog.tipranks.com/wp-content/uploads/2025/03/image-413.png 1051w" sizes="(max-width: 1024px) 100vw, 1024px" /></a></figure>
"""
        fixed1 = self.spider_util.fix_text(text1)
        self.assertEqual(
            fixed1,
            expected1,
        )

    def test_has_chinese(self):
        """测试 has_chinese 方法"""
        # 测试包含中文的字符串
        self.assertTrue(self.spider_util.has_chinese("你好，世界"))
        self.assertTrue(self.spider_util.has_chinese("Hello 世界"))

        # 测试不包含中文的字符串
        self.assertFalse(self.spider_util.has_chinese("Hello, World!"))
        self.assertFalse(self.spider_util.has_chinese("123456"))

    def test_md5(self):
        """测试 md5 方法"""
        # 测试空字符串的 MD5
        self.assertEqual(self.spider_util.md5(""), "d41d8cd98f00b204e9800998ecf8427e")

        # 测试普通字符串的 MD5
        self.assertEqual(
            self.spider_util.md5("hello"), "5d41402abc4b2a76b9719d911017c592"
        )

    def test_current_time_string(self):
        """测试 current_time_string 方法"""
        # 获取当前时间字符串
        time_str = self.spider_util.current_time_string()

        # 验证格式是否正确 (YYYY-MM-DD HH:MM:SS)
        self.assertRegex(time_str, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

    def test_convert_utc_to_local(self):
        """测试 convert_utc_to_local 方法"""
        # 测试整数时间戳
        timestamp = 1609459200  # 2021-01-01 00:00:00 UTC
        local_time = self.spider_util.convert_utc_to_local(timestamp)
        self.assertEqual(local_time, "2021-01-01 08:00:00")  # UTC+8

        # 测试字符串时间戳
        timestamp_str = "1609459200"
        local_time = self.spider_util.convert_utc_to_local(timestamp_str)
        self.assertEqual(local_time, "2021-01-01 08:00:00")  # UTC+8

    def test_parse_time(self):
        """测试 parse_time 方法"""
        # 测试不同格式的时间字符串
        time_str = "2021-01-01 00:00:00"
        format_str = "%Y-%m-%d %H:%M:%S"
        local_time = self.spider_util.parse_time(time_str, format_str)
        self.assertEqual(local_time, "2021-01-01 08:00:00")  # UTC+8

        # 测试另一种格式
        time_str = "01/01/2021"
        format_str = "%m/%d/%Y"
        local_time = self.spider_util.parse_time(time_str, format_str)
        self.assertEqual(local_time, "2021-01-01 08:00:00")  # UTC+8

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='{"data": [{"link": "http://example.com/1"}, {"link": "http://example.com/2"}]}',
    )
    def test_history_posts(self, mock_file):
        """测试 history_posts 方法"""
        result = self.spider_util.history_posts("dummy_path")

        # 验证返回的数据结构
        self.assertIn("articles", result)
        self.assertIn("links", result)

        # 验证文章数量
        self.assertEqual(len(result["articles"]), 2)

        # 验证链接列表
        self.assertEqual(
            result["links"], ["http://example.com/1", "http://example.com/2"]
        )

    @patch("builtins.open", new_callable=mock_open)
    def test_append_to_temp_file(self, mock_file):
        """测试 append_to_temp_file 方法"""
        # 测试追加数据到文件
        self.spider_util.append_to_temp_file("./tmp/test.txt", "test data")

        # 验证文件被打开并写入数据
        mock_file.assert_called_with("./tmp/test.txt", "a")
        mock_file().write.assert_called_with("test data")

    @patch("os.getenv")
    def test_get_env_variable(self, mock_getenv):
        """测试 get_env_variable 方法"""
        # 设置 mock 返回值
        mock_getenv.return_value = "test_value"

        # 测试获取存在的环境变量
        value = self.spider_util.get_env_variable("TEST_KEY", "fallback_value")
        self.assertEqual(value, "test_value")

    def test_contains_language(self):
        """测试 contains_language 方法"""
        # 测试日语
        self.assertTrue(self.spider_util.contains_language("こんにちは", ["japanese"]))
        self.assertTrue(self.spider_util.contains_language("ありがとう", ["japanese"]))

        # 测试韩语
        self.assertTrue(self.spider_util.contains_language("안녕하세요", ["korean"]))

        # 测试法语/西班牙语
        self.assertTrue(self.spider_util.contains_language("café", ["french"]))
        self.assertTrue(self.spider_util.contains_language("señor", ["spanish"]))

        # 测试不包含指定语言的文本
        self.assertFalse(
            self.spider_util.contains_language("Hello World", ["japanese"])
        )
        self.assertFalse(self.spider_util.contains_language("", ["japanese"]))

    @patch("json.load")
    def test_get_random_proxy(self, mock_json_load):
        """测试 get_random_proxy 方法"""
        # 模拟代理池数据
        mock_proxies = [
            {"region": "GLOBAL", "host": "proxy1.example.com", "port": "8080"},
            {"region": "GLOBAL", "host": "proxy2.example.com", "port": "8080"},
            {"region": "US", "host": "us-proxy.example.com", "port": "8080"},
        ]

        # 设置 mock 返回值
        self.spider_util._proxy_pools = mock_proxies

        # 测试获取 GLOBAL 地区的代理
        proxy = self.spider_util.get_random_proxy("GLOBAL")
        self.assertIn(proxy, [mock_proxies[0], mock_proxies[1]])

        # 测试获取 US 地区的代理
        proxy = self.spider_util.get_random_proxy("US")
        self.assertEqual(proxy, mock_proxies[2])

    @patch("json.dump")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_json_to_file(self, mock_file, mock_json_dump):
        """测试 write_json_to_file 方法"""
        # 测试数据
        test_data = [{"title": "Test Article", "link": "http://example.com"}]

        # 调用方法
        self.spider_util.write_json_to_file(test_data, "./tmp/test.json")

        # 验证文件被打开
        mock_file.assert_called_with("./tmp/test.json", "w", encoding="utf-8")

        # 验证 json.dump 被调用，并且数据格式正确
        mock_json_dump.assert_called_once()
        args, kwargs = mock_json_dump.call_args
        self.assertEqual(args[0], {"data": test_data})
        self.assertEqual(kwargs["ensure_ascii"], False)

    def test_execute_with_timeout(self):
        """测试 execute_with_timeout 方法"""

        # 测试正常执行的函数
        def normal_func():
            time.sleep(0.1)
            return "success"

        # 执行函数
        self.spider_util.execute_with_timeout(normal_func, timeout=1)

        # 测试超时的函数
        def timeout_func():
            time.sleep(2)
            return "timeout"

        # 执行函数
        result = self.spider_util.execute_with_timeout(timeout_func, timeout=0.1)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
