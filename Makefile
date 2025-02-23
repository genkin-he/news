sync:
	source ./news/scripts/init/init.sh && ./sync.sh

clean:
	rm -rf .git
	git config --global init.defaultBranch main
	git init .
	git remote add origin git@github.com:genkin-he/news.git
	git add .
	git commit -am "clean"

setup:
	git branch --set-upstream-to=origin/main