# Cache News

财经/科技资讯采集仓库：各源一个脚本，由 GitHub Actions 定时运行，抓取结果直接提交回仓库。仅用于代码学习与研究，如有侵权请联系作者删除。

## 目录结构

| 路径 | 说明 |
| --- | --- |
| `news/scripts/*.py` / `*.sh` | 各采集源脚本，CI 会运行该目录下所有可执行脚本 |
| `news/scripts/disabled/` | 已停用的源（长期 403、站点停更或被其他脚本替代），CI 不运行 |
| `news/scripts/util/` | 公共工具：`spider_util.py`（日志、健康状态、超时、写文件等） |
| `news/scripts/callbacks/` | CI 收尾：`stale_check.py` 检查长期无新稿的源，`after_actions.py` 汇总告警发 Slack |
| `news/data/<源>/list.json` | 各源最近的稿件 |
| `tmp/health/` | 各源连续失败的状态，只在失败/恢复时写入 |
| `tmp/schedule/` | `should_run_every` 限频用的上次运行时间 |

## CI

- `save news`（`.github/workflows/news.yml`）：由外部 `repository_dispatch` 触发，8 路并行运行脚本（单个脚本 15 秒超时，超时或异常退出会在运行页标成 warning），然后提交并推送数据。
- `clean history`（`clean.yml`）：每天北京时间 19:00 打 `backup` tag 后重建 git 历史，控制仓库体积。
- `cleanup workflow runs`（`cleanup_runs.yml`）：定期删除旧的 workflow run 记录。

## 告警

- 单个源连续失败超过 30 分钟才告警，同一故障每小时最多提醒一次（见 `spider_util.flush_action_errors`）。
- 不依赖脚本是否上报错误的兜底：某个源超过 72 小时没有新稿，会被汇总进一条提醒，每天最多一次（见 `callbacks/stale_check.py`）。停用的源要加进 `IGNORED_SOURCES`。

## 本地使用

```bash
pip install -r requirements.txt
make sync   # 依次运行所有采集脚本
make test   # 运行单元测试（会改写 ./tmp 下的健康状态文件）
```

新增源：在 `news/scripts/` 下新建可执行脚本，使用 `SpiderUtil` 打日志、写数据；请求失败用 `util.log_action_error` 上报，才能进入健康告警。

## License

MIT，详见 LICENSE。
