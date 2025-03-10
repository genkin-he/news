sync:
	source ./news/scripts/init/init.sh && ./sync.sh

clean:
	git pull
	git tag backup && git push origin backup -f && rm -rf .git
	git config --global init.defaultBranch main
	git init .
	git remote add origin git@github.com:genkin-he/news.git
	git add .
	git commit -am "clean"
	git push origin -f
	git branch --set-upstream-to=origin/main

setup:
	git branch --set-upstream-to=origin/main

# 测试相关命令
test:
	@echo "运行 util 目录下的所有测试..."
	python -m unittest discover -s news/scripts/util -p "*_test.py"

.PHONY: sync clean setup test