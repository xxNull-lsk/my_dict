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
image_version=latest
image_name=my_dict_ocr
image_tag=xxnull/my_dict_ocr

function start_server()
{
    echo "启动OCR服务..."
    id=`docker ps -a --filter name=${image_name} --format "{{.ID}}"`
    if [ "$id" != "" ]; then
      echo "OCR服务已经启动."
        return
    fi

    param="-d"
    param="$param -p 12126:12126"
    param="$param --name ${image_name}"

    docker run $param ${image_tag}:${image_version}
    ret=$?
    if [ $ret -ne 0 ]; then
        echo "启动OCR服务. exit_code=$ret"
        exit $ret
    fi
    echo "启动OCR服务成功."
}

function stop_server()
{
    echo "停止OCR服务..."
    id=`docker ps -a --filter name=${image_name} --format "{{.ID}}"`
    if [ "$id" != "" ]; then
        docker rm -f $id
    fi
    echo "停止OCR服务成功."
}

function check_docker()
{
    which docker >/dev/null 2>&1
    if [ $? -eq 0 ]; then
      return
    fi
    echo "安装Docker..."
    source /etc/os-release
    if [ "$ID" == "arch" ]; then
        pacman -S --noconfirm --needed docker
        ret=$?
    else
      check_curl
      curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
      ret=$?
    fi
    if [ $ret -ne 0 ]; then
        echo "安装Docker失败. exit_code=$ret"
        exit $ret
    fi
}

function check_curl()
{
    which curl >/dev/null 2>&1
    if [ $? -eq 0 ]; then
      return
    fi
    which apt >/dev/null 2>&1
    if [ $? -eq 0 ]; then
      apt install -y curl
      return
    fi
    which yum >/dev/null 2>&1
    if [ $? -eq 0 ]; then
      yum -y install curl
      return
    fi
    which yum >/dev/null 2>&1
    if [ $? -eq 0 ]; then
      pacman -S --noconfirm --needed curl
      return
    fi
}

function install_server()
{
    check_docker
    systemctl enable docker
    systemctl start docker
    usermod -a -G docker $ORG_USER
    docker images | grep ${image_tag} | grep ${image_version} >/dev/null 2>&1
    if [ $? -ne 0 ]; then
      # 删除已经安装的镜像
      stop_server
      docker rmi ${image_tag}:${image_version} >/dev/null 2>&2
    fi
    echo "拉取镜像..."
    docker pull ${image_tag}:${image_version}
    ret=$?
    if [ $ret -ne 0 ]; then
        echo "拉取失败. exit_code=$ret"
        exit $ret
    fi
    echo "安装OCR服务成功."
}

function check_install()
{
    which docker >/dev/null 2>&1
    if [ $? -ne 0 ]; then
      return 1
    fi
    docker images | grep ${image_tag} | grep latest >/dev/null 2>&1
    if [ $? -ne 0 ]; then
      return 2
    fi
    return 0
}

if [ "$cmd" == "install" ]; then
    if [ `id -u` -ne 0 ]; then
        echo "提升$USER 为管理权限..."
        export ORG_USER=$USER
        echo $PASSWD | sudo -SE -p '' bash $0 $1 $USER
        exit $?
    fi
    echo "以管理员权限运行..."
    # 安装OCR服务
    install_server
elif [ "$cmd" == "start" ]; then
    start_server
elif [ "$cmd" == "stop" ]; then
    stop_server
elif [ "$cmd" == "check_install" ]; then
    check_install
    exit $?
fi

exit 0
}