# -*- coding: utf-8 -*-

"""
Created on Tus Apr 13 18:48:04 2021

@author: Ke-Wei Zhao
"""

import re
import json 
import spacy
import string
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
    with open(datapath + '/TO_dictionary.txt','w') as f:
        for i in dictionary:
            f.write(i + '\n')
    e = json.dumps(standard_dic)
    with open(datapath + '/TO_sd.txt','w') as f:
            f.write(e)
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
    e = json.dumps(p_d)
    with open(datapath + 'pubtator_data.json','w') as f:
        f.write(e)
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
    e = json.dumps(gts)
    with open(datapath + 'gts_pro.json','w') as f:
        f.write(e)
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
    e = json.dumps(gts)
    with open(datapath + 'gtsd.json','w') as f:
        f.write(e)
    return gts

def create_corpus(gts,dirpath):
    datapath = dirpath + 'data/'
    with open(datapath + 'co_corpus.txt','w') as f:
        for key in gts.keys():
            f.write(key+'\n')

def main():
    dirpath = "../"
    special_TO = ['BY','An']
    dictionary,standard_dic = create_dictionary(dirpath)
    grpd = pubtator_reader(dirpath)
    grsd = abstract_sentence(grpd)
    gts = TO_match(dirpath,grsd,dictionary,special_TO)
    gts = dependency_tree(gts,dirpath)
    create_corpus(gts,dirpath)

main()