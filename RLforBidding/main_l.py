
# coding: utf-8

# In[1]:


from config import *
from rlb_s import *


# In[2]:


log_in = open("../large_bid_performance/T={}_T0={}_C0={}.txt".format(T, T0, C0), "w")
log = "{:<42}  {:<8}  {:<10}  {:<5}  {:<9}  {:>9}  {:>8}  {:>8}".format(
        "setting","auction", "impression", "click", "cost", "win-rate", "CPM", "eCPC")
print(log)
log_in.write(log + "\n")


for camp in CAMPS:
    camp_info = get_camp_info(camp)
    rlb = rlb_s(camp_info)
    setting = "camp={},T={},T0={},C0={}".format(camp, T, T0, C0)
    bid_log_path = "../large_bid_performance/bid_log/" + camp + "_T={}_T0={}_C0={}.txt".format(T, T0, C0)
    
    #计算V 存入文件
    value_path = "../large_bid_performance/bid_model/" + camp + "_T0={}_c0={}_value.txt".format(T0, C0)
    dtb_path = "../large_bid_performance/bid_model/" + camp + "_T0={}_c0={}_dtb.txt".format(T0, C0)
    rlb.calc_optimal_value_function(value_path)
    rlb.v2d(value_path, dtb_path)
    
    auction_info = open(DATA_PATH + camp + "/test.theta.txt", "r")
    rlb.load_dtb_function(dtb_path)
    (auction, imp, clk, cost) = rlb.run(auction_info, bid_log_path, True)
    
    win_rate = imp / auction * 100
    cpm = (cost / 1000) / imp * 1000  #千次展示费用 费用单位 千
    ecpc = (cost / 1000) / clk  #单次点击成本  费用单位 千
    log = "{:<42}  {:<8}  {:<10}  {:<5}  {:<9}  {:>8.2f}%  {:>8.2f}  {:>8.2f}".format(
        setting, auction, imp, clk, cost, win_rate, cpm, ecpc)
    print(log)
    log_in.write(log + "\n")
log_in.flush()
log_in.close()
    
    
    

