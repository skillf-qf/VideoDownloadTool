# VideoDownloadTool
这是一个b站视频下载工具，仅供学习参考！

依赖的库:
```
requests
qrcode
Image
opencv-python
ffmpy
```

打包成exe可执行文件：

#### 使用pyinstaller库打包生成exe单文件
安装 pyinstaller
```
py -m pip install pyinstaller
```

打包成exe
```
pyinstaller --workpath .\tmp -F .\downloadTool-cmd-api.spec
```
-F  生成结果是一个exe程序，所有第三方依赖库和其他资源都被打包进该exe程序中，但最后还需要将Source文件夹单独复制到与exe文件同一目录下。
-–workpath    为输出的所有临时文件指定存放目录: tmp

#### 致谢
- https://github.com/SocialSisterYi/bilibili-API-collect
