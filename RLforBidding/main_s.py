
# coding: utf-8

# In[1]:


from config import *
from rlb_s import *


# In[2]:


#日志文件记录结果
log_in = open("../bid_performance/T={}_C0={}_v2.txt".format(T, C0), "w")
log = "{:<32}   {:<8}   {:<10}   {:<8}   {:<9}   {:>9}   {:>8}   {:>8}".format(
        "setting","auction", "impression", "click", "cost", "win-rate", "CPM", "eCPC")
print(log)
log_in.write(log + "\n")
    
for camp in CAMPS:
    camp_info = get_camp_info(camp)
    rlb = rlb_s(camp_info)
    setting = "camp={},T={},C0={}".format(camp, T, C0)
    bid_log_path = "../bid_performance/bid_log/" + camp + "_T={}_c0={}_v2.txt".format(T,C0)
    
    #计算V 存入文件
    value_path = "../bid_performance/bid_model/" + camp + "_T={}_c0={}.txt".format(T,C0)
    rlb.calc_optimal_value_function(value_path)
    
    auction_info = open(DATA_PATH + camp + "/test.theta.txt", "r")
    rlb.load_value_function(value_path)
    (auction, imp, clk, cost) = rlb.run(auction_info, bid_log_path)
    
    win_rate = imp / auction * 100
    cpm = (cost / 1000) / imp * 1000  #千次展示费用 费用单位 千
    ecpc = (cost / 1000) / clk  #单次点击成本  费用单位 千
    log = "{:<32}   {:<8}   {:<10}   {:<8}   {:<9}   {:>8.2f}%   {:>8.2f}   {:>8.2f}".format(
        setting, auction, imp, clk, cost, win_rate, cpm, ecpc)
    print(log)
    log_in.write(log + "\n")
log_in.flush()
log_in.close()
    

