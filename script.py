# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 19:57:00 2021

@author: Ke-Wei Zhao
"""

from random import shuffle
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt

def importdata(dirpath):
    
    genia_raw = []
    with open (dirpath + '/genia_pure.txt') as f1:
        for le in f1:
            l = le.strip()
            genia_raw.append(l)
    
    AGAC_raw = []
    with open (dirpath + '/train_pure.txt') as f2:
        for le in f2:
            l = le.strip()
            AGAC_raw.append(l)
    return genia_raw,AGAC_raw

def sampling(genia_raw,AGAC_raw):
    
    shuffle(genia_raw)
    genia_sample = genia_raw[0:30000]
    
    shuffle(AGAC_raw)
    AGAC_sample = AGAC_raw[0:3000]
    
    return genia_sample,AGAC_sample

def TTR(genia_sample,AGAC_sample):
    genia_TTR = len(set(genia_sample))/30000
    AGAC_TTR = len(set(AGAC_sample))/3000

    return genia_TTR,AGAC_TTR

def KdePlot(x,name):

    plt.rcParams['font.sans-serif'] = ['SimHei']   
    plt.rcParams['axes.unicode_minus'] = False

    plt.figure()
    sns.set(style='white', 
            font = 'SimHei')      
    sns.distplot(x,                 
                 color='orange',    
                 kde=True,          
                 hist=True,         
                 rug=True,          
                 kde_kws = {"shade": True,          
                            "color": 'darkorange',  
                            # 'linewidth': 1.0,     
                            'facecolor': 'gray'},   
                 rug_kws = {'color': 'red',         
                            'height': 0.1})         
                 # vertical = True)                 

    plt.title(name)               
    plt.xlabel('TTR')                 
    plt.ylabel('density')              
    plt.savefig(name+'.png', dpi=300)    
    plt.show()

def boxplot(genia_TTR,AGAC_TTR):
    plt.boxplot((genia_TTR,AGAC_TTR),labels=('genia_TTR','AGAC_TTR'))
    plt.savefig('box.png', dpi=300)   

def main():
    dirpath = 'D:/junior_n/自然语言处理/task_1'
    genia_raw,AGAC_raw = importdata(dirpath)
    genia_TTR = [0]*1000
    AGAC_TTR = [0]*1000
    for i in range(1000):
        genia_sample,AGAC_sample = sampling(genia_raw,AGAC_raw)
        genia_TTR[i],AGAC_TTR[i] = TTR(genia_sample,AGAC_sample)
    stats.normaltest (genia_TTR, axis=0)#正态性检验，可以不做
    stats.normaltest (AGAC_TTR, axis=0)#正态性检验，可以不做
    statistic, pvalue = stats.levene(genia_TTR,AGAC_TTR)#方差非齐性
    if pvalue < 0.05:
        stats.ttest_ind(genia_TTR, AGAC_TTR, equal_var=False)
    else:
        stats.ttest_ind(genia_TTR, AGAC_TTR, equal_var=True)
    KdePlot(genia_TTR,'Genia Corpus')
    KdePlot(AGAC_TTR,'AGAC Corpus')
    boxplot(genia_TTR,AGAC_TTR)