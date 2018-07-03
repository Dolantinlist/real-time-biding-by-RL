
# coding: utf-8

# In[1]:


import _pickle as pickle
import time


# In[2]:


DATA_PATH = "../ipinyou/"
CAMPS = ["1458", "2259", "2261", "2821","3358","3427","3476"]

UP_PRECISION = 1e-10
ZERO_PRECISION = 1e-12
MAX_PRICE = 300  #最大竞拍价
T = 50000  #每个episode的竞拍数
T0 = 1000  #V的计算范围
C0 = 1/32  #用来计算预算  每个episode的budget = CPM * T * C0


# In[3]:


#读出camp的统计信息
def get_camp_info(camp):
    info = pickle.load(open(DATA_PATH + camp + "/info.txt", "rb"))
    return info


# In[6]:


#计算竞标成功的价格δ的概率密度函数
def calc_m_pdf(m_counter, laplace = 1):
    m_pdf = [0] * len(m_counter)
    sum = 0
    for i in range(len(m_counter)):
        sum += m_counter[i]
    for i in range(len(m_counter)):
        m_pdf[i] = (m_counter[i] + laplace) / (sum + len(m_counter) * laplace)
    return m_pdf


# In[7]:


def get_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

