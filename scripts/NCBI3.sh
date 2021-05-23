#!/bin/bash
F_OUT="result_MM_Pubtator.txt"
F_LIST="PMID.txt"

echo -e "\n I am curating the result of MM. Jingbo\n"
echo -e "\n" >$F_OUT

i=1
while IFS= read -r line
do
	xx=`echo https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/pubtator?pmids=$line`
	curl $xx >>$F_OUT
	printf "$i -th result out of xxxxx is processing...\n"
	i=$[i+1]
	sleep 5.8s
done <"$F_LIST"
