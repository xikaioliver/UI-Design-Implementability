
# coding: utf-8

# In[1]:


import openpyxl
import re
import requests
import os
from sys import argv
from openpyxl import Workbook
from datetime import datetime
import html.parser
from pyquery import PyQuery as pq


# In[2]:


def download_apk(url):
    """
    下载文件
    :param url:下载链接
    :param num:索引值
    """
    global count
    global successful_count
    count += 1
    succeed = 'Succeed'
    failure = 'Failure'
    print('第' + str(count) + '条url:\n' + url)
    filename = os.path.basename(url)
    filename = filename.split('?')[0]
    response = requests.head(url)
    filesize = round(float(response.headers['Content-Length']) / 1048576, 2)
    apk_format = 'application/vnd.android.package-archive'

    # 过滤非zip文件或大于100.00M的文件
    # TODO 可按需修改
    if response.headers['Content-Type'] == apk_format and filesize < 100.00:
        print('文件类型：' + response.headers['Content-Type'] + "\n" +
              '文件大小：' + str(filesize) + 'M' + "\n" +
              '文件名：' + str(filename))

        # 下载文件
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.0.3; zh-cn; M032 Build/IML74K) '
                          'AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
            'Connection': 'keep-alive', }
        file = requests.get(url, headers=headers, timeout=10)

        with open(filename, 'wb') as apk:
            apk.write(file.content)
            print(succeed + "\n")
            successful_count += 1

    else:
        print('文件类型:' + response.headers['Content-Type'] + "\n" +
              '文件大小:' + str(filesize) + 'M' + "\n" +
              failure + "\n")


# In[3]:


def crawl(url):
    download_list = []
    response = requests.get(url)
    d = pq(response.text)
    package_list = d('div').filter('#full-package-list').children('a.package-header')
    for i in range(len(package_list)):
        download_list.append('https://f-droid.org' + package_list.eq(i).attr('href'))
    partial_next = d('li').filter('.nav.next').children('a.label').attr('href')
    if partial_next != None:
        next_url = 'https://f-droid.org' + partial_next
    else:
        next_url = ''
    return download_list, next_url


# In[4]:


def get_download_url(url):
    response = requests.get(url)
    d = pq(response.text)
    download_url = d('p').filter('.package-version-download').eq(0).children('a').attr('href')
    return download_url


# In[5]:


import xml.sax
 
class LayoutHandler_new( xml.sax.ContentHandler ):
    result = {}
    
    def __init__(self):
        self.CurrentData = ""
        
    # 元素开始事件处理
    def startElement(self, tag, attributes):
        if '.' in tag:
            if not tag.startswith('android.'):
                if tag in LayoutHandler.result:
                    LayoutHandler.result[tag] += 1
                else:
                    LayoutHandler.result[tag] = 1
        
#     # 元素结束事件处理
#     def endElement(self, tag):
#         print('}', end = "")

class LayoutHandler( xml.sax.ContentHandler ):
    result = {}
    
    def __init__(self):
        self.CurrentData = ""
        
    # 元素开始事件处理
    def startElement(self, tag, attributes):
        if '.' in tag:
            if not tag.startswith('android.'):
                if tag not in LayoutHandler.result:
                    LayoutHandler.result[tag] = 1

# 创建一个 XMLReader
parser_new = xml.sax.make_parser()
parser = xml.sax.make_parser()
# turn off namepsaces
parser_new.setFeature(xml.sax.handler.feature_namespaces, 0)
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
 
# 重写 ContextHandler
Handler_new = LayoutHandler_new()
Handler = LayoutHandler()
parser_new.setContentHandler( Handler_new )
parser.setContentHandler( Handler )


# In[6]:


def analyse(rootdir):
    list =  os.listdir(rootdir)
    new = True
    for file in list:
        if not file.endswith('.xml'):
            continue
        if new:
            parser_new.parse(os.path.join(rootdir,file))
            new = False
        else:
            parser.parse(os.path.join(rootdir,file))


# In[7]:


def traverse(filename):
    rootdir = filename + '/resources/res'
    try:
        list = os.listdir(rootdir)
    except:
        pass
    else:
        #遍历./resources/res/layout (layout-...) 中XML文件，进行统计
        for i in range(0,len(list)):
            if list[i].startswith('layout'):
                path = os.path.join(rootdir,list[i])
                analyse(path)


# In[71]:


count = 0
successful_count = 0

url = input("Please input initial URL: ")
download_list = []
page_count = 0

result = {}

#一次最多爬取10页，300个apk
while url != '' and page_count < 10:
    print('crawling URL: ' + url)
    
    #分析网页，获得package list和下个url
    download_list, url = crawl(url)
    for package_url in download_list:
        download_url = get_download_url(package_url)
        
        #下载APK
        download_apk(download_url)
        
        #反编译
        filename = os.path.basename(download_url).split('?')[0]
        file = os.popen('jadx ' + str(filename))
        file.read()
        
        #分析第三方component
        traverse(str(filename)[:-4])
    page_count += 1
print('共尝试下载' + str(count) + '个APK，成功' + str(successful_count) + '个')


# In[29]:


list = os.listdir()
for filename in list:
    if os.path.isdir(filename):
        print(filename)
        traverse(filename)
#     if os.path.isdir(list[i]):
#         traverse(list[i])


# In[73]:


#将结果转化为dataframe便于统计。保存入CSV文件中
import pandas as pd
data = pd.DataFrame(LayoutHandler.result, index=['num']).T
data.to_csv("result_2.csv",index=True,sep=',')


# In[8]:


import pandas as pd
import matplotlib.pyplot as plt
data = pd.read_csv("result_2.csv", sep=',')
data.rename(columns={'Unnamed: 0':'component'}, inplace = True)


# In[9]:


dict = {}
for i in range(data.shape[0]):
    key = data.iloc[i]['component'].partition('.')[0]
    if key in dict:
        dict[key] += data.iloc[i]['num']
    else:
        dict[key] = data.iloc[i]['num']


# In[11]:


LayoutHandler.result = dict


# In[12]:


LayoutHandler.result

