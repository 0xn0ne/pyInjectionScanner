# pyInjectionScanner

原项目：https://github.com/sethsec/PyCodeInjection

为了使渗透速度能跟上时代的脚步，原项目的操作速度已经无法满足撒网捕鱼的需求，然后有了弄成自动化扫描的想法。

python 远程代码注入扫描，暂未添加扫描功能，仅对源代码进行优化。但目标依旧是自动化，将会在这几天内弄出扫描函数。

+ VulnApp 文件夹中的 main.py 为测试 web 应用程序
+ pis.py 为攻击脚本

刚刚和大佬交流了一下扫描思路，突然发现很尴尬的事情

![burpsuite](images/Snipaste_2019-08-24_23-48-25.png)

![burpsuite](images/Snipaste_2019-08-25_00-27-27.png)

# 快速开始

### 依赖

+ Python >= 3.6

进入项目目录，使用以下命令安装依赖库

```
$ pip3 install -r requirements.txt
```

若需测试 web 应用程序，在 *VulnApp* 目录下再执行一次以上相同的操作

### 使用说明

**帮助内容**

```
usage: pis.py [-h] [-u URL] [-c CMD] [-p [PARAMS [PARAMS ...]]]
              [-r REQUEST_FILE]

optional arguments:
  -h, --help            显示帮助信息
  -u URL, --url URL     URL；在 url 中使用 "*" 或设置 `-p` 参数指定注入点
  -c CMD, --cmd CMD     远程执行的命令
  -p [PARAMS [PARAMS ...]], --params [PARAMS [PARAMS ...]]
                        指定注入的参数
  -r REQUEST_FILE, --request-file REQUEST_FILE
                        指定请求文件；`*` 和 `-p` 参数均有效
```

