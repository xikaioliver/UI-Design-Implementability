
# coding: utf-8

# In[3]:


import os


# In[6]:


list = os.listdir('./APK')
f_list = open('./APK/UnDecompiled_List.txt', 'a+')
for name in list:
    if name.endswith('.apk'):
        f_list.write(name+'\n')
f_list.close()


# In[8]:


with open("./APK/UnDecompiled_List.txt","r") as f:
    lines = f.readlines()
    print(lines)
f_w = open('./APK/Decompiled_List.txt', 'a+')
with open("./APK/UnDecompiled_List.txt","w") as f_w_un:
    for line in lines:
        print('jadx ./APK/' + line[:-2] + ' -d ./APK/' + line[:-5])
        file = os.popen('jadx ./APK/' + line[-2] + ' -d ./APK/' + line[:-5])
        f_w.write(line)
f_w.close()


# In[9]:


list = os.listdir('./APK')
for name in list:
    if name.endswith('.apk'):
        print('jadx ./APK/' + name + ' -d ./APK/' + name[:-4])
        file = os.popen('jadx ./APK/' + name + ' -d ./APK/' + name[:-4])


# In[1]:


import xml.sax
 
class LayoutHandler( xml.sax.ContentHandler ):
#    def __init__(self):
#       self.CurrentData = ""
 
   # 元素开始事件处理
   def startElement(self, tag, attributes):
      print(tag + '{', end = "")
 
   # 元素结束事件处理
   def endElement(self, tag):
      print('}', end = "")
 
    # 内容事件处理
#    def characters(self, content):
#     if content != "":
#         print(content, end="")
#       if self.CurrentData == "type":
#          self.type = content
#       elif self.CurrentData == "format":
#          self.format = content
#       elif self.CurrentData == "year":
#          self.year = content
#       elif self.CurrentData == "rating":
#          self.rating = content
#       elif self.CurrentData == "stars":
#          self.stars = content
#       elif self.CurrentData == "description":
#          self.description = content


# In[2]:


# 创建一个 XMLReader
parser = xml.sax.make_parser()
# turn off namepsaces
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
 
# 重写 ContextHandler
Handler = LayoutHandler()
parser.setContentHandler( Handler )
   
parser.parse("name_APKTOOL_DUPLICATENAME_0x7f040a0a.xml")


# In[3]:


# 创建一个 XMLReader
parser = xml.sax.make_parser()
# turn off namepsaces
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
 
# 重写 ContextHandler
Handler = LayoutHandler()
parser.setContentHandler( Handler )
   
parser.parse("name_APKTOOL_DUPLICATENAME_0x7f040a0b.xml")


# In[5]:


# 创建一个 XMLReader
parser = xml.sax.make_parser()
# turn off namepsaces
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
 
# 重写 ContextHandler
Handler = LayoutHandler()
parser.setContentHandler( Handler )
   
parser.parse("name_APKTOOL_DUPLICATENAME_0x7f040a0c.xml")

