#!/usr/bin/env bash

SOURCE="$0"
while [ -h "$SOURCE"  ]; do
    DIR="$( cd -P "$( dirname "$SOURCE"  )" && pwd  )"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /*  ]] && SOURCE="$DIR/$SOURCE"
done
SRC_PATH="$( cd -P "$( dirname "$SOURCE"  )" && pwd  )"
cd $SRC_PATH

cmd=$1
image_name=my_dict_ocr
image_tag=xxnull/my_dict_ocr

if [ "$cmd" == "install" ]; then
    which docker >/dev/null 2>dev/null
    if [ $? -ne 0 ]; then
        echo "安装Docker..."
        curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
        ret=$?
        if [ $ret -ne 0 ]; then
            echo "安装Docker失败."
            exit $ret
        fi
    fi
    echo "拉取镜像..."
    docker pull ${image_tag}:latest
    ret=$?
    if [ $ret -ne 0 ]; then
        echo "拉取失败."
        exit $ret
    fi
elif [ "$cmd" == "start" ]; then
    echo "启动OCR服务..."
    id=`docker ps -a --filter name=${image_name} --format "{{.ID}}"`
    if [ "$id" != "" ]; then
        docker rm -f $id
    fi

    param="-itd"
    param="$param --ulimit core=0"
    param="$param -v /etc/localtime:/etc/localtime:ro"
    param="$param -v /etc/timezone:/etc/timezone:ro"
    param="$param --restart=always"
    param="$param -p 12126:12126"
    param="$param --name ${image_name}"

    docker run $param ${image_tag}:latest
    ret=$?
    if [ $ret -ne 0 ]; then
        exit $ret
    fi
elif [ "$cmd" == "stop" ]; then
    echo "停止OCR服务..."
    id=`docker ps -a --filter name=${image_name} --format "{{.ID}}"`
    if [ "$id" != "" ]; then
        docker rm -f $id
    fi
fi

exit 0