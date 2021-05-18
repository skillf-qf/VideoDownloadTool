#!/usr/bin/env python
# coding=utf-8

#!/usr/bin/env python
# coding=utf-8
#* 
 # @Author: skillf
 # @Date: 2021-04-15 22:55:57
 # @LastEditTime: 2021-05-18 12:47:18
 # @FilePath: \bilibiliVideoDownloadTool-v2.03\downloadTool-v2.03.py
#*

from lxml import etree
import json
import requests
import time
from os.path import join
import os
import shutil
import sys
import platform

pathSeparator = '\\'

currentRootDir = os.path.dirname(sys.argv[0])
downloadPath = currentRootDir + '\\Downloads'
ffmpeg = currentRootDir + '\\Include\\ffmpeg\\ffmpeg.exe'
configFile = currentRootDir + '\\Include\\config\\config'

if platform.system() == 'Linux':
    downloadPath = os.getcwd() + '/Downloads'
    ffmpeg = 'ffmpeg'
    configFile = os.getcwd() + '/Include/config/config'
    pathSeparator = '/'

# SESSDATA有效期是30天，过后需要重新去网页获取
with open(configFile) as f:
    SESSDATA = f.read()
    value = SESSDATA.split('=')
    #print(value[1])
    if value[1]=='\'\'':
        print("SESSDATA不能为空，请修改配置文件 ./Include/config/config\nSESSDATA=''\n")
        if platform.system() == 'Windows':
            os.system('pause')
        exit()


#检查网址信息
def checkUrl(url):
    urlType = ''
    urlApi = ''
    if  url.find('video') > -1:
        urlApi = "https://api.bilibili.com/x/player/playurl"
        urlType = 'up'

    elif  url.find('bangumi') > -1:
        urlApi = "https://api.bilibili.com/pgc/player/web/playurl"
        urlType = "bangumi"
    return urlType,urlApi

#处理文件、文件夹名字中不允许存在的特殊字符串
def characterConversion(str):
    exclusive = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    ls = list(str)
    #print(ls)
    for i in ls:
        if i in exclusive:
            ls[str.find(i)] = '_'
    #print(''.join(ls))
    return ''.join(ls)     

#处理每一页的音视频数据
def singlePageProcessing(url,bvid,cid,title,qn,fnval,path):
    params = {
        "otype": "json",
        "bvid": bvid,
        "qn": qn,
        "fnval": fnval
    }
    params['cid'] = cid

    headers = {
        # SESSDATA有效期是30天，过后需要重新去网页获取
        "cookie": f"{SESSDATA}",
        "referer": url,
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/85.0.4183.121 Safari/537.36 "
    }
    urlApi = checkUrl(url)[1]
    pageInfo = requests.get(url=urlApi, headers=headers, params=params).json()
    pageData = pageInfo['data']
    pageDash = pageData['dash']
    pageVideo = pageDash['video']
    pageAudio = pageDash['audio'][0]
    videoUrls = []
    audioUrl = ''
    #video = videoInfo.get('dash').get('video')

    #print(pageInfo)
    #print(pageDash)
    #print(type(pageVideo))
    #print(len(pageVideo))
    #print("qn: ", qn)
    for i in pageVideo:
        if i['id'] == int(qn):
            videoUrls.append(i['base_url'])
    #print(videoUrls)
    #sys.exit()

    videoName = 'video.m4s'
    #print("===================================")
    #print(videoUrls[0])

    for videoUrl in videoUrls:
        saveFile(videoUrl, path, videoName)
        time.sleep(2)

    audioUrl = pageAudio.get('base_url')
    audioName = 'audio.m4s'
    saveFile(audioUrl, path, audioName)
    #time.sleep(2)

    #print("\n合并文件： ",title)
    newName = path+pathSeparator+title+'.mp4'
    #print(newName)
    mergeFile(join(path, videoName),join(path, audioName),newName)
    #os.system('pause')

def readonly_handler(func, path, execinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def downloads(url, urlapi, videoType, accept_quality, urldata):
    accept_description = {'80':"1080P 高清",'60':"720P 高清",'32':"480P 清晰",'16':"360P 流畅"}
    qn = accept_quality[0] # height quality
    # 大会员视频质量限制，非大会员最高 1080
    if int(qn) > 80:
        #print('qn:',qn)
        qn = '80'
    #sys.exit()
    fnval = videoType
    bvid = urldata.get('bvid')
    title = characterConversion(urldata.get('videoData').get('title'))
    pages = urldata.get('videoData').get('pages')

    #print("downloadPath: ",downloadPath)

    command = '1'
    sections = []
    print('\n已找到视频：{}\n 总共{}集\n'.format(title,len(pages)))
    if len(pages)>1:
        result = selectSection()
        command = result[0]
        sections = result[1]

    print('\n')
    if not os.path.exists(downloadPath):
        os.mkdir(downloadPath)
    if os.path.exists(downloadPath+pathSeparator+title):
        #print(downloadPath+'\\'+title)
        shutil.rmtree(downloadPath+pathSeparator+title,onerror=readonly_handler)
        time.sleep(1)
    os.mkdir(downloadPath+pathSeparator+title)
    #print('qn: ',qn)
    #print('videoType: ',fnval)
    #print('bvid: ',bvid)
    #print('title: ',title)
    #print('pages: ',len(pages))
    #showInfo(title,bvid,len(pages),downloadPath)
    #exit()
    currentCount = 0
    start = time.perf_counter()
    if command == '1':
        showInfo(title,bvid,len(pages),accept_description[qn],downloadPath)
        for page in pages:
            currentCount = currentCount + 1
            #print('cid: ',page['cid'],'part: ',page['part'])
            #print('正在下载： ', page['part'],' ',accept_description[qn])
            progressBar(page['part'],currentCount,len(pages),start)
            singlePageProcessing(url,bvid,page['cid'],page['part'],qn,fnval,downloadPath+pathSeparator+title)
    elif command == '2':
        showInfo(title,bvid,len(sections),accept_description[qn],downloadPath)
        for section in sections:
            currentCount = currentCount + 1
            #print('正在下载：', pages[section-1]['part'],' ',accept_description[qn])
            progressBar(pages[section-1]['part'],currentCount,len(sections),start)
            singlePageProcessing(url,bvid,pages[section-1]['cid'],pages[section-1]['part'],qn,fnval,downloadPath+pathSeparator+title)

#保存服务器回应的音视频数据
def saveFile(base_url, path, filename):
    
    savePath = join(path, filename)

    headers = {
        "accept": "*/*",
        "accept-encoding": "identity",
        "accept-language": "zh-CN,zh;q=0.9",
        "referer": "https://www.bilibili.com",
        "range": "bytes=0-",  # 视频字节响应范围 0- 为全部字节
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/85.0.4183.121 Safari/537.36 "
    }
    res = requests.get(url=base_url, stream=True, headers=headers)

    videoBytes = int(res.headers['content-length'])
    #print('videoBytes: ',videoBytes)
    mode = 'wb'
    #合并多个视频文件
    if os.path.exists(savePath):
        if videoBytes == int(os.path.getsize(savePath)):
            return True
        elif videoBytes > int(os.path.getsize(savePath)):
            mode = 'ab'
            headers['range'] = f"bytes={os.path.getsize(savePath)}-"
            res = requests.get(url=base_url, stream=True, headers=headers)
            #content_length = int(res.headers['content-length'])
        else:
            os.remove(savePath)

    #print(res.status_code)
    #print("save path:",savePath)
    with open(savePath, mode) as f:
            for chunk in res.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    #print(f'\r下载进度:{int(int(os.path.getsize(savePath)) / videoBytes * 100)}%',end='', flush=True)
    f.close()

#处理网页数据
def dataHandling(url):
    html = requests.get(url).text
    parser = etree.HTML(html)
    scripts = parser.xpath("//script")
    dataInfo = "window.__INITIAL_STATE__"
    playInfo = "window.__playinfo__"
    dataEnd = ";(function"
    data = {}

    #print(scripts)
    accept_quality_list = []
    accept_quality = ''
    for script in scripts:
        body = script.xpath("text()")
        #print("\n")
        
        if len(body) == 0:
            continue
        #print(body[0])
     
        #获取视频播放画质列表
        elif body[0].find(playInfo) == 0:
            #print(body[0][body[0].find('accept_quality')-1 :body[0].rfind('video_codecid')-2])
            accept_quality = body[0][body[0].find('accept_quality')-1 :body[0].rfind('video_codecid')-2]
            accept_quality_list = (accept_quality[accept_quality.find('[')+1:-1]).split(',')
        
        elif body[0].find(dataInfo) == 0:
            data = json.loads(body[0][len(dataInfo) + 1:body[0].rfind(dataEnd)])
            break
    #print(accept_quality_list)
    #print(data)
    return accept_quality_list, data

def mergeFile(video_path,audio_path,new_path):
    
    # 合并的输入/输出文件整个路径都需要用双引号 "" 括起来，不然ffmpeg会报错。
    try:
        mergeStatus = os.system(f"{ffmpeg} -loglevel quiet -i \"{video_path}\" -i \"{audio_path}\" -codec copy \"{new_path}\"")
    except IOError as e:
            print("Error: 文件合并失败：",e)
            if platform.system() == 'Windows':
                os.system('pause')

    if not mergeStatus:
        os.remove(video_path)
        os.remove(audio_path)
        #print("文件合并完成 !")
    else:
        print("文件合并失败 。。。")
        if platform.system() == 'Windows':
            os.system('pause')


def inputHandle():
    url_check = 0
    #url = input("请输入你想要下载的视频网址：")
    while(not url_check):
        url = input("请输入你想要下载的视频网址：")
        #print(url.find('https://www.bilibili.com/'))
        if url.find('https://www.bilibili.com/') < 0:
            url_check = 0
            print('输入的网址有误，请重新输入！')
        else:
            url_check = 1

    return url

def selectSection():
    input_check = 0
    while(not input_check):
        command = input("1：全集下载    2：指定集数下载    q|Q：退出\n请输入指令：")
        #print("command: ",command)
        if command == 'q' or command == 'Q':
            exit()
        if command == '1':
            #print("command: ",command)
            input_check = 1
            sections = []
        elif command == '2':
            section = input("请输入你想要下载的集数（数字形式），多集数请以空格隔开: \n")
            #print(len(section))
            #print(section.__contains__(" "))
            section =  section.split(' ')
            sections = []
            for s in section:
                sections.append(int(s))
            sections.sort()
            #print(sections)
            input_check = 1
        else :
            print("指令错误，请输入对应指令！")
            input_check = 0
            continue

    return command,sections



def showInfo(video_title,bvid,pages,video_quality,download_path):
    """
    # show eg:
    ==========================================
    正在下载：【MIT】线性代数（声道修复）
    番        号：BV1bb411H7JN
    视频页数：35
    下载路径：c:\\Users\\qf\\Desktop\\bilibiliVideoDownloadTool-V2.01\\Downloads
    ==========================================
    """
    print('==========================================')
    print("正在下载：{}\n番    号：{}\n视频页数：{}\n视频质量：{}\n下载路径：{}".format(video_title,bvid,pages,video_quality,download_path))
    print('==========================================')

def progressBar(section_info,current_count,content_length,start_time):
    """
    # show eg:
    Downloading: [■■■■----------------------------------------------]  8 % Time: 00:01:11 03矩阵的乘法和逆
    """
    # 进度条长度
    scale = 20 
    #print(current_count)
    load = "■" * (current_count*scale// content_length)
    empty = "-" * (scale - current_count*scale//content_length)
    dr = current_count*scale//content_length*(100/scale)
    #elapsedTime = time.perf_counter() - start_time
    elapsedTime = timeTransfer(int("{:.0f}".format(time.perf_counter() - start_time)))
    # 多余的空格为了覆盖上一行预留的字符串
    # ^表示中间对齐 后面的数字表示位数. {:^10d} 中间对齐 (宽度为10)
    # ＂ <＂、＂>＂、＂^＂符号表示左对齐、右对齐、居中对齐
    # .nf 表示保留小数点位数,n表示小数点的位数 {:.2f} 3.14 保留小数点后两位
    # {:^3.0f} ： 宽度为 3，中间对齐默认空格填充，四舍五入
    #print("\rDownloading: [{}{}] {:^3.0f}% Time: {:0>2d}:{:0>2d}:{:0>2d}  正在下载：{}          ".format(load,empty,dr,elapsedTime[0],elapsedTime[1],elapsedTime[2],section_info),end="")
    print("\rDownloading: [{}{}] {:^3.0f}% Time: {:0>2d}:{:0>2d}:{:0>2d} {}          ".format(load,empty,dr,elapsedTime[0],elapsedTime[1],elapsedTime[2],section_info),end="")

def timeTransfer(t):
    h = t // 3600
    m = (t % 3600) // 60
    s = (t % 3600)% 60
    return h,m,s


if __name__ == '__main__':

    print("bilibiliVideoDownloadTool-V2.03 程序已启动 (′▽`〃)\n")
    #print('__file__: ',__file__)
    #print('sys.path[0]: ',sys.path[0])
    #print('sys.argv[0]: ',sys.argv[0])
    
    url = inputHandle()

    # 模拟电子技术基础 上交大 郑益慧主讲
    #url = 'https://www.bilibili.com/video/BV1Gt411b7Zq?p=46'
    # PyQt5教程，来自网易云课堂
    # url = 'https://www.bilibili.com/video/BV154411n79k?from=search&seid=7744546193416442486'
    
    #url = 'https://www.bilibili.com/video/BV1NZ4y1L7Hq?p=5'

    #print(url)
    #print(command)
    #print(sections)
    urlstatus = checkUrl(url)
    #urlType = urlstatus[0]
    urlApi = urlstatus[1]
    #print(urlstatus[1])

    accept_quality_list = dataHandling(url)[0]
    urlData = dataHandling(url)

    #print(accept_quality_list)
    #print(urlData)
    videoType = 80 # videoType : m4s
    downloads(url, urlApi, videoType, urlData[0], urlData[1])
    #bvid = urlData[1].get('bvid')
    #cid = '72840297'
    #qn = urlData[0][0]
    #title = '02-PN结的形成'
    #singlePageProcessing(url,bvid,cid,title,int(qn),fnval)
    print("\n\n下载完成！\n\n")
    if platform.system() == 'Windows':
        os.system('pause')
