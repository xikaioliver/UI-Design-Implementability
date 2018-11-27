
# coding: utf-8

# In[4]:


import pandas as pd
import matplotlib.pyplot as plt
data = pd.read_csv("result_2.csv", sep=',')
data.rename(columns={'Unnamed: 0':'component'}, inplace = True)


# In[2]:


dict = {}
for i in range(data.shape[0]):
    key = data.iloc[i]['component'].partition('.')[0]
    if key in dict:
        dict[key] += data.iloc[i]['num']
    else:
        dict[key] = data.iloc[i]['num']


# In[3]:


statics = pd.DataFrame(dict, index=['num'])
# statics = statics.reset_index()
statics


# In[68]:


# statics.columns = ['type', 'num']
plt.figure(figsize=(5,5))
plt.pie(statics.iloc[0,:],radius=1,labels=statics.columns)
# plt.pie(data.iloc[1,:],radius=0.7,wedgeprops=dict(width=0.3,edgecolor='w'),colors=['r','g','b','y'])


# In[78]:


statics = statics.T.reset_index()
statics.columns = ['type', 'num']


# In[81]:


statics.sort_values(by = 'num',axis = 0,ascending = False)


# In[8]:


data.sort_values(by = ['num'],axis = 0,ascending = False)

