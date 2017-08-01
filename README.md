# workflows.kyoyue
优越加速Alfred Workflow，自动获取服务器信息，支持服务器ping值排序，支持热键生成对应条目的ss/ssr二维码，支持surge配置信息自动生成，支持自动/手动获取更新。

-------

操作GIF示意：

![](https://github.com/wizyoung/workflows.kyoyue/blob/master/gofree.gif?raw=true)

![](https://github.com/wizyoung/workflows.kyoyue/blob/master/ping.gif?raw=true)

![](https://github.com/wizyoung/workflows.kyoyue/blob/master/update.gif?raw=true)

------------------

**使用说明**：
- 首次使用键入`yyset`输入优越加速email和登录密码
- `gofree`  自动获取服务器IP信息等, 该指令设定为查询一次后，信息缓存在本地10分钟，10分钟内再次查询从缓存中读取信息
- `gofree ping` 对所有服务器进行ping 3 次，去平均值排序，超过1000ms的直接判断为超时

以上两条指令，按下`cmd`或者`option`可弹出指定服务器的ss或者ssr二维码

- `gofree surge` 将服务器信息配置成surge所需格式，根据用户指令(按下`fn`或者`ctrl`)复制到剪切板
- `gofree update` 手动检查更新，有新版本时选择是否自动下载更新安装。workflow每3天自动检查更新一次

-----

该workflow只支持Alfred3 (不兼容2)，请到[release](https://github.com/wizyoung/workflows.kyoyue/releases)界面点击下载

-----

## The MIT License (MIT)


