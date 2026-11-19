"""按数据产出判断采集源是否已经失效

逐源的健康告警依赖脚本自己调用 log_action_error，只打日志（util.error）或静默
拿不到数据的脚本永远显示健康——scmp 每轮 403 却从未告警就是这样漏掉的。这里不看
脚本报不报错，只看 news/data/<源>/list.json 里最新一条稿件的 pub_date：超过
STALE_SECONDS 没有新稿就列入汇总，一天最多提醒一次。
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

DATA_DIR = "./news/data"
STATE_PATH = "./tmp/stale_alert.json"
PUB_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
# pub_date 统一按北京时间写入
LOCAL_TZ = ZoneInfo("Asia/Shanghai")
# 留足周末：财经类源周五晚到周一早上本来就没有新稿
STALE_SECONDS = 72 * 3600
REPEAT_SECONDS = 24 * 3600

# 对应脚本已停用的数据目录，不再参与检查：移到了 news/scripts/disabled/，
# 或像 scmp 这样去掉了可执行位（CI 只运行可执行脚本）
IGNORED_SOURCES = frozenset({"cleantechnica", "scmp", "vietnamnews"})


def latest_pub_date(path: str) -> Optional[datetime]:
    """读取 list.json 中最新一条稿件的发布时间，读不到或没有日期返回 None"""
    try:
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
    except (OSError, ValueError):
        return None
    items = payload.get("data", []) if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        return None
    dates = []
    for item in items:
        raw = item.get("pub_date") if isinstance(item, dict) else None
        try:
            dates.append(datetime.strptime(str(raw)[:19], PUB_DATE_FORMAT))
        except ValueError:
            continue
    return max(dates, default=None)


def find_stale_sources(
    data_dir: str, now: datetime, ignored: frozenset
) -> list[tuple[str, datetime]]:
    """返回超过 STALE_SECONDS 没有新稿的源，按最近一条时间从旧到新排序"""
    threshold = now - timedelta(seconds=STALE_SECONDS)
    stale = []
    for name in sorted(os.listdir(data_dir)):
        if name in ignored:
            continue
        latest = latest_pub_date(os.path.join(data_dir, name, "list.json"))
        if latest is not None and latest < threshold:
            stale.append((name, latest))
    return sorted(stale, key=lambda pair: pair[1])


def _read_last_alert(state_path: str) -> float:
    try:
        with open(state_path) as f:
            return float(json.load(f).get("last_alert") or 0)
    except (OSError, ValueError, AttributeError):
        return 0.0


def build_report(
    data_dir: str,
    state_path: str,
    now: datetime,
    ignored: frozenset = IGNORED_SOURCES,
) -> Optional[str]:
    """生成失效源汇总；没有失效源或距上次提醒不足 REPEAT_SECONDS 时返回 None

    只在真正发出提醒时写状态文件，避免每轮提交都带上它。
    """
    if not os.path.isdir(data_dir):
        return None
    stale = find_stale_sources(data_dir, now, ignored)
    if not stale:
        return None
    timestamp = now.timestamp()
    if timestamp - _read_last_alert(state_path) < REPEAT_SECONDS:
        return None
    os.makedirs(os.path.dirname(state_path) or ".", exist_ok=True)
    with open(state_path, "w") as f:
        json.dump({"last_alert": timestamp}, f)
    lines = [
        "#stale_check 以下 {} 个源超过 {} 小时没有新稿：".format(
            len(stale), STALE_SECONDS // 3600
        )
    ]
    for name, latest in stale:
        days = (now - latest).total_seconds() / 86400
        lines.append("- {}：最近一条 {}（{:.1f} 天前）".format(name, latest, days))
    return "\n".join(lines)


def current_local_time() -> datetime:
    """与 pub_date 同口径的北京时间（naive）"""
    return datetime.now(LOCAL_TZ).replace(tzinfo=None)
