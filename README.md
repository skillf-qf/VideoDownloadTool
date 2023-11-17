# VideoDownloadTool
这是一个b站视频下载工具，仅供学习参考！

### 1. 安装本项目的Python依赖库
```
requests
qrcode
Image
opencv-python
ffmpy
pyinstaller # 用于打包生成exe单文件
```
可执行下述命令，安装Python依赖库:

```
pip install -r .\requirements.txt
```
如果下载速度比较慢甚至导致下载失败，请尝试更换国内pip源，或者使用以下命令:
```
pip install -r .\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 打包成exe可执行文件

#### 使用pyinstaller库打包生成exe单文件
安装 pyinstaller（如1中已安装则跳过该步骤）
```
py -m pip install pyinstaller
```

根据文件`downloadTool-cmd-api.spec`的参数来打包生成exe文件，如有其它参数需求，可以自行研究更改该文件：
```
pyinstaller .\downloadTool-cmd-api.spec
```

等待结果提示
```
INFO: Building EXE from EXE-00.toc completed successfully.
```
表示成功生成exe文件，然后将文件夹"dist"里的exe文件拷贝出来，其它生成的文件可以一律删除了，最后将exe文件与本项目的文件夹"Source"放置于同一目录下即可！


#### 致谢
- https://github.com/SocialSisterYi/bilibili-API-collect
