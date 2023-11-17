#!/usr/bin/env python
# coding=utf-8
#*
 # @Author       : skillf
 # @Date         : 2021-12-14 09:15:34
 # @LastEditTime : 2023-11-18 00:59:49
 # @FilePath     : \VideoDownloadTool\downloadTool-cmd-api.py
#*

from cmath import sin
import os
import time
import base64
import requests
import json
import qrcode
import cv2  # pip install opencv-python
from contextlib import closing
import re
from ffmpy import FFmpeg
#import platform     # 打包成exe程序运行完之后暂停cmd
from version import __version__

def login(url,cookies_file):
    qr = qrcode.QRCode(
        version = 1,
        error_correction = qrcode.constants.ERROR_CORRECT_L,
        box_size = 10,
        border = 1,
    )
    qr.add_data(url)
    qr.make()
    qr_img = qr.make_image()
    qr_name = 'login.png'
    qr_img.save(qr_name)
    wname = 'QRcode'
    login_img = cv2.resize(cv2.imread(qr_name), dsize=(350, 350))
    cv2.imshow(wname, login_img)
    cv2.waitKey(1)

    params = {"oauthKey":oauthKey}
    status = 0
    while True:
        res_info = post_url(API['LOGIN_INFO'],params=params)
        status = res_info.json().get('status')
        #print("wait scan: ",res_info.json())
        if status:
            print("正在登陆...")
            cv2.destroyWindow(wname)
            # print(res_info.json())
            save_cookie(res_info,cookies_file)
            # print("cookies 已获取！")
            os.remove(qr_name)
            break
        else:
            if res_info.json().get('data') == -4:
                print("请打开bilibili手机客户端扫描二维码...")
            elif res_info.json().get('data') == -5:
                print("请在bilibili手机客户端确认登陆...")
        time.sleep(3)

# AV转BV 算法
XOR = 177451812
ADD = 100618342136696320
TABLE = "fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF"
MAP = 9, 8, 1, 6, 2, 4, 0, 7, 3, 5

