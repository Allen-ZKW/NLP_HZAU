# -*- coding: utf-8 -*-

"""
Created on Tus Apr 13 18:48:04 2021

@author: Ke-Wei Zhao
"""

import re
import csv
import json
import jieba 
import spacy
import string
import imageio
from scipy import stats
import seaborn as sns
import networkx as nx
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import defaultdict

def create_dictionary(dirpath):#function to find synonm, name in TO file and build a dictionary for these
    datapath = dirpath + 'data/'
    dictionary = []
    standard_dic = {}
    with open(datapath + '/RTO-1.0.txt','r',encoding = 'utf-8') as f:
        for row in f:
            buffer = row.split(':')
            if buffer[0] == 'name':
                word = buffer[1].strip()
                record = word
                dictionary.append(word)
                standard_dic[word] = word
            elif buffer[0] == 'synonym':
                word = buffer[1].split('"')[1]
                word = word.split(' (')[0].strip()
                standard_dic[word] = record
                dictionary.append(word)
    dictionary = list(set(dictionary))
    '''    
    with open(datapath + '/TO_dictionary.txt','w') as f:
        for i in dictionary:
            f.write(i + '\n')
    with open(datapath + '/TO_sd.txt','w') as f:
        for i in standard_dic:
            f.write(i + '\n')
    ''' 
    return dictionary,standard_dic

def pubtator_reader(dirpath):#function to read and classify pubtator infromation
    datapath = dirpath + 'data/'
    p_d = {}
    with open(datapath + 'result_MM_Pubtator.txt','r',encoding='utf-8') as f:
        for row in f:
            if '|t|' in row:
                key = row.split('|t|')[0]
                title = row.split('|t|')[1].strip()+' '
                p_d[key] = {}
                p_d[key]['paper'] = title
                p_d[key]['annotation'] = []
            elif '|a|' in row:
                key = row.split('|a|')[0]
                abstract = row.split('|a|')[1].strip()+' '
                p_d[key]['paper'] = p_d[key]['paper'] + abstract
                start = [0]
                stop = []
                for i in range(len(p_d[key]['paper'])):
                    if p_d[key]['paper'][i:i+2] == '. ':
                        stop.append(i+2)
                        start.append(i+2)
                del start[-1]
                sentence = []
                for i in range(len(start)):
                    sentence.append([start[i],stop[i]])
                p_d[key]['sentence'] = sentence
            elif row != '\n':
                note = row.strip().split('\t')
                if note[4] == 'Gene':
                    p_d[key]['annotation'].append(note)
    '''
    e = json.dumps(p_d)
    with open(datapath + 'pubtator_data.json','w') as f:
        f.write(e)
    '''
    grpd = {}
    for key in p_d.keys():
        if p_d[key]['annotation'] != []:
            grpd[key] = p_d[key]
    return grpd

def include(sentence,annotation):#function to renturn a relationship of sentence and gene annotation
    if sentence[0] <= int(annotation[1]) and sentence[1] >= int(annotation[2]):
        return True
    else:
        return False

def abstract_sentence(grpd):#function to find all sentence which include gene annotation
    grsd = {}
    for key in grpd.keys():
        for sentence in grpd[key]['sentence']:
            for annotation in grpd[key]['annotation']:
                if include(sentence,annotation) == True:
                    start = sentence[0]
                    end = sentence[1]
                    co = grpd[key]['paper'][start:end]
                    if co not in grsd.keys():
                        grsd[co] = [annotation[3]]
                    else:
                        grsd[co].append(annotation[3])
    return grsd

def concordance(target):
    del_set = set()
    for i in target:
        for j in target:
            if i in j and i != j:
                del_set.add(i)
    if del_set == set():
        return target
    else:
        for i in del_set:
            target.remove(i)
        return target

def TO_match(dirpath,grsd,dictionary,special_TO):#function to match TO in these sentences 
    datapath = dirpath + 'data/'
    gts = {}
    for key in grsd.keys():
        gts[key] = {}
        gts[key]['GO'] = grsd[key]
        gts[key]['TO'] = []
        pure_sentence = key.translate(str.maketrans('', '', string.punctuation)).lower()
        for TO in dictionary:
            if TO not in special_TO:
                pure_TO = TO.translate(str.maketrans('', '', string.punctuation)).lower()
                pattern = re.compile('\\b' + pure_TO + '\\b')
                m = re.search(pattern,pure_sentence)
                if m != None:
                    gts[key]['TO'].append(TO)
            else:
                pure_sentence = key.translate(str.maketrans('', '', string.punctuation))
                pure_TO = TO.translate(str.maketrans('', '', string.punctuation))
                pattern = re.compile('\\b' + pure_TO + '\\b')
                m = re.search(pattern,pure_sentence)
                if m != None:
                    gts[key]['TO'].append(TO)
    key_list = list(gts.keys())
    for key in key_list:
        if gts[key]['TO'] == []:
            del gts[key]
        else:
            gts[key]['GO'] = list(set(gts[key]['GO']))
            gts[key]['TO'] = concordance(gts[key]['TO'])
    '''
    e = json.dumps(gts)
    with open(datapath + 'gts_pro.json','w') as f:
        f.write(e)
    '''
    return gts

def dependency_tree(gts,dirpath):
    datapath = dirpath + 'data/'
    nlp = spacy.load('en_core_web_sm')
    for key in gts.keys():
        sentence = key
        num =1
        for i in gts[key]['GO']:
            sentence = sentence.replace(i,'GO'+str(num))
        num = 1
        for i in gts[key]['TO']:
            sentence = sentence.replace(i,'TO'+str(num))
        word_pos_dict = {}
        doc = nlp(sentence)
        for token in doc:
            word_pos_dict[token.dep_] = token.text
        gts[key]['depency_result'] = word_pos_dict
    '''
    e = json.dumps(gts)
    with open(datapath + 'gtsd.json','w') as f:
        f.write(e)
    '''
    return gts

def GT_net(gts,standard_dic,dirpath):
    datapath = dirpath + 'data/'
    G = nx.Graph()
    for key in gts:
        T_nodes = []
        G_nodes = gts[key]['GO']
        for j in gts[key]['TO']:
            T_nodes.append(standard_dic[j])
        T_nodes = list(set(T_nodes))
        for a in T_nodes:
            for b in G_nodes:
                if (a,b) not in G.edges:
                    G.add_edge(a,b,freq=1)
                else:
                    for i in G.edges(data=True):
                        if i[0]==a or i[1]==b:
                            G.add_edge(a,b,freq=i[2]['freq']+1)
                        if i[0]==b or i[1]==a:
                            G.add_edge(a,b,freq=i[2]['freq']+1)
    '''
    with open(datapath + 'network.csv','w') as f:
        fwriter = csv.writer(f)
        for i in G.edges(data=True):
            fwriter.writerow([i[0],i[1],i[2]['freq']])
    '''
    return G

def degree(G):
    freq_list = []
    for node in G.nodes:
        freq = 0
        for edge in G.edges(data=True):
            if edge[0] == node or edge[1] == node:
                freq += edge[2]['freq']
        freq_list.append(freq)
    return freq_list

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

def drawcloud(word_freq,pngname,dirpath):
    text=''
    for i in word_freq:
        text = text + (i[0]+' ')*i[1]
    cut = jieba.cut(text)
    string = ' '.join(cut)
    color_mask =imageio.imread(dirpath+pngname)
    wc = WordCloud(
                background_color="white",
                collocations=False,
                mask=color_mask) 
    wc.generate(string)
    wc.to_file(dirpath+'wc'+pngname)

def create_corpus(gts,dirpath):
    datapath = dirpath + 'data/'
    with open(datapath + 'co_corpus.txt','w') as f:
        for key in gts.keys():
            f.write(key+'\n')

def wordcloud(dirpath,filename,pngname):
    word_freq = []
    csv_reader = csv.reader(open(dirpath+filename))
    for row in csv_reader:
        word_freq.append((row[0],int(row[1])))
    text=''
    for i in word_freq:
        text = text + (i[0]+' ')*i[1]
    cut = jieba.cut(text)
    string = ' '.join(cut)
    color_mask =imageio.imread(dirpath+pngname)
    wc = WordCloud(
                background_color="white",
                collocations=False,
                mask=color_mask) 
    wc.generate(string)
    wc.to_file(dirpath+'wc'+pngname)

def main():
    dirpath = "./"
    special_TO = ['BY','An']
    dictionary,standard_dic = create_dictionary(dirpath)
    grpd = pubtator_reader(dirpath)
    grsd = abstract_sentence(grpd)
    gts = TO_match(dirpath,grsd,dictionary,special_TO)
    gts = dependency_tree(gts,dirpath)
    G = GT_net(gts,standard_dic,dirpath)
    freq_list = degree(G)
    KdePlot(freq_list,"Kernel Density Plot of Ontology Freqence")
    create_corpus(gts,dirpath)
    wordcloud(dirpath,"word_freq.csv","稻.png")