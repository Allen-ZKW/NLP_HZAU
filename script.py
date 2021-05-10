from wordcloud import WordCloud
import imageio
import csv
import jieba 

def batchdel(tar_list,del_list):#functions to delete batch of data
    for i in sorted(del_list,reverse=True):
        del tar_list[i]
    return tar_list

def importdata(filename,dirpath):
    word_freq = []
    word_list = []
    csv_reader = csv.reader(open(dirpath+filename))
    for row in csv_reader:
        word_freq.append((row[0],int(row[1])))
        word_list.append(row[0])
    return word_freq,word_list

def cross(AGAC_freq,AGAC_list,GENIA_freq,GENIA_list):
    cross_freq = []
    AGAC_del = []
    GENIA_del = [] 
    cross_list = list(set(AGAC_list)&set(GENIA_list))
    for word in cross_list:
        freq = AGAC_freq[AGAC_list.index(word)][1] + GENIA_freq[GENIA_list.index(word)][1]
        cross_freq.append((word,freq))
        AGAC_del.append(AGAC_list.index(word))
        GENIA_del.append(GENIA_list.index(word))
    AGAC_freq = batchdel(AGAC_freq,AGAC_del)
    GENIA_freq = batchdel(GENIA_freq,GENIA_del)
    return AGAC_freq,GENIA_freq,cross_freq

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
    wc.to_file('wc'+pngname)

def main():
    dirpath = "D:/junior_n/NLP/task_2/"
    AGAC_freq,AGAC_list = importdata("AGAC_freq.csv",dirpath)
    GENIA_freq,GENIA_list = importdata("genia_freq.csv",dirpath)
    drawcloud(GENIA_freq,"GENIA.png",dirpath)
    drawcloud(AGAC_freq,"AGAC.png",dirpath)
    AGAC_freq,GENIA_freq,cross_freq = cross(AGAC_freq,AGAC_list,GENIA_freq,GENIA_list)
    drawcloud(GENIA_freq,"GENI.png",dirpath)
    drawcloud(AGAC_freq,"GAC.png",dirpath)
    drawcloud(cross_freq,"A.png",dirpath)
main()