import atexit
import hashlib
import json
import os
import random
import signal
import threading
import time
import traceback
from datetime import datetime, timedelta, timezone

import ftfy


# 采集健康状态：每个源一个小文件，记录最近一次成功、连续失败的起点、最近一次告警。
# CI 以 xargs -P 8 并行跑脚本，按源分文件可以避免多进程写同一份状态。
HEALTH_DIR = "./tmp/health"
# 连续失败超过这个时长才值得告警。CI 每 2~4 分钟跑一轮，境外站点偶发超时是常态，
# 单轮失败并不代表源坏了——实测 coinlive / businesstoday 这类源当天仍在正常出稿。
HEALTH_GRACE_SECONDS = 30 * 60
# 同一次持续故障的重复告警间隔，避免坏一次就每轮刷屏
HEALTH_REPEAT_SECONDS = 60 * 60


class SpiderUtil:
    def __init__(self, notify=True):
        # 打印调用栈信息
        stack = traceback.extract_stack()
        # 获取倒数第二个调用（即调用 SpiderUtil() 的地方）
        filename = os.path.basename(stack[-2].filename)
        # 获取文件名，不要后缀
        self.current_file = filename.split(".")[0]
        self.path = "./news/scripts/util/urls.json"
        self.notify = notify
        # 本轮缓存的告警文案，等一轮跑完再按健康状态决定是否真的发出去
        self._pending_errors = []
        self._flush_registered = False

    # 打印日志
    def info(self, message):
        print(f"[\033[32m{self.current_file}\033[0m] {message}")

    def error(self, message):
        print(f"[\033[31m{self.current_file}\033[0m] {message}")

    def should_run_by_minute(self, divisor=10):
        """
        检查当前分钟数是否能被指定数字整除
        Args:
            divisor: 除数，默认为 10
        Returns:
            bool: 如果当前分钟数能被除数整除则返回 True，否则返回 False
        """
        current_time = datetime.now()
        current_minute = current_time.minute
        if current_minute % divisor == 0:
            self.info(f"当前分钟数 {current_minute} 能被{divisor}整除，可以执行任务")
            return True
        else:
            self.info(f"当前分钟数 {current_minute} 不能被{divisor}整除，跳过执行")
            return False

    def history_posts(self, filepath):
        """
        从指定文件中读取历史文章数据，并返回文章列表和链接列表。

        参数：
        filepath (str): 包含历史文章数据的文件路径。

        返回：
        dict: 包含文章列表和链接列表的字典。
        """
        try:
            with open(filepath) as user_file:
                articles = json.load(user_file)["data"]
                links = []
                for article in articles:
                    links.append(article["link"])
                return {"articles": articles, "links": links}
        except:
            return {"articles": [], "links": []}

    def fix_text(self, text):
        """
        解析文本，将文本中的特殊字符转换为标准字符
        """
        return ftfy.fix_text(text)

    def parse_time(self, time_str, format):
        """
        将给定的时间字符串解析为本地时间，并返回格式化后的时间字符串。

        参数：
        time_str (str): 要解析的时间字符串。
        format (str): 时间字符串的格式。

        返回：
        str: 格式化后的本地时间字符串。
        """
        timeObj = datetime.strptime(time_str, format)
        local_time = timeObj + timedelta(hours=8)
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    def has_chinese(self, string):
        """
        检查字符串中是否包含中文字符。

        参数：
        string (str): 要检查的字符串。

        返回：
        bool: 如果字符串中包含中文字符，返回 True；否则返回 False。
        """
        for ch in string:
            if "\u4e00" <= ch <= "\u9fff":
                return True
        return False

    def current_time(self):
        """
        获取当前的本地时间，时区为 UTC+8。

        返回：
        datetime: 当前的本地时间。
        """
        return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))

    def md5(self, string):
        """
        计算给定字符串的 MD5 哈希值。

        参数：
        string (str): 要计算哈希值的字符串。

        返回：
        str: 字符串的 MD5 哈希值。
        """
        return hashlib.md5(string.encode()).hexdigest()

    def current_time_string(self):
        """
        获取当前的本地时间字符串，格式为"YYYY-MM-DD HH:MM:SS"。

        返回：
        str: 当前的本地时间字符串。
        """
        return self.current_time().strftime("%Y-%m-%d %H:%M:%S")

    def convert_utc_to_local(self, timestamp, tz=timezone.utc):
        """
        将传入的时间戳转换为本地时间（UTC+8），并返回格式化后的时间字符串。

        参数：
        timestamp (int/str): 要转换的时间戳，可以是整数或字符串。

        返回：
        str: 格式化后的本地时间字符串，格式为"YYYY-MM-DD HH:MM:SS"。
        """
        if isinstance(timestamp, str):
            timestamp = float(timestamp)
        utc_time = datetime.fromtimestamp(timestamp, tz)
        local_time = utc_time.astimezone(timezone(timedelta(hours=8)))
        return local_time.strftime("%Y-%m-%d %H:%M:%S")

    def append_to_temp_file(self, file_path, data):
        try:
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.isdir(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            if not os.path.exists(file_path):
                with open(file_path, "w") as file:
                    pass
            with open(file_path, "a") as file:
                file.write(data)
        except Exception as e:
            # 捕获异常并打印错误信息
            self.error(f"写入临时文件过程中发生错误：{str(e)}")

    def log_action_error(self, error_message):
        error_message = f"#{self.current_file} {error_message}"
        # 打印错误信息（CI 日志里始终保留完整细节）
        self.error(error_message)
        if not self.notify:
            return
        # 截断上限由 100 提到 400：100 字符常把 URL 之后的错误原因整段砍掉，
        # 而 CI 以 xargs -P 8 并行追加同一文件，单行仍远低于 PIPE_BUF(4096) 的
        # O_APPEND 原子写入上限，并发安全。
        if len(error_message) > 400:
            error_message = error_message[:400] + "\n"
        # 不再立刻写进告警文件：先缓存，等本轮结束时结合历史健康状态判断。
        self._pending_errors.append(error_message)
        self._register_flush()
        return

    def _register_flush(self):
        """进程正常退出或被 gtimeout SIGTERM 掉时，都要把缓存的告警结算掉"""
        if self._flush_registered:
            return
        self._flush_registered = True
        atexit.register(self.flush_action_errors)
        try:
            previous = signal.getsignal(signal.SIGTERM)

            def handler(signum, frame):
                self.flush_action_errors()
                if callable(previous) and previous not in (
                    signal.SIG_DFL,
                    signal.SIG_IGN,
                ):
                    previous(signum, frame)
                raise SystemExit(143)

            signal.signal(signal.SIGTERM, handler)
        except (ValueError, OSError):
            # 不在主线程时无法装信号处理器，atexit 仍然兜底
            pass

    def _health_path(self):
        return os.path.join(HEALTH_DIR, f"{self.current_file}.json")

    def _read_health(self):
        try:
            with open(self._health_path()) as health_file:
                return json.load(health_file)
        except Exception:
            return {}

    def _write_health(self, health):
        try:
            os.makedirs(HEALTH_DIR, exist_ok=True)
            with open(self._health_path(), "w") as health_file:
                json.dump(health, health_file)
        except Exception as e:
            self.error(f"写入健康状态失败：{str(e)}")

    def flush_action_errors(self):
        """进程退出时按健康状态结算本轮告警

        结算放在进程级而不是每轮结束：像 stockinvest / biopharmadive 这种一个进程
        连跑两轮的脚本，若按轮结算，后一轮成功会把前一轮的失败计时清掉，一个长期
        坏掉的入口就永远告不出来。只要本进程出现过错误，本轮就记为失败。


        单轮失败不告警：CI 每 2~4 分钟一轮，跑在 GitHub 的美国 runner 上，
        境外/境内站点偶发超时与 403 是常态，逐轮告警只会把真正坏掉的源淹掉。
        连续失败超过 HEALTH_GRACE_SECONDS 才发，且同一次持续故障最多每
        HEALTH_REPEAT_SECONDS 提醒一次；期间一旦成功一轮，计时清零。
        """
        if not self.notify:
            return
        errors, self._pending_errors = self._pending_errors, []
        now = time.time()
        health = self._read_health()

        if not errors:
            if health.get("first_failure"):
                self.info("recovered, failure streak cleared")
            self._write_health({"last_success": now})
            return

        first_failure = health.get("first_failure") or now
        last_alert = health.get("last_alert", 0)
        failing_for = now - first_failure
        health = {
            "last_success": health.get("last_success"),
            "first_failure": first_failure,
            "last_alert": last_alert,
        }

        if failing_for >= HEALTH_GRACE_SECONDS and (
            now - last_alert >= HEALTH_REPEAT_SECONDS
        ):
            health["last_alert"] = now
            for message in errors:
                self.append_to_temp_file("./tmp/action_errors.log", message + "\n")
        else:
            self.info(
                "failing for {:.0f}s (< {}s grace or alerted {:.0f}s ago), "
                "not paging".format(
                    failing_for, HEALTH_GRACE_SECONDS, now - last_alert
                )
            )
        self._write_health(health)

    def get_env_variable(self, key, fallback):
        """
        获取环境变量的值，如果不存在则返回默认值

        参数：
        key (str): 环境变量的键
        fallback (str): 如果环境变量不存在时返回的默认值

        返回：
        str: 环境变量的值或默认值
        """
        return os.getenv(key, fallback)

    def execute_with_timeout(self, func, *args, timeout=10, **kwargs):
        """
        接受一个函数，执行这个函数并设置超时时间，同时统计函数的执行时间

        参数：
        func (callable): 要执行的函数
        *args: 传递给函数的位置参数
        timeout (int): 超时时间，单位为秒
        **kwargs: 传递给函数的关键字参数

        返回：
        tuple: (执行结果，执行时间) 如果在超时时间内完成
        None: 如果函数执行超时
        """

        # 打印调用栈信息
        stack = traceback.extract_stack()
        # 获取倒数第二个调用（即调用 execute_with_timeout 的地方）
        filename = os.path.basename(stack[-2].filename)
        lineno = stack[-2].lineno

        self.info(f"{filename}#{lineno} start executing...")
        # 一轮成功也要留痕（清掉失败计时），所以这里就注册结算钩子
        self._register_flush()
        # 记录本轮截止时间，供采集脚本在循环中查询剩余预算并主动收尾。
        # 仅靠给每个请求设 timeout 不足以守住预算：requests 的 timeout 是 connect 与 read
        # 各算一次（最坏翻倍），urlopen 亦是每次 socket 操作各算一次，因此“请求数 × 超时”
        # 会低估最坏耗时。有了截止时间，脚本可以少抓几篇但保住已抓到的内容，
        # 而不是被整轮判超时、零产出。
        self._deadline = time.time() + timeout
        # 本轮是否已经落盘过内容，决定超时该不该进告警通道（见下方超时分支）
        self._wrote = False

        class FuncThread(threading.Thread):
            def __init__(self, func, *args, **kwargs):
                threading.Thread.__init__(self)
                self.func = func
                self.args = args
                self.kwargs = kwargs
                self.result = None
                self.execution_time = None

            def run(self):
                start_time = time.time()
                try:
                    self.func(*self.args, **self.kwargs)
                except Exception as e:
                    traceback.print_exc()
                    # 使用外部的 log_action_error 方法
                    self._log_action_error(f"#{lineno} error: {repr(e)}\n")
                finally:
                    end_time = time.time()
                    self.execution_time = end_time - start_time

            def _log_action_error(self, error_message):
                # 调用外部类的 log_action_error 方法
                self._outer.log_action_error(error_message)

        # 将外部类的实例传递给线程类
        thread = FuncThread(func, *args, **kwargs)
        thread._outer = self
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            # 原先此处直接 return None，不打印也不告警——采集卡住时整轮完全静默，
            # 而 CI 的 `gtimeout 15` 随后会 SIGTERM 杀掉进程，更不会留下任何记录。
            # 超时属于运行级失败，必须进入告警通道。
            #
            # 但「超时」分两种：已经落过盘的，本轮内容并没丢，抓慢一点属于 CI 到
            # 境内站点的正常网络抖动（c114 即长期如此），报警只会淹没真问题；
            # 零产出的才是真失败。故按是否写过文件区分严重级别。
            if self._wrote:
                self.info(
                    f"#{lineno} timeout after {timeout}s, "
                    "aborted with data already written"
                )
            else:
                self.log_action_error(
                    f"#{lineno} timeout: still running after {timeout}s, aborted"
                )
            return None
        self.info(
            f"Function #{filename}#{lineno} executed in {thread.execution_time:.3f} seconds."
        )
        return None

    def time_left(self):
        """距本轮截止还剩多少秒；execute_with_timeout 之外调用时返回一个较大值"""
        deadline = getattr(self, "_deadline", None)
        if deadline is None:
            return float("inf")
        return deadline - time.time()

    def out_of_time(self, reserve=2.0):
        """剩余预算不足 reserve 秒时返回 True，用于在循环中主动收尾"""
        return self.time_left() < reserve

    def read_with_deadline(self, response, seconds, chunk_size=65536):
        """按「总时长」读完响应体，超时抛 TimeoutError

        urlopen/requests 的 timeout 只约束单次 socket 操作：对端每次都在超时前
        吐一小段数据，整体就能无限拉长。CI 的美国 runner 拉境内站点时正是这样——
        连接和每次 read 都不超时，整轮却被 10 秒看门狗打断且零产出。
        这里给读取过程本身加一个总预算，慢就尽早放弃，把剩余预算留给重试。
        """
        deadline = time.time() + seconds
        chunks = []
        while True:
            if time.time() > deadline:
                raise TimeoutError(
                    f"body read exceeded {seconds:.1f}s, got {sum(map(len, chunks))} bytes"
                )
            chunk = response.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)

    def request_timeout(self, preferred=5, reserve=1.0, minimum=1.0):
        """把单次请求的超时收敛进本轮剩余预算

        循环里的 out_of_time() 只能拦住「还没发出的请求」，拦不住已经在等的那一个：
        脚本里写死 timeout=30 而本轮预算只有 10 秒时，慢站点必然走到
        "timeout: still running after 10s, aborted"——被外层强杀，连已抓到的内容
        都写不进文件。用剩余预算反推上限后，请求会先自己超时返回，脚本还有机会
        落盘已有结果。

        preferred 允许传 requests 的 (connect, read) 二元组，逐项收敛后原样返回。
        """
        if isinstance(preferred, tuple):
            return tuple(
                self.request_timeout(item, reserve, minimum) for item in preferred
            )
        left = self.time_left()
        if left == float("inf"):
            return preferred
        return max(minimum, min(preferred, left - reserve))

    def write_json_to_file(self, data, filename, encoding="utf-8"):
        """
        将 JSON 数据以格式化的形式写入传入的文件，并同时写入 SQLite 数据库

        参数：
        data (dict): 要写入文件的 JSON 数据
        filename (str): 文件名

        返回：
        None
        """
        try:
            # 确保目标文件夹存在
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # 写入 JSON 文件
            with open(filename, "w", encoding=encoding) as f:
                json.dump({"data": data}, f, ensure_ascii=False, indent=4)
                self._wrote = True
                self.info(f"JSON data has been written to {filename} successfully.")

            # # 写入数据库
            # with self._get_db_connection() as conn:
            #     cursor = conn.cursor()
            #     self._insert_articles(cursor, data)
            #     conn.commit()
            #     self.info(f"{filename} inserted to db successfully.")

        except Exception as e:
            self.info(f"Error writing data: {e}")
            # 记录详细错误日志
            self.log_action_error(f"Error in write_json_to_file: {str(e)}")

    def contains_language(self, text, languages=None):
        """
        判断文本是否包含指定的语言字符。

        参数：
        text (str): 要检查的文本
        languages (list): 要检查的语言列表，支持以下值：
            'japanese' - 日语
            'korean' - 韩语
            'french' - 法语
            'spanish' - 西班牙语
            默认为 ['japanese']

        返回：
        bool: 如果文本包含指定语言的字符，返回 True；否则返回 False
        """
        if not text:
            return False

        # 默认检查中文和英文
        if languages is None:
            languages = ["japanese"]

        for ch in text:
            # 检查日语
            if "japanese" in languages and (
                "\u3040" <= ch <= "\u309f"  # 平假名
                or "\u30a0" <= ch <= "\u30ff"  # 片假名
                or "\u4e00" <= ch <= "\u9fff"  # 汉字
            ):
                return True
            # 检查韩语
            if "korean" in languages and "\uac00" <= ch <= "\ud7a3":
                return True
            # 检查法语/西班牙语（主要检查特殊字符）
            if (
                "french" in languages or "spanish" in languages
            ) and ch in "éèêëàâäôöûüçñ":
                return True

        return False

    _proxy_pools = None  # 类变量用于存储代理池

    @property
    def proxy_pools(self):
        """懒加载代理池"""
        if self._proxy_pools is None:
            try:
                with open("./news/scripts/util/proxy_pool.json") as f:
                    self._proxy_pools = json.load(f)
            except Exception as e:
                self.info(f"加载代理池失败：{str(e)}")
                self._proxy_pools = []
        return self._proxy_pools

    def get_random_proxy(self, region: str = "GLOBAL") -> dict[str, str] | None:
        """从代理池中根据地区随机选择一个代理"""
        try:
            region_proxies = [
                proxy for proxy in self.proxy_pools if proxy.get("region") == region
            ]
            if not region_proxies:
                self.info(f"没有找到 {region} 地区的代理")
                return None
            return random.choice(region_proxies)
        except Exception as e:
            self.info(f"获取随机代理时发生错误：{str(e)}")
            return None
