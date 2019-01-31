
# coding: utf-8

# In[4]:


from uiautomator import device as d
d.info


# In[3]:


d.screen.on()


# In[8]:


d.press.camera()


# In[14]:


d.orientation


# In[90]:


d.screenshot("home.png")


# In[84]:


d.dump("hierarchy.xml", compressed=False)


# In[104]:


d(scrollable='true').info


# In[82]:


d.dump("hierarchy.xml")


# In[40]:


d.watcher("AUTO_FC_WHEN_ANR").when(clickable="true").click(text="")


# In[23]:


d(scrollable=True).fling.vert.backward()


# In[21]:


d(clickable=True, instance=3).click()


# In[29]:


import xml.sax
import os
from uiautomator import device as d
import re
import subprocess
import time
android_home = os.environ['ANDROID_HOME'] + '/'


# In[2]:


def findFiles(rootdir):
    #find all files under the rootdir
    files = []
    list = os.listdir(rootdir)
    for subPath in list:
        path = os.path.join(rootdir,subPath)
        if os.path.isdir(path):
            files.extend(findFiles(path))
        if os.path.isfile(path):
            files.append(path)
    return files

# class MyHandler( xml.sax.ContentHandler ):
#     def __init__(self, resourceIDList):
#         self.resourceIDList = resourceIDList
 
#    # 元素开始事件处理
#     def startElement(self, tag, attributes):
#         self.CurrentData = tag
#         if attributes.get('package') != 'com.android.systemui':
#             resourceID = str(attributes.get('resource-id'))
#             bounds = str(attributes.get('bounds'))
#             find = resourceID.find('/')
#             if find != -1:
#                 resourceID = str(resourceID[find+1:])
#                 self.resourceIDList[resourceID] = bounds
                
class FindLayoutHandler (xml.sax.ContentHandler):
    def __init__(self, appName, resultList):
        self.appName = appName
        self.resultList = resultList
 
    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if ('.' in tag) and (not 'android' in tag) and (not self.appName in tag):
            resourceID = str(attributes.get('android:id'))
            find = resourceID.find('/')
            if find != -1:
                resourceID = resourceID[find+1:]
            if resourceID in self.resultList:
                self.resultList[resourceID].append(tag)
            else:
                self.resultList[resourceID] = [tag]


# In[3]:


def getThirdPartyComponents(appName, layoutFolder):
    resultList = {}
    if not os.path.exists(layoutFolder):
        return resultList
    files = findFiles(layoutFolder)
    for file in files:
        if file.endswith('.xml'):
            parser = xml.sax.make_parser()
            parser.setFeature(xml.sax.handler.feature_namespaces, 0)
            Handler = FindLayoutHandler(appName, resultList)
            parser.setContentHandler( Handler )
            parser.parse(file)
            resultList = Handler.resultList
    return resultList


# In[4]:


# class LayoutHandler (xml.sax.ContentHandler):
#     def __init__(self, appName, hasThirdParty):
#         self.appName = appName
#         self.hasThirdParty = hasThirdParty
 
#     def startElement(self, tag, attributes):
#         self.CurrentData = tag
#         if ('.' in tag) and (not 'android' in tag) and (not self.appName in tag):
#             self.hasThirdParty = True


# In[5]:


# def hasThirdParty(path):
#     layoutPath = os.path.join(path,'resources','res','layout')
#     if (os.path.exists(layoutPath)):
#         xmlFiles = os.listdir(layoutPath)
#         hasThirdParty = False
#         appName = path.split('/')[-1].split('.')[1]
#         for file in xmlFiles:
#             filePath = os.path.join(layoutPath,file)
#             if os.path.isfile(filePath) and filePath.endswith('.xml'):
#                 parser = xml.sax.make_parser()
#                 parser.setFeature(xml.sax.handler.feature_namespaces, 0)
#                 Handler = LayoutHandler(appName, hasThirdParty)
#                 parser.setContentHandler( Handler )
#                 parser.parse(filePath)
#                 hasThirdParty = Handler.hasThirdParty
#             if hasThirdParty:
#                     return True
#     return False
    
    
def getList(folderPath):
    files = []
    list = os.listdir(folderPath)
    appList = 'appList.txt'
    writePath = os.path.join(folderPath,appList)
    writeFile = open(writePath, 'w')
    for subPath in list:
        path = os.path.join(folderPath,subPath)
        if os.path.isdir(path):
            writeFile.write(path.split('/')[-1] + '.apk' + '\n')
#             if hasThirdParty(path):
#                 writeFile.write(path.split('/')[-1] + '.apk' + '\n')
    writeFile.close()


# In[87]:


rootDir = '/Users/xikaioliver/Desktop/APK'
getList(rootDir)
appList = os.path.join(rootDir,'appList.txt')

with open(appList, 'r') as f:
        apks_to_test = [line.rstrip() for line in f]
f.close()

for apk in apks_to_test:
        m = re.findall('^(.*)_.*\.apk', apk)
        packageName = m[0]
        try:
            ps = subprocess.Popen([android_home + 'build-tools/26.0.1/aapt', 'dump', 'badging', os.path.join(rootDir,apk)],
                                  stdout=subprocess.PIPE)
            output = subprocess.check_output(('grep', 'launchable-activity:'), stdin=ps.stdout)
            label = output.decode('utf-8')
        except subprocess.CalledProcessError:
            continue
        m = re.findall('^launchable-activity:(.*)$', label)
        try:
            startActivity = m[0].split()[0][6:-1]
        except IndexError:
            continue
        else:
            thirdPartyComponents = getThirdPartyComponents(packageName.split('.')[1], os.path.join(rootDir, apk[:-4], 'resources','res','layout'))
            if len(thirdPartyComponents) > 0:
                test(apk, startActivity, packageName)


# In[86]:


def test(apk, startActivity, packageName):
    print('!!!')
    d.press('home')
    subprocess.Popen(['adb', 'install', os.path.join(rootDir,apk)])
    subprocess.Popen(['adb', 'shell', 'am', 'start', '-n', packageName + '/' + startActivity])
    time.sleep(10)
    
    
    #遍历5min
    traverse(1, os.path.join('/Users/xikaioliver/Desktop/Result', packageName))
    
    time.sleep(1000)
    subprocess.Popen(['adb', 'shell', 'am', 'force-stop', packageName])
    d.press('home')


# In[77]:


class DumpFileHandler( xml.sax.ContentHandler ):
    def __init__(self, thirdPartyComponentList):
        self.thirdPartyComponentList = thirdPartyComponentList

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        if attributes.get('package') != 'com.android.systemui':
            resourceID = str(attributes.get('resource-id'))
            bounds = str(attributes.get('bounds'))
            find = resourceID.find('/')
            if find != -1:
                resourceID = str(resourceID[find+1:])
                if resourceID in thirdPartyComponents:
                    self.thirdPartyComponentList[resourceID] = bounds

def traverse(pageNum, resultFolder):
    current = d.dump('temp.xml', compressed=False)
    thirdPartyComponentList = {}
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = DumpFileHandler(thirdPartyComponentList)
    parser.setContentHandler( Handler )
    parser.parse('temp.xml')
    thirdPartyComponentList = Handler.thirdPartyComponentList
    
    if len(thirdPartyComponentList) > 0:
        d.screenshot(os.path.join(resultFolder, str(pageNum) + ".png"))
        d.dump(os.path.join(resultFolder, str(pageNum) + ".xml"), compressed=False)
        writePath = os.path.join(resultFolder, str(pageNum) + '.txt')
        writeFile = open(writePath, 'w')
        for component in thirdPartyComponentList:
            writeFile.write(component + '\n')
        writeFile.close()

    componentList = {}
    UISelectorList = d(packageName = packageName, clickable=True)
    for component in UISelectorList:
        componentList[component] = 'clickable'
    for component in componentList.keys():
        if componentList[component] == 'clickable' and component.exists:
            print(component.info)
            component.click()
            new = d.dump('temp.xml', compressed=False)
            print(current == new)
            if (current != new):
                print('here')
                traverse(pageNum + 1, resultFolder)
    d.press.back()


# In[79]:


traverse(1, '/Users/xikaioliver/Desktop/Result')


# In[65]:


packageName = 'com.fsck.k9'


# In[47]:


d(packageName = packageName, clickable=True)


# In[42]:


d.press('home')

