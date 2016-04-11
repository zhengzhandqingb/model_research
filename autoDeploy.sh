#!/usr/bin/env bash
#跳转到该脚本所在目录
basedir=`dirname $0`
cd ${basedir}

git checkout master
git pull

#启动python执行环境
source pyenv/bin/activate

python model_research/main.py

