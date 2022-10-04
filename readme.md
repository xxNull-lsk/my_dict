# 下载地址
- github [下载安装](https://github.com/xxNull-lsk/my_dict/releases/latest) 。
- 下载链接：https://home.mydata.top:8095/share/dkxS22x1  提取码：1wde
- 百度网盘链接：https://pan.baidu.com/s/1jYhvQNSqF-ghJbeeA0MSuw 提取码:ihbi
- [星火应用商店](https://www.deepinos.org/) 搜索：mydict


# 简介

一个词典客户端。支持：

- 剪贴板取词。
- OCR取词。
- 基本的查词功能。
- 基本的翻译功能。
- 支持开机自启动。
- 单文件，双击即可运行。
- 支持离线词典。



# 词典界面

![zhuchuangkou](https://home.mydata.top:8684/blog/20221002200213-main.png)

![zhuchuangkou](https://home.mydata.top:8684/blog/20221002200217-main2.png)

# 剪贴板取词

![剪贴板取词](https://home.mydata.top:8684/blog/20221002200220-clipboard.png)

![剪贴板取词](readme.assets/clipboard2.png)

# OCR取词

英文取词：

![grab.png](https://home.mydata.top:8684/blog/20221002200223-grab.png)

汉字取词：

![grab.png](https://home.mydata.top:8684/blog/20221002200226-grab1.png)

# 设置界面

![设置界面](https://home.mydata.top:8684/blog/20221002200232-setting.png)

# 下载离线词典

![下载词典](https://home.mydata.top:8684/blog/20221002200235-download.png)

# 生词本

![wordbook](https://home.mydata.top:8684/blog/20221002200237-wordbook.png)

![review](https://home.mydata.top:8684/blog/20221002200241-review.png)

# 支持的系统

- UOS 社区版
- Ubuntu 20.04

理论上也支持其他Linux发行版，未测试。



# 源码运行

```bash
python3 mydict.py
```



# 打包

```bash
pip3 install pyinstaller
pip3 install -r requirements.txt
pyinstaller mydict.spec
```

注意：

- 第2步有可能会失败。建议先源码运行，报错缺少哪个库就用pip3安装哪个库，这样一个一个地安装成功的概率会高很多。

- 打包时可能会报某些目录没有执行权限，这会导致打包失败。建议通过chmod给对应的文件加上可执行权限。

# 感谢

- 感谢stardict项目，该程序的离线词典使用的该项目的词典。下载地址：http://download.huzheng.org
- 在线查词和翻译功能使用了有道词典的API，所有权归有道，不晓得是否可以使用，侵删。



# 开发文档

https://blog.mydata.top/index.php/category/mydict/
