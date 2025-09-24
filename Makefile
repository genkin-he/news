sync:
	source ./news/scripts/init/init.sh && ./sync.sh

clean:
	sh ./clean.sh

setup:
	git branch --set-upstream-to=origin/main

# 测试相关命令
test:
	@echo "运行 util 目录下的所有测试..."
	python -m unittest discover -s news/scripts/util -p "*_test.py"

.PHONY: sync clean setup test