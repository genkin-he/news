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