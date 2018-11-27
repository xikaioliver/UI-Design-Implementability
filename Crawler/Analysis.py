
# coding: utf-8

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


import os


# In[3]:


list = os.listdir()
list


# In[6]:


# 创建一个 XMLReader
parser = xml.sax.make_parser()
# turn off namepsaces
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
# 重写 ContextHandler
Handler = LayoutHandler()
parser.setContentHandler( Handler )
for name in list:
    if name.endswith('.xml'):
        print(name)
        parser.parse(name)
        print()

