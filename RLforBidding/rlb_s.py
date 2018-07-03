
# coding: utf-8

# In[1]:


from config import *
import os


# In[2]:


class rlb_s:

    #在实际应用时 这种配置是否需要根据历史文件自动更新
    def __init__(self,camp_info):
        self.cpm = camp_info["cost_train"] / camp_info["imp_train"]
        self.theta_avg = camp_info["clk_train"] / camp_info["imp_train"]
        self.B0 = int(camp_info["cost_train"] / camp_info["imp_train"] * C0 * T0)
        self.B = int(camp_info["cost_train"] / camp_info["imp_train"] * C0 * T)
        self.cpc = camp_info["cost_train"] / camp_info["clk_train"]
        self.m_pdf = calc_m_pdf(camp_info["price_counter_train"])
        self.V = []
        self.D = []
    
    #计算V(t,b)
    def calc_optimal_value_function(self,model_path):
        if os.path.exists(model_path):
            return 0
        else:
            V = [0] * (self.B0 + 1)
            nV = [0] * (self.B0 + 1)
            V_inc = 0
            V_max = 0
            V_out = open(model_path, "w")
        
            #V_inc 出最高价，即a_max的情况下能得到的点击率期望
            for b in range(MAX_PRICE + 1):
                V_inc += self.m_pdf[b] * self.theta_avg
       
            #对于状态S(t,b)中的每个t
            for t in range(T0 - 1):
                a = [0] * (self.B0 + 1)
                bb = self.B0 - 1
                #计算a(t,b) 此时用到的V(b)其实是V(t-1,b)
                for b in range(self.B0, 0, -1):  
                    while bb >= 0 and (V[bb] - V[b]) + self.theta_avg >=0:
                        bb -= 1
                    if bb < 0:
                        a[b] = min(MAX_PRICE, b)  #能出价多少出多少
                    else:
                        a[b] = min(MAX_PRICE, b - bb - 1)
                
                #将V(t-1,b)写入文件
                for b in range(self.B0):
                    V_out.write("{}\t".format(V[b]))
                V_out.write("{}\n".format(V[self.B0]))
                
                #然后计算V(t,b)
                V_max += V_inc 
                for b in range(1, self.B0 + 1):
                    nV[b] = V[b]
                    for delta in range(0, a[b] + 1):
                        nV[b] += self.m_pdf[delta] * (self.theta_avg + V[b - delta] - V[b])
                
                    #如果当前b是取得最优结果的b(得到最优点击且不影响之后竞拍的点击量)，则当预算大于b时的Value也都取此值
                    if abs(nV[b] - V_max) < UP_PRECISION:
                        for bb in range(b + 1, self.B0 + 1):
                            nV[bb] = V_max
                        break
                V = nV[:]
        
            for b in range(0, self.B0):
                V_out.write("{0}\t".format(V[b]))
            V_out.write("{0}\n".format(V[self.B0]))
            
            V_out.flush()
            V_out.close()
                
    #将V从文件读到内存    
    def load_value_function(self, model_path):
        self.V = [[0 for i in range(self.B0 + 1)] for j in range(T0)]
        with open(model_path, "r") as fin:
            n = 0
            for line in fin:
                line = line[:len(line) - 1].split("\t")
                for b in range(self.B0 + 1):
                    self.V[n][b] = float(line[b])
                n += 1
                if n >= T0:
                    break
     
    
    #根据V算出D
    def v2d(self,v_path,d_path):
        if os.path.exists(d_path):
            return 0
        else:
            with open(v_path, "r") as fin:
                with open(d_path, "w") as fout:
                    for line in fin:
                        line = line[:len(line) - 1].split("\t")
                        nl = ""
                        for b in range(len(line) - 1):
                            d = float(line[b + 1]) - float(line[b])
                            if abs(d) < ZERO_PRECISION:
                                d = 0
                            if b == len(line) - 2:
                                nl += "{}\n".format(d)
                            else:
                                nl += "{}\t".format(d)
                        fout.write(nl)
     
    
    def load_dtb_function(self, model_path):
        self.D = [[0 for i in range(self.B0)] for j in range(T0)]
        with open(model_path, "r") as fin:
            n = 0
            for line in fin:
                line = line[:len(line) - 1].split("\t")
                for b in range(self.B0):
                    self.D[n][b] = float(line[b])
                n += 1
                if n >= T0:
                    break
                    
    #输入t,b,theta  决策竞标价格a                
    def bid_by_v(self, t, b, theta):
        a = 0
        for delta in range(1, min(b, MAX_PRICE) + 1):
            if theta + self.V[t - 1][b - delta] - self.V[t - 1][b] >= 0:
                a = delta
            else:
                break
        return a
    
     #输入t,b,theta  决策竞标价格a                
    def bid_by_d(self, t, b, theta):
        if t >= T0:
            return self.bid_by_d(T0 - 1, int(b / t * (T0 - 1)), theta)
        if b > self.B0:
            return self.bid_by_d(int(t / b * self.B0), self.B0, theta)
        a = 0
        value = theta
        for delta in range(1, min(b, MAX_PRICE) + 1):
            value -= self.D[t - 1][b - delta]
            if value >= 0:
                a = delta
            else:
                break
        return a
    
    #竞标
    def run(self, auction_info, log_path, large_scale = False):
        auction = 0
        imp = 0
        clk = 0
        cost = 0
        
        log_in = open(log_path, "w")
        log_in.write(get_time() + "\t{:<8}\t{:<8}\t{:<8}\t{:<8}\t{:<8}\t{:<8}\t{:<8}\t{:<8}\t\n".format(
                "episode", "b", "t", "a", "price", "click", "clk", "imp"))
        
        episode = 1
        t = T
        b = self.B
        for line in auction_info:
            line = line[:len(line)-1].split(" ")
            click = int(line[0])
            price = int(line[1])
            theta = float(line[2])
            
            if large_scale:
                a = self.bid_by_d(t, b, theta)
            else:
                a = self.bid_by_v(t, b, theta)
            
            #a = min(a, int(self.cpc * theta * 2))  
            #限制epsidode末的竞标花费
            
            log = get_time() + "\t{:<8}\t{:<8}\t{:<8}\t{:<8}\t{:<8}\t{:<8}\t{:<8}\t{:<8}\t".format(
                episode, b, t, a, price, click, clk, imp)
            log_in.write(log + "\n")
            
            if a >= price:
                imp += 1
                if click:
                    clk += 1
                b -= price
                cost += price
            t -= 1
            auction += 1
            
            if t == 0:
                episode += 1
                t = T
                b = self.B
                
        log_in.flush()
        log_in.close()
        
        return auction, imp, clk, cost

