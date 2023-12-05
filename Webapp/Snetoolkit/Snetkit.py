# -*- coding: utf-8 -*-
"""
For: UMR TETIS RESEARCH UNIT
Author: rodrique_kafando
"""
import sys
import pandas as pd
import nltk
import spacy
import json
from titlecase import titlecase
import os

from .src import params as params
from .src import utils as utils
from .src.disambiguate import Disambiguate as ds

nlp_enL = spacy.load('en_core_web_trf')

#########  geonames var
import geocoder



def delStrInStr(string: str, find: str, replace: str) -> str:
    temp = string.rsplit(find)
    return replace.join(temp).strip()


# extract spatial named entities from document
def spacySne(text):
    utils.manageDir()
    dc = params.nlp_model(text)
    # only LOC and GPE lables are used
    listOfSne = [str(ent) for ent in dc.ents if ent.label_ in  ['LOC' ,'GPE']]  # only consider GPE & LOC spatatial named entities
    prefix = 'the '
#     SneList = [string.lower()[string.lower().startswith(prefix) and len(prefix):].strip() for string in listOfSne]
    SneList = [titlecase(delStrInStr(string=string.lower(), find=prefix, replace='')) for string in listOfSne]
    SneList = [titlecase(st) for st in SneList]
    return SneList



def getCandidates(listOfSne:list,lang:str):
    """ 
    for each SNE extracted from the document, return its potential candidate
    @listOfSne: list of sne extracted from the document
    @lang: specify the language of the text
    @SameNameAs: list of candidate that have the same name as the input @sne in the for loop
    @NotAsSne: list of candidate that do not match exactly with the input @sne
    """
    SameNameAs = {}
    NotAsSne = {}
    for sne in listOfSne:
#         print('sne :', sne)
#         geo = geocoder.geonames(sne, key=key, maxRows=1000,featureClass=['A','P'], lang =lang) #,country=['GB']
        geo = geocoder.geonames(sne, key=params.key, maxRows=50,featureClass=['A','P'], lang =lang) #,country=['GB']

        Candidates = list(set([(r.address, r.lat, r.lng, r.country_code ,r.feature_class, r.population) for r in geo]))

        SneSet = list(set([sn[0] for sn in Candidates]))
        if len(SneSet) == 1 and  SneSet[0].lower()==sne.lower():
            SameNameAs[sne] = Candidates
        else:
            Candidates = [tuple(sn) for sn in Candidates]
            NotAsSne[sne] = Candidates
#         print(SameNameAs)
    return SameNameAs, NotAsSne

def longlistToJson(Llist, fil_name):
    path = "Snetoolkit/candidates/" + fil_name + '.json'
    with open(path, 'w') as fout:
    #with open('../defaultgeo/'+fil_anme + '.json', 'a') as fout:
        json.dump(Llist , fout)

def getCandidFromCorpora(corpora:str, out_fname, lang='en'):
	files_list = glob.glob(corpora)
	List = []
	doclist = []
	Final_AllSneCandidateD = []
	Final_NotAsSne = []
	AllSneCandidateD = {}
	for doc in files_list:
		doclist.append(doc)
		print(doc)
		fnamesrc = Path(doc).stem
		AllSneCandidateD[fnamesrc] = {}
		doc_data = read_txt(doc)
		SneList = spacySne(doc_data,params.nlp_enL)
		SneList = list(set(SneList))
		SameAsSne, NotAsSne = getCandidates(SneList,params.key,lang='en')

		AllSneCandidateD[fnamesrc]['assne'] = SameAsSne
		AllSneCandidateD[fnamesrc]['notassne'] = NotAsSne
	List.append(AllSneCandidateD)
	longlistToJson(List, out_fname)
	return doclist

def dicToDf(Dic:dict):
    df = pd.DataFrame(Dic.items())  
    
    columns=['name', 'lat', 'lng', 'Country Code', 'Type', 'Population']
    df[columns] = pd.DataFrame(df[1].tolist(), index=df.index)
    df = df[columns]
    return df

""" 
for each SNE extracted from the document, return its potential candidate
"""
def DefltCandidate(listOfSne:list,lang:str):
    AllSneCandidateD = {}
    for sne in listOfSne:
        geo = geocoder.geonames(sne, key= params.key, lang =lang) #,country=['GB']
        Candidates = list(set([(r.address, r.lat, r.lng, r.country_code ,r.feature_class, r.population) for r in geo]))
        if len(Candidates)>0:
            AllSneCandidateD[sne] = list(Candidates[0])
        else:
            pass
    df = dicToDf(AllSneCandidateD)
    return df 

def getCandidFromInputText_(input_text, lang='en'):
    SneList = spacySne(input_text)
    SneList = list(set(SneList))
    df = getDefltCandidate(SneList,lang)
    return df

def getDefltCand(SneList,  lang='en'):
    #SneList = spacySne(input_text,nlp_enL)
    SneList = list(set(SneList))
    df = DefltCandidate(SneList,lang)
    df.to_csv('./defaultgeocoding/defaultgeocoding.csv', index = None)
    return df


def MltCandidates(listOfSne:list, maxRows:int, lang:str):
    """ 
    for each SNE extracted from the document, return its potential candidate
    @listOfSne: list of sne extracted from the document
    @lang: specify the language of the text
    @SameNameAs: list of candidate that have the same name as the input @sne in the for loop
    @NotAsSne: list of candidate that do not match exactly with the input @sne
    """
    SameNameAs = {}
    NotAsSne = {}
    for sne in listOfSne:
        geo = geocoder.geonames(sne, key=params.key, maxRows=maxRows,featureClass=['A','P'], lang =lang) #,country=['GB']

        Candidates = list(set([(r.address, r.lat, r.lng, r.country_code ,r.feature_class, r.population) for r in geo]))

        SneSet = list(set([sn[0] for sn in Candidates]))
        if len(SneSet) == 1 and  SneSet[0].lower()==sne.lower():
            SameNameAs[sne] = Candidates
        else:
            Candidates = [tuple(sn) for sn in Candidates]
            NotAsSne[sne] = Candidates
#         print(SameNameAs)
    return SameNameAs, NotAsSne

def getMultiCand(SneList:str, out_fname, maxRows=5, lang='en'):
    List = []
    AllSneCandidateD = {}
    AllSneCandidateD['doc'] = {}
    #SameAsSne, NotAsSne = getCandidates_tobeexplored(key,SneList,lang='en')
    SameAsSne, NotAsSne = MltCandidates(SneList, maxRows, lang)

    AllSneCandidateD['doc']['assne'] = SameAsSne
    AllSneCandidateD['doc']['notassne'] = NotAsSne

    List.append(AllSneCandidateD)
    print("test within")
    longlistToJson(List, out_fname)
    print('Data saved in ./Candidates')
# 	return doclist

def applyDisamb(candidates_file, version_list =['f','fa','fas']):
    orig_stdout = sys.stdout
    f = open('Snetoolkit/logs/logs.txt', 'w')
    sys.stdout = f
    for v in version_list:
        desambiguated_df, NonAmbigusSne, toBeDesambAgain = ds(candidates_file, v)
        desambiguated_df.to_csv('Snetoolkit/disambiguated/'+'disambiguated'+v+'.csv', index = None)
        NonAmbigusSne.to_csv('Snetoolkit/disambiguated/NonAmbigusSne_'+v+'.csv', index = None)
        toBeDesambAgain.to_csv('Snetoolkit/remaining/toBeDisambAgain_'+v+'.csv', index = None)

    sys.stdout = orig_stdout
    print("logs saved to ./logs")
    f.close()