def av2bv(av: int) -> str:
    av = (av ^ XOR) + ADD
    bv = [""] * 10
    for i in range(10):
        bv[MAP[i]] = TABLE[(av // 58**i) % 58]
    return "".join(bv)


def inputHandle():
    while True:
        s = input("\n\n请输入你想要下载的b站视频的网址或者BV号(退出: q/Q)：\n\n$ ")
        if s == 'q' or s == 'Q':
            exit()
        ms = re.search('BV.{10}',s)
        if not ms:
            ms = re.search('av[0-9]+',s)
        if ms:
            if 'av' in ms.group(0):
                bvNum = "BV"+av2bv(int(ms.group(0)[2:]))
                return bvNum
            elif 'BV' in ms.group(0):
                return ms.group(0)
        else:
            print("信息有误，请重新输入！\n")

def check_login(api, headers=None, cookies=None):
    res_userinfo = get_url(api, headers=headers, cookies=cookies)
    if res_userinfo.json().get('code') == 0:
        print("\n登陆成功！")
        # print(res_userinfo.json())
        print("\n\t欢迎您，{} ~\n".format(res_userinfo.json().get('data').get('name')))
    elif res_userinfo.json().get('code') == -101:
        print("Error: cookies 已过期，请扫描二维码重新登陆！")
        login(qr_url, COOKLES_FILE)

def get_video_details(bv):
    params = {"bvid":bv}
    res_detail = get_url(API['VIDEO_DETAIL'], headers=headers, params=params, cookies=cookies)
    if res_detail.json().get('code') == -404:
        return -404,None,None
    video_title = res_detail.json().get('data').get('title')
    video_bvid = res_detail.json().get('data').get('bvid')
    total_videos = res_detail.json().get('data').get('videos')
    video_duration = res_detail.json().get('data').get('duration')
    video_desc = res_detail.json().get('data').get('desc')
    video_cid = res_detail.json().get('data').get('cid')
    pages = res_detail.json().get('data').get('pages')

    params['cid'] = video_cid
    params['qn'] = "80"
    res_stream = get_url(API['VIDEO_STREAM'], headers=headers, params=params, cookies=cookies)
    quality = VIDEO_DEFINITION_MARK.get(str(res_stream.json().get('data').get('quality')))
    base_info = [video_title,video_bvid,total_videos,video_duration,video_desc,len(pages),quality]
    # print(base_info)

    pages_info = []
    for page in pages:
        pages_info.append({
            'cid':page.get('cid'),
            'page':page.get('page'),
            'part':page.get('part'),
            'duration':page.get('duration'),
        })

    return 0,base_info,pages_info

def show_info(user_info, base_info, pages_info):
    """
    # show eg:
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #                     bilibiliVideoDownloadTool-vx.x.x (′▽`〃)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    #                                        当前用户:【xxx】| 等级:【xxxx】| 硬币:【xxx】
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    视频标题:       xxxxxxxxxxx
    视频番号:       xxxxxxxxxxx
    视频总数:       xxxxxxxxxxx
    视频总时长:     xxxxxxxxxxx
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    视频选集:【xx】| 视频质量:【xxxx】|━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    P1 xxxxxxxxxxx----------------------------------------------------------xx:xx:xx
    P2 xxxxxxxxxxx----------------------------------------------------------xx:xx:xx
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    """
    app_name = "bilibiliVideoDownloadTool-{} (′▽`〃)".format(__version__)
    username = "当前用户:【{}】| 等级:【Lv.{}】| 硬币:【{}】".format(user_info.get('name'),user_info.get('level'),user_info.get('coins'))
    tmpstr = '视频选集:【{}】| 视频质量:【{}】|'.format(base_info[5],base_info[6])
    STR_WIDTH = 80
    app_space_width = (STR_WIDTH-len(app_name.encode('GBK')))//2

    print('━'*STR_WIDTH)
    print(' '*app_space_width,app_name,' '*app_space_width)
    print('━'*STR_WIDTH)
    # 每个中文字符占用两个字节
    # 为保持打印宽度一致，需要修改打印宽度为：STR_WIDTH - (len(username.encode('GBK')-len(username)))
    # 因为最后一个为'】'占用两字节导致尾部会多一个空字节位，因此 修改后的宽度+1 去除空位
    print('{x:>{y}}'.format(x=username,y=STR_WIDTH - (len(username.encode('GBK'))-len(username)) + 1))
    print('━'*STR_WIDTH)
    print("视频标题:\t{}\n视频番号:\t{}\n视频总数:\t{}\n视频总时长:\t{}".format(base_info[0], base_info[1], base_info[2],cs_time(base_info[3])))
    print('━'*STR_WIDTH)
    print(tmpstr,end='')
    print('━'*(STR_WIDTH-len(tmpstr.encode('GBK'))))
    print('━'*STR_WIDTH)
    for page in pages_info:
        single_page_info = cs_str_limit('P{} {}'.format(page.get('page'),page.get('part')))
        # len = 固定长度 - len(single_page_info.encode('GBK'))
        # -: 为字符串多余宽度的填充字符，>{y}: 右对齐, y: 字符串宽度, x: 待打印的字符串
        # '{x:->{y}}'打印字符串x，宽度(除开single_page_info的长度)为y，然后右对齐，左侧字符串多余宽度用'-'来填充
        print(single_page_info+'{x:->{y}}'.format(x=cs_time(page.get('duration')),y=STR_WIDTH-len(single_page_info.encode('GBK'))))
    print('━'*STR_WIDTH)

def selectSection(pages_info):
    input_check = 0
    sections = []
    while(not input_check):
        command = input("\n[1]：全集下载    [2]：指定集数下载    [r/R]：返回主菜单    [q/Q]：退出\n请输入指令：")
        if command == 'q' or command == 'Q':
            exit()
        elif command == 'r' or command == 'R':
            break
        elif command == '1':
            input_check = 1
        elif command == '2':
            error_status = 0
            error_list = []
            while(not error_status):
                section = input("\n请输入你想要下载的具体集数，多集数请以空格隔开(返回上一级请按 [q/Q] )\neg. P1 P2 P3 P4 P5 ...\n\n$ ")
                if section == 'q' or section == 'Q':
                    break
                section =  section.split(' ')
                for s in section:
                    if re.match('P[0-9]+',s):
                        if int(s[1:]) < len(pages_info)+1:
                            sections.append(s[1:])
                        else:
                            error_list.append(s)
                    else:
                        error_list.append(s)
                if error_list:
                    print("输入的具体集数有误: {}\n".format(error_list))
                    sections.clear()
                    error_list.clear()
                    error_status = 0
                else:
                    sections.sort()
                    error_status = 1
                    input_check = 1
        else:
            print("指令错误，请输入正确的指令！")
    return command,sections

def save_cookie(response, cookies_file):
    with open(cookies_file, 'w+') as f:
        cookies = {}
        for key,value in response.cookies.get_dict().items():
            cookies[key] = encode_str(value)
        json.dump(cookies, f)
        cookies.clear()

def read_cookie(cookies_file):
    cookies = {}
    with open(cookies_file, 'r') as f:
        cookies['SESSDATA'] = decode_str(json.loads(f.read()).get('SESSDATA'))
    return cookies

def encode_str(s):
    # encode()转化s为bytes类型
    # b64encode()加密bytes类型
    # decode()最后转化为str类型
    return base64.b64encode(s.encode()).decode()

def decode_str(s):
    # encode()转化s为bytes类型
    # b64decode()解密bytes类型
    # decode()最后转化为str类型
    return base64.b64decode(s.encode()).decode()


def get_url(url, headers=None, params=None, cookies=None):
    res_get = requests.get(url, headers=headers, params=params, cookies=cookies)
    return res_get

def post_url(url, headers=None, params=None, cookies=None):
    res_post = requests.post(url, headers=headers, params=params, cookies=cookies)
    return res_post

def cs_time(t):
    h = t // 3600
    m = (t % 3600) // 60
    s = (t % 3600)% 60
    # 0: 为字符串多余宽度的填充字符，>2d: 右对齐 2: 字符串宽度为2
    # '{:0>2d}'字符串宽度为2,然后右对齐，左侧字符串多余宽度用'0'来填充
    return '{:0>2d}:{:0>2d}:{:0>2d}'.format(int(h),int(m),int(s))

def cs_unit(bytes):
    # Keep one decimal place
    if bytes >= (1024*1024):
        trans = round(bytes / (1024 ** 2), 1)
        unit = "MB"
    else:
        trans = round(bytes / 1024, 1)
        unit = "KB"
    return [trans,unit]

def cs_char(str):
    exclude_char_list = ['\\','/',':','*','?','"','<','>','|']
    for c in str:
        if c in exclude_char_list:
            str=str.replace(c,'_')
    return str

def cs_str_limit(str):
    # 限制打印长度，72为总打印字符长度减去时间字符长度
    if len(str.encode('GBK')) > 72:
        return str[:40]
    else:
        return str

def check_existing_mp4(path, filename):
    # 查找重名文件，并递增命名
    modify_name = filename
    if os.path.exists(filename):
        same_files = []
        for root, subdirs, filenames in os.walk(path):
            for fn in filenames:
                if os.path.splitext(fn)[1] == '.mp4':
                    same_files.append(fn)
        tmp = 0
        if len(same_files) > 1:
            for same in same_files:
                if re.search('\(.+\).mp4',same):
                    i = int(re.search('\d+',re.search('\(.+\).mp4',same).group()).group())
                    if tmp < i:
                        tmp = i
            modify_name = filename.replace('.mp4','('+str(tmp+1)+').mp4')
        else:
            modify_name = filename.replace('.mp4','(1).mp4')
    return modify_name

def download(command, select_list, bv, title, pages_list):
    """
    ┏━ 正在下载: xxxxxxxxxxxxxx
    ┣━┳━ P1 xxxxxxxxxxx----------------------------------【XXXX XXXX】
    ┃ ┗━ [■■■■■■■■■■■■■■■■■■■■] xx% x.xxMB/s Time: xx:xx:xx
    ┣━┳━ P2 xxxxxxxxxxx----------------------------------【XXXX XXXX】
    ┃ ┗━ [■■■■■■■■■■■■■■■■■■■■] xx% x.xxMB/s Time: xx:xx:xx
    ............
    """
    STR_WIDTH = 80
    video_path = os.path.join(os.environ.get('USERPROFILE'), "Downloads", cs_char(title))
    if not os.path.exists(video_path):
        os.mkdir(video_path)

    pages_tmplist = []
    if command == "1":
        pages_tmplist = pages_list
    elif command == "2":
        for i in pages_list:
            if str(i.get('page')) in select_list:
                pages_tmplist.append(i)
    print('\n')
    print('━'*STR_WIDTH,end='\n\n')
    print("即将开始下载: \n\t{}".format(title),end='\n\n')
    # print('━'*STR_WIDTH)
    print("视频保存目录: \n\t{}\n".format(video_path))
    print('━'*STR_WIDTH,end='\n\n')
    time.sleep(1)

    print("┏━ 正在下载: {}".format(title),end='')
    # 对选择的所有集做必要处理
    for page in pages_tmplist:
        part_name = cs_char(page.get('part'))
        if not part_name:
            part_name = cs_char(title)

        basename = os.path.join(video_path, part_name)
        page_num = page.get('page')
        if len(pages_list) > 1:
            basename = os.path.join(video_path, 'P'+str(page_num)+'_'+part_name)

        mp4file = basename+".mp4"
        pinfo = cs_str_limit("\n\r┣━┳━ P{} {}".format(page_num, part_name))
        if os.path.exists(mp4file):
            saved = int(os.path.getsize(mp4file))
            vinfo = "【{}{} 文件已存在】".format(cs_unit(saved)[0],cs_unit(saved)[1])
            # 如果不能正常编码为GBK，则需用GBK编码的超集 GB18030
            # len = 固定长度 - (pinfo GBK编码长度)
            # -: 为字符串多余宽度的填充字符，>{y}: 右对齐, y: 字符串宽度, x: 待打印的字符串
            # print(pinfo+'{x:->{y}}'.format(x=vinfo,y=STR_WIDTH - len(pinfo.encode('GBK')) + (len(vinfo.encode('GB18030'))-len(vinfo))))
            print(pinfo+'{x:->{y}}'.format(x=vinfo,y=STR_WIDTH - len(pinfo.encode('GBK'))))
            pbar = ProgressBar()
            pbar(saved,saved,0)
            continue

        params['bvid'] = bv
        params['cid'] = page.get('cid')
        # 视频字节响应范围 0- 为全部字节
        headers['range'] = "bytes=0-"
        # print("params:",params)
        res = get_url(API['VIDEO_STREAM'], headers=headers, params=params, cookies=cookies)
        quality = VIDEO_DEFINITION_MARK.get(str(res.json().get('data').get('quality')))
        part_urls = res.json().get('data').get('durl')
        video_size = 0
        for ul in part_urls:
            video_size += ul.get('size')
        video_size = cs_unit(video_size)
        # len = 固定长度 - (pinfo GBK编码长度) + (vinfo GB18030编码与UTF-8编码的长度差) -1
        # -: 为字符串多余宽度的填充字符，>{y}: 右对齐, y: 字符串宽度, x: 待打印的字符串
        # '{x:->{y}}'打印字符串x，宽度(除开s的长度)为y，然后右对齐，左侧字符串多余宽度用'-'来填充
        vinfo = "【{}{} {}】".format(video_size[0],video_size[1],quality)
        print(pinfo+'{x:->{y}}'.format(x=vinfo,y=STR_WIDTH - len(pinfo.encode('GBK')) + (len(vinfo.encode('GBK'))-len(vinfo)) -1))
        # 开始对当前集进行下载，循环下载当前集的所有分段
        section_count = 0
        for url in part_urls:
            section_count += 1
            tmpfile = basename+'_'+str(url.get('order'))+".flv.dtdownload"
            flvfile = basename+'_'+str(url.get('order'))+".flv"
            if os.path.exists(tmpfile):
                os.remove(tmpfile)

            if os.path.exists(flvfile):
                saved = int(os.path.getsize(flvfile))
                pbar = ProgressBar()
                pbar(saved,saved,0)
                continue

            pbar = ProgressBar()
            # Because stream=True packets are not downloaded at one time,
            # the requested connection is correctly closed through 'contextlib.closing'.
            with closing(requests.get(url.get('url'), stream=True, headers=headers)) as res:
                content_size = int(res.headers.get('content-length'))
                with open(tmpfile, "ab") as f:
                    start_time = time.time()
                    data_download = 0
                    for data in res.iter_content(chunk_size=1024):
                        if data: # filter out keep-alive new chunks

                            # 在f对象中写入data数据
                            f.write(data)
                            data_download += len(data)
                            use_time = time.time() - start_time
                            if use_time > 1 or data_download == content_size:
                                pbar(data_download,content_size,use_time,section_count,len(part_urls))
                                start_time = time.time()
            if int(os.path.getsize(tmpfile)) == content_size:
                os.rename(tmpfile,flvfile)

        merge_video(video_path,mp4file)
        for root, subdirs, filenames in os.walk(video_path):
            for fn in filenames:
                if os.path.splitext(fn)[1] == '.flv' or os.path.splitext(fn)[1] == '.txt':
                    os.remove(os.path.join(root, fn))
    os.startfile(video_path)

def ProgressBar():
    data_count = []
    def bar(saved_data,total_data,usetime,current_section_count=None,total_section_count=None):
        data_count.append(saved_data)
        percent = saved_data / total_data * 100
        if len(data_count) > 1:
            data_add = cs_unit(data_count[-1] - data_count[-2])
        else:
            data_add = cs_unit(data_count[-1])

        if usetime:
            speed = data_add[0]
            if data_add[1] == 'MB':
                unit = 1024 ** 2
            elif data_add[1] == 'KB':
                unit = 1024 ** 1

            requested_time = cs_time(int(total_data-saved_data) / unit / speed)
        else:
            speed = 0
            requested_time = "00:00:00"

        # 进度条长度
        scale = 42
        load = "#" * (saved_data * scale // total_data)
        empty = "-" * (scale - saved_data * scale // total_data)

        # ＂ <＂、＂>＂、＂^＂符号表示左对齐、右对齐、
        # 3.2f 字符串宽度为3，同时四舍五入保留两位小数
        # {:^3.0f} ： 字符串宽度为3，居中对齐，字符串多余宽度默认用空格填充
        if total_section_count is not None and total_section_count > 1: # 判断是否显示当前下载的分段编号
            print("\r┃ ┗━ [{}{}] {:>3.0f}% [{}/{}] {:^3.2f}{}/s Time: {}        ".format(load,empty,percent,current_section_count,total_section_count,speed,data_add[1],requested_time),end='')
        else:
            print("\r┃ ┗━ [{}{}] {:>3.0f}% {:^3.2f}{}/s Time: {}        ".format(load,empty,percent,speed,data_add[1],requested_time),end='')
    return bar

def merge_video(video_path,video_name):

    if os.environ.get('os') == 'Windows_NT':
        # print('Windows')
        # 添加ffmpeg.exe环境变量
        if os.environ['PATH'].find('Source') == -1:
            os.environ['path'] = os.environ.get('PATH')+';'+os.getcwd()+"\\Source\\ffmpeg;"

    # print("\nos.environ['path']:",os.environ['path'])
    # exit(0)
    videos_file = os.path.join(video_path, 'videos_file.txt')
    # print(videos_file)
    with open(videos_file, 'w', encoding='utf-8') as f:
        for root, subdirs, filenames in os.walk(video_path):
            # print(root)
            for fn in filenames:
                if os.path.splitext(fn)[1] == '.flv':
                    # 文件名须用单引号括起来，防止空格和特殊符号引起程序报错
                    f.write('file \'{}\'\n'.format(fn))
    video_name = check_existing_mp4(video_path,video_name)
    # 转换flv为mp4
    # print("合并转换视频中...")
    ffmpeg = FFmpeg(
        global_options=['-loglevel', 'quiet', '-f', 'concat', '-safe', '0'],
        inputs={videos_file: None},
        outputs={video_name: ['-codec', 'copy']}
    )
    ffmpeg.run()
    # print("合并转换成功:\n".format(video_name))
    # print("\t{}\n".format(video_name))


if __name__ == '__main__':

    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "accept-encoding": "identity",
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/85.0.4183.121 Safari/537.36 ",
        "referer": 'https://www.bilibili.com/'
    }

    params = {
        # "bvid":"BV1kZ4y1u7dw",  # 必要（可选）: avid与bvid任选一个
        # "cid":"216162032",      # 必要
        "qn":"80",              # 非必要	未登录默认32（480P）登录默认64（720P）值含义见上表 注：dash方式无效
        "fnval":"0",            # 非必要	默认为0 (0 2: flv方式（可能会有分段）1: 低清mp4方式（仅240P与360P，且限速65K/s）16 80: dash方式（音视频分流，支持H.265）)
        "fnver":"0",            # 非必要	固定为0
        "fourk":"0"             # 非必要	默认为0 (0: 画质最高1080P 1: 画质最高4K)
    }

    API = {
        "LOGIN_URL":"http://passport.bilibili.com/qrcode/getLoginUrl",
        "LOGIN_INFO":"http://passport.bilibili.com/qrcode/getLoginInfo",
        "USER_INFO":"http://api.bilibili.com/x/space/myinfo",
        "VIDEO_PLAYURL":"http://api.bilibili.com/x/player/playurl",
        "VIDEO_DETAIL":"http://api.bilibili.com/x/web-interface/view",
        "VIDEO_PAGELIST":"http://api.bilibili.com/x/player/pagelist",
        "VIDEO_STREAM":"http://api.bilibili.com/x/player/playurl",
    }

    VIDEO_DEFINITION_MARK = {
        "125":"HDR 真彩色",              # 需求认证大会员账号
        "120":"4K 超清",                 # 需求认证大会员账号
        "116":"1080P60 高帧率",          # 需求认证大会员账号
        "112":"1080P+ 高码率",           # 需求认证大会员账号
        "80":"1080P 高清",               # 需要认证登录账号
        "74":"720P60 高帧率",
        "64":"720P 高清",
        "32":"480P 清晰",
        "16":"360P 流畅",
        "6":"240P 极速",
    }

    COOKLES_NAME = "cookie.json"
    config_path = os.path.join(os.getcwd(), "Source", "config")
    if not os.path.exists(config_path):
        os.mkdir(config_path)
    COOKLES_FILE = os.path.join(config_path, COOKLES_NAME)

    # 测试：视频分段
    # 搞机番外篇：MIUI 8最快最详细体验 广告少了吗？
    #bv_number = "BV1Us411i7BT"

    # 测试：纯中文标题
    # 婴儿级教程：带你从0.1到1制作Awtrix桌面像素屏
    # bv_number = "BV18Y411W7Qt"

    # 测试：纯英文标题
    # 【公开课】完美的Vim课程【生肉】
    #bv_number = "BV1Cb411u7L9"

    # 测试：中英混合
    # 【完整版-麻省理工-线性代数】全34讲+配套教材
    #bv_number = "BV1ix411f7Yp"

    # 测试：AV号
    # 字幕君交流场所
    #bv_number = "av2"
    # 弹幕测试专用
    #bv_number = "av271"
    # 【致自己】要努力加油
    #bv_number = "av98800013"

    # print(biliBV.encode("av2"))

    # exit(0)

    res_login = get_url(API['LOGIN_URL'], headers=headers)
    qr_url = res_login.json().get('data').get('url')
    oauthKey = res_login.json().get('data').get('oauthKey')
    try:
        cookies = read_cookie(COOKLES_FILE)
    except FileNotFoundError:
        login(qr_url, COOKLES_FILE)
        cookies = read_cookie(COOKLES_FILE)
    check_login(API['USER_INFO'], cookies=cookies, headers=headers)

    while True:
        res_userinfo = get_url(API['USER_INFO'], headers=headers, cookies=cookies)
        user_info = res_userinfo.json().get('data')

        bv_number = inputHandle()
        # print(bv_number)
        # exit(0)
        status,base_info,pages_info = get_video_details(bv_number)
        if status == -404:
            print("\n抱歉，该视频不存在！")
            continue
        show_info(user_info,base_info,pages_info)
        command,select_list = selectSection(pages_info)
        if command == 'r' or command == 'R':
            continue
        download(command, select_list, bv_number, base_info[0], pages_info)
        print("\n\n《{}》 下载完成！\n\n".format(base_info[0]))

    # # 打包成exe程序运行完之后暂停cmd
    # if platform.system() == 'Windows':
    #     os.system('pause')
