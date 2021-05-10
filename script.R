library('devtools')
library(DOSE)
library(org.Hs.eg.db)
library(topGO)
library(clusterProfiler)
library(pathview)
MyGeneSet <- read.table('D:/junior_n/NLP/task_3/data/gene_result.csv')
MyGeneSet <- as.character(MyGeneSet$V1)
MyGeneIDSet <- bitr(MyGeneSet,
			 fromType="SYMBOL",
			 toType=c("ENSEMBL","ENTREZID", "GO"),
			 OrgDb="org.Hs.eg.db")
data(geneList, package="DOSE")

ego_ALL <- enrichGO(gene = MyGeneIDSet$ENTREZID, 
                    universe = names(geneList),
                    OrgDb = org.Hs.eg.db, 
                    ont = "ALL",
                    pAdjustMethod = "BH",
                    pvalueCutoff = 1, 
                    qvalueCutoff = 1,
                    readable = TRUE)

ego_MF <- enrichGO(gene = MyGeneIDSet$ENTREZID,
			 universe = names(geneList),
			 OrgDb = org.Hs.eg.db,
			 ont = "MF",
			 pAdjustMethod = "BH",
			 pvalueCutoff = 1,
			 qvalueCutoff = 1,
			 readable = TRUE)

ego_CC <- enrichGO(gene = MyGeneIDSet$ENTREZID,
			 universe = names(geneList),
			 OrgDb = org.Hs.eg.db,
			 ont = "CC",
			 pAdjustMethod = "BH",
			 pvalueCutoff = 1,
			 qvalueCutoff = 1,
			 readable = TRUE)

ego_BP <- enrichGO(gene = MyGeneIDSet$ENTREZID,
			 universe = names(geneList),
			 OrgDb = org.Hs.eg.db,
			 ont = "BP",
			 pAdjustMethod = "BH",
			 pvalueCutoff = 1,
			 qvalueCutoff = 1,
			 readable = TRUE)

dotplot(ego_MF,title="EnrichmentGO_MF_dot")
dotplot(ego_CC,title="EnrichmentGO_CC_dot")
dotplot(ego_BP,title="EnrichmentGO_BP_dot")

barplot(ego_MF, showCategory=20,title="EnrichmentGO_MF")
barplot(ego_CC, showCategory=20,title="EnrichmentGO_MF")
barplot(ego_BP, showCategory=20,title="EnrichmentGO_MF")

plotGOgraph(ego_MF,firstSigNodes = 10, useInfo = "all", sigForAll = TRUE,useFullNames = TRUE)
plotGOgraph(ego_CC,firstSigNodes = 10, useInfo = "all", sigForAll = TRUE,useFullNames = TRUE)
plotGOgraph(ego_BP,firstSigNodes = 10, useInfo = "all", sigForAll = TRUE,useFullNames = TRUE)
