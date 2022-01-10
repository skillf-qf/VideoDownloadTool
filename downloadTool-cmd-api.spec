'''
Author       : skillf
Date         : 2022-01-10 11:31:45
LastEditTime : 2022-01-10 12:47:25
FilePath     : \VideoDownloadTool\downloadTool-cmd-api.spec
'''


# -*- mode: python -*-

block_cipher = None

# 此列表存放项目设计的所有python脚本文件
py_files = [
    'downloadTool-cmd-api.py',
]

# 打包输出exe程序的名字
app_name = 'downloadTool-3.0'

a = Analysis(
    py_files,
    # 此列表为项目绝对路径
    pathex=['.'],
    binaries=[],
    # 此列表存放所有资源文件，每个文件是一个2元组元素
    # datas: non-binary files included in the app.
    datas=None,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    # 此处console=True表示，打包后的可执行文件双击运行时屏幕会出现一个cmd窗口，不影响原程序运行
    console=True,
    # 设置程序图标, 切记：绝对路径
    icon='Source\\Pic\\favicon.ico'
)
