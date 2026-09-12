chmod +x ./news/scripts/*.sh && for f in ./news/scripts/*.sh ; do [ -x "$f" ] && [ ! -d "$f" ] && echo $f && time "$f" ; done
chmod +x ./news/scripts/*.py && for f in ./news/scripts/*.py ; do [ -x "$f" ] && [ ! -d "$f" ] && echo $f && time python3 $f ; done

rm -rf .git && git config --global init.defaultBranch main && git init . && git remote add origin git@github.com:genkin-he/news.git