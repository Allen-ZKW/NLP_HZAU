datapath = '../data/'
PMID = []
with open(datapath + 'abstract.json',encoding='utf-8') as f:
    for row in f:
        if 'PMID' in row:
            PMID.append(row.split(':')[1].split('[')[0].strip())
with open(datapath + 'PMID.txt','w') as f:
    for i in PMID:
        f.write(i+'\n')