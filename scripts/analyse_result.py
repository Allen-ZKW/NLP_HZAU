import csv
import json
import jieba
import imageio
import networkx as nx
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def read_result(dirpath):
    datapath = dirpath + 'data/'
    with open(datapath+'gtsd.json') as f1:
        gts = json.load(f1)
    with open(datapath+'TO_sd.txt') as f2:
        standard_dic = json.load(f2)
    return gts,standard_dic

def relationship_fliter(gts,dirpath):
    datapath = dirpath + 'data/'
    resultpath = dirpath + 'result/'
    gts_fliter = {}
    for key in gts.keys():
        buffer = gts[key]['depency_result']
        if 'nsubjpass' in buffer.keys() and 'nsubj' in buffer.keys():
            if (buffer['nsubj'][0:2] == 'TO' or buffer['nsubj'][0:2] == 'GO' ) and (buffer['nsubjpass'][0:2] == 'TO' or buffer['nsubjpass'][0:2] == 'GO' ):
                gts_fliter[key] = {}
                gts_fliter[key]['GO'] = gts[key]['GO']
                gts_fliter[key]['TO'] = gts[key]['TO']
                gts_fliter[key]['depency_result'] = gts[key]['depency_result']
        elif 'nsubj' in buffer.keys() and 'dobj' in buffer.keys():
            if (buffer['nsubj'][0:2] == 'TO' or buffer['nsubj'][0:2] == 'GO') and (buffer['dobj'][0:2] == 'TO' or buffer['dobj'][0:2] == 'GO'):
                gts_fliter[key] = {}
                gts_fliter[key]['GO'] = gts[key]['GO']
                gts_fliter[key]['TO'] = gts[key]['TO']
                gts_fliter[key]['depency_result'] = gts[key]['depency_result']
        elif 'nsubjpass' in buffer.keys() and 'dobj' in buffer.keys():
            if (buffer['nsubjpass'][0:2] == 'TO' or buffer['nsubjpass'][0:2] == 'GO') and (buffer['dobj'][0:2] == 'TO' or buffer['dobj'][0:2] == 'GO'):
                gts_fliter[key] = {}
                gts_fliter[key]['GO'] = gts[key]['GO']
                gts_fliter[key]['TO'] = gts[key]['TO']
                gts_fliter[key]['depency_result'] = gts[key]['depency_result']
    strong_TG = {}
    for key_1 in gts_fliter.keys():
        strong_TG[key_1]=[]
        for key_2 in gts_fliter[key_1]['depency_result'].keys():
            if key_2=='nsubjpass' or key_2=='nsubj' or key_2=='dobj':
                if gts_fliter[key_1]['depency_result'][key_2][0:2] == 'TO' or gts_fliter[key_1]['depency_result'][key_2][0:2] == 'GO':
                    index = int(gts_fliter[key_1]['depency_result'][key_2][2])-1
                    if gts_fliter[key_1]['depency_result'][key_2][0:2]=='TO':
                        strong_TG[key_1].append('TO:'+gts_fliter[key_1]['TO'][index])
                    if gts_fliter[key_1]['depency_result'][key_2][0:2]=='GO':
                        strong_TG[key_1].append('GO:'+gts_fliter[key_1]['GO'][index])
    e = json.dumps(gts_fliter)
    with open(resultpath + 'gts_fliter.json','w') as f:
        f.write(e)
    return gts_fliter,strong_TG

def GT_net(gts,standard_dic,dirpath):
    resultpath = dirpath + 'data/'
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
    with open(resultpath + 'network.csv','w') as f:
        fwriter = csv.writer(f)
        for i in G.edges(data=True):
            fwriter.writerow([i[0],i[1],i[2]['freq']])
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

def KdePlot(x,name,dirpath):
    resultpath = dirpath + "result/"
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
    plt.xlabel('Degree')                 
    plt.ylabel('Density')              
    plt.savefig(resultpath+name+'.png', dpi=300)    
    plt.show()

def wordcloud(dirpath,filename,pngname):
    resultpath = dirpath + 'result/'
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
    wc.to_file(resultpath+'wc'+pngname)

def main():
    dirpath = "../"
    gts,standard_dic = read_result(dirpath)
    gts_fliter,strong_TG = relationship_fliter(gts,dirpath)
    wordcloud(dirpath,"word_freq.csv","稻.png")
    G = GT_net(gts,standard_dic,dirpath)
    freq_list = degree(G)
    KdePlot(freq_list,"Kernel Density Plot of Degree",dirpath)
main()