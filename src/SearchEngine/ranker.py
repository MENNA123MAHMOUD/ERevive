import itertools
from re import L
import sys
# import threading
from .searchIndexer import *
from .joiner import *
# import globalVars
import os
import json
import timeit
import pickle
from .utilities import *
from gensim.models import KeyedVectors
from functools import lru_cache
import hoggorm as ho

global takenAttrs 
takenAttrs = set()
global takenEntities
takenEntities = set()

def getListQueries():
    listOfQueries=[]
    datapath = "../../dataset"
    files = os.listdir(datapath)
    for queryFile in files:
        if queryFile.find("synonyms")!=-1:
            continue
        with open(datapath+"/"+queryFile)as f:
            fileObj = json.load(f)
            for query in fileObj:
                if len(query["allQueries"])==1:
                    listOfQueries.extend(query["allQueries"])

    return listOfQueries
def load_model():
    glove_vectors = KeyedVectors.load("glove_vectors.model")
    return glove_vectors

def rankQueriesSimilarities(quiries_keywords,quiries,er):
    model = load_model()
    quiries_scores = []
    er_keys = []
    for keyword in er:
        try:
            er_keys.append(model.get_vector(keyword))
        except Exception as e:
            continue
    er = er_keys
    er_mat = np.array(er).T
    filtered_quiries=[]
    for idx,q in enumerate(quiries):
        query_keywords_init = quiries_keywords[idx]
        query_keywords = []
        for keyword in query_keywords_init:
            try:
                model_keyword = model.get_vector(keyword)
                query_keywords.append(model_keyword)
            except Exception as e:
                print(e)
                continue
        
        query_matrix = np.array(query_keywords).T
        query_out = ho.RVcoeff([query_matrix,er_mat])
        score = query_out[-1][0]
        if score>0.55:
            filtered_quiries.append(q)
            quiries_scores.append(score)


    quieries_scores_zip = list(zip(filtered_quiries,quiries_scores))

    quieries_score_zip = sorted(quieries_scores_zip,key=lambda x:x[1],reverse=True)  # sort by score
    return quieries_score_zip

@lru_cache(maxsize=None)
def mapEntity(entityKeywords,schemaEntityNames):
    #print("mapEntity",entity,schemaEntityNames)
    entityKeywordsSplit = cleanEntityName(entityKeywords)
    #if "song" in entityKeywords:
    #    print("mapEntity",entityKeywords,schemaEntityNames,entityKeywordsSplit)
    MaxMatchScore,MappedEntity  = 0,None
    for entity in schemaEntityNames:
        cleanName = cleanEntityName(entity)
        matchScore = getMatchScore(entityKeywordsSplit,cleanName)
        #if "song" in entityKeywords:
        #    print("scores",entityKeywords,entity,entityKeywordsSplit,cleanName,matchScore,MaxMatchScore,MappedEntity)
        if matchScore > MaxMatchScore:
            MaxMatchScore = matchScore
            MappedEntity = [entity]
            MatchedWord = [cleanName]
        elif MaxMatchScore!=0 and matchScore == MaxMatchScore:
            MappedEntity.append(entity)
            MatchedWord.append(cleanName)
    if MappedEntity is not None:
        return (MappedEntity,MatchedWord,MaxMatchScore,entityKeywordsSplit)
    return None

def mapEntities(queryEntities,schemaEntityNames):
    global takenEntities
    mappedEntitesDict = {}
    mappedEntities = []
    for entityKeywords in queryEntities:
        EntityMatchData = mapEntity(entityKeywords,schemaEntityNames)
        if EntityMatchData is not None:
            for idx,MappedEntity in enumerate(EntityMatchData[0]):
                if MappedEntity not in takenEntities:
                    takenEntities.add(MappedEntity)
                    mappedEntitesDict[entityKeywords] = MappedEntity
                    mappedEntities.append((MappedEntity,EntityMatchData[1][idx],EntityMatchData[2],EntityMatchData[3]))
                    break
    return mappedEntitesDict,mappedEntities


def getMatchScore(queryWords,schemaWords):
    # matchedWords / max(len(queryWords),len(schemaWords))
    queryVector = getKeyWordsVector(queryWords)
    schemaVector = getKeyWordsVector(schemaWords)
    matchCount = np.dot(queryVector.T, schemaVector)
    matchScore = matchCount[0][0]/max(len(queryWords),len(schemaWords))
    return matchScore

def constructDictionary(schema):
    entityDict = {}
    for key in schema.keys():
        entityDict[schema[key]["TableName"]] = key
    return entityDict

def ifWordInWord(word_one,word_two):
    if word_one in word_two or word_two in word_one: 
        return True
    elif abs(len(word_one)-len(word_two))<=2 and len(word_one)>=2 and len(word_two)>=2 and word_one[0:2]==word_two[0:2]:
        if word_one[:-1] in word_two or word_two[:-1] in word_one\
            or word_one[:-2] in word_two or word_two[:-2] in word_one or word_one[:-1] in word_two[:-1] or word_two[:-1] in word_one[:-1]\
            or word_one[:-2] in word_two[:-2] or word_two[:-2] in word_one[:-2]:
            return True
    return False
@lru_cache(maxsize=None)
def mapAttrEntity(entityAttributes, attribute):
    MaxMatchScore,MatchedWord  = 0,None
    for attr in entityAttributes:
        cleaned_attr = cleanEntityName(attr)
        matchScore = getMatchScore(attribute,cleaned_attr)
        if matchScore > MaxMatchScore:
            MaxMatchScore = matchScore
            MatchedWord = [attr]
        elif MaxMatchScore!=0 and matchScore == MaxMatchScore:
            MatchedWord.append(attr)
    if MatchedWord is not None:
        return (MatchedWord,MaxMatchScore)

    MaxMatchScore,MatchedWord  = 0,None
    for attr in entityAttributes:
        cleaned_attr = cleanEntityName(attr)
        dominator = max(len(cleaned_attr),len(attribute))
        attr_score = 0
        for word in attribute:
            for other_word in cleaned_attr:
                if ifWordInWord(word,other_word):
                    attr_score += 1/dominator
                    break
        if attr_score > MaxMatchScore:
            MaxMatchScore = attr_score
            MatchedWord = [attr]
        elif MaxMatchScore!=0 and attr_score == MaxMatchScore:
            MatchedWord.append(attr)
    if MatchedWord is not None:
        return (MatchedWord,MaxMatchScore)            
    return None,0


def mapAttr(entities , attribute , entityDict, schema,origAttribute):
    global takenAttrs
    attribute = cleanEntityName(attribute)
    MaxMatchScore,Matched  = 0,None
    for entityName in entities:
        idx = entityDict[entityName]
        entityAttributes = tuple(schema[idx]["attributes"].keys())
        attr,matchScore = mapAttrEntity(entityAttributes,tuple(attribute))
        if matchScore > MaxMatchScore:
            MaxMatchScore = matchScore
            Matched = [(attr,entityName)]
        elif MaxMatchScore!=0 and matchScore == MaxMatchScore:
            Matched.append((attr,entityName))

    if Matched is not None:
        for attrs,MatchedEntityName in Matched:
            for MatchedWord in attrs:
                if MatchedWord not in takenAttrs:
                    if type(attribute) is list and attribute[0] == "*":
                        return (MatchedEntityName,"*",0,"*","*",None)
                    idx = entityDict[MatchedEntityName]
                    dtype = schema[idx]["attributes"][MatchedWord]
                    takenAttrs.add(MatchedWord)
                    MatchedWord = "*" if attribute == "*" else MatchedWord
                    return (MatchedEntityName,MatchedWord,MaxMatchScore,attribute,origAttribute,dtype) 

    return None


def getAllAttributes(query):
    attrKeys = ['selectAttrs','groupByAttrs']
    attrKeysAggr = ['orderByAttrs','aggrAttrs','havingAttrs']
    attributes = set()
    for key in query.keys():
        if query[key] == []:
            continue
        #print(key,query[key])
        if key in attrKeys:
            attributes.update(set(query[key]))
        elif key in attrKeysAggr:
            zipIndex = 1 if key =="havingAttrs" else 0
            attNames = set(list(zip(*query[key]))[zipIndex])
            #print(key,attNames)
            attributes.update(attNames)
        elif key == 'whereAttrs':
            whereAttributes = [[atr[0],atr[2]] if atr[2]!="value" else [atr[0]]  for atr in query[key]]
            attNames = set(flattenList(whereAttributes))
            attributes.update(attNames)
    return attributes


def mapToSchema(schemaGraph,query,schema,entityDict,schemaEntityNames):
    ##################Remember mapped Entities
    initSchemaGraph(schemaGraph)
    #test_entities= ["department", "location"]
    #query_entities = query['entities']

    mappedEntitesDict,mappedEntities = mapEntities(tuple(query['entities']),tuple(schemaEntityNames))
   
    mappedEntitesNames = [ v for k,v in mappedEntitesDict.items()]
    #mappedEntitesNames = ["players","teams","coaches","awards_coaches"]
    start = timeit.default_timer()
    bestJoin , goals = connectEntities(tuple(mappedEntitesNames))
    #if len(query_entities)==2 and query_entities[0]=="department" and query_entities[1]=="location":
    #    print("query AHO: ",query , "mapedEntitesDict: ",mappedEntitesDict , "mappedEntities: ",mappedEntities, "bestJoin: ",bestJoin, "goals: ",goals)

    #print(mappedEntitesNames)
    #print(bestJoin,goals,mappedEntitesNames)
    end = timeit.default_timer()
    
    '''
    select s.name , s.age , a.name , a.age , a.address
    from student s , address a

    mapAttr([student],[name,age])
    mapAttr([address],[name,age,address])

    check for . if true
    same entity => in search
    if successful => break
    if not
        entities in mapped => if successful => break
        if not:
            entities goals_joins => if successful => break
            if not:
                search => schema if successful => break
                if not return None
    '''
    
    mappedAttributes = []
    attributes = getAllAttributes(query)

    for attribute in attributes:

        origAttribute = attribute
        goals_copy = goals.copy()
        schemaEntities = {schema[idx]["TableName"] for idx in schema.keys()}

        if attribute[0] == "*":
            mappedAttributes.append((None,"*",0,attribute[0],attribute[0],None))
            continue


        #level 1
        if '.' in attribute:
            entity = attribute.split('.')[0]
            attribute = attribute.split('.')[1]

            if entity in mappedEntitesDict.keys(): 
                entity = mappedEntitesDict[entity]
                if attribute[0] == "*":
                    if len(query['entities']) == 1: entity = None
                    mappedAttributes.append((entity,"*",0,attribute[0],origAttribute,None))
                    continue

                mapping = mapAttr([entity],attribute,entityDict,schema,origAttribute)
                if mapping is not None:
                    if type(mapping[3]) is list and mapping[3][0] == "*":
                        mapping = (mapping[0],mapping[3][0],mapping[2],mapping[3][0],origAttribute,mapping[4])
                    mappedAttributes.append(mapping)
                    continue

            #else: print(f"This Alias entity '{entity}' did not exist {mappedEntitesDict} xx {query['entities']} xx {attribute}")
            goals_copy.discard(entity) #discard searched entity
            schemaEntities.discard(entity) #discard searched entity
          
        #level 2
        entities = {entity for _,entity in mappedEntitesDict.items()}
        mapping = mapAttr(entities,attribute,entityDict,schema,origAttribute)
        if mapping is not None:
            if type(mapping[3]) is list and mapping[3][0] == "*":
                mapping = (mapping[0],mapping[3][0],mapping[2],mapping[3][0],origAttribute,mapping[4])
            mappedAttributes.append(mapping)
            continue
        goals_copy = goals_copy - entities 
        schemaEntities = schemaEntities - entities

        #level 3
        mapping = mapAttr(goals_copy,attribute,entityDict,schema,origAttribute)
        if mapping is not None:
            if type(mapping[3]) is list and mapping[3][0] == "*":
                mapping = (mapping[0],mapping[3][0],mapping[2],mapping[3][0],origAttribute,mapping[4])
            mappedAttributes.append(mapping)
            continue
        #schemaEntities = schemaEntities - goals_copy

        # level 4
        # TO BE DISCUSSED
        # mapping = mapAttr(schemaEntities,attribute,entityDict,schema)
        # if mapping is not None:
        #     mappedAttributes.append(mapping)
        #     continue

        mappedAttributes.append((None,None,0,attribute,origAttribute,None))

    global takenAttrs
    takenAttrs = set()

    global takenEntities
    takenEntities = set()

    #goals.update(set(mappedEntitesNames))
    # global bazetCount
    # print("bazetCount",bazetCount)
    return mappedEntities,mappedAttributes,goals,mappedEntitesDict,bestJoin

def queryCoverage(mappedAttributes):
    found = sum([1 for entity,_,_,_,_,_ in mappedAttributes if entity is not None])
    attributesMapped = max(len(mappedAttributes),1)
    return found/attributesMapped

def queryCompactness(mappedEntitiesDict,goals):
    mappedEntites = max(len(goals) ,1)
    compactness = len(mappedEntitiesDict)/mappedEntites
    return compactness

################get final query hits#################
def getNonZeroQueryHits(queryHits):
    nonZeroQueryHits = [ idx for idx,q in enumerate(queryHits) if q!=0]
    return nonZeroQueryHits


def flatten_query_entities(listOfQueries):
    flattened_query_entities = []
    for query in listOfQueries:
        entities = []
        for entity in query['entities']:
            entities.extend(entity.split("_"))
        flattened_query_entities.append(entities)
    return flattened_query_entities

def loadNgramsPickle():
    with open('nGrams/ngrams.pickle', 'rb') as handle:
        ngrams = pickle.load(handle)
    with open('nGrams/unigram.pickle', 'rb') as handle:
        unigram = pickle.load(handle)
    return ngrams,unigram
def loadEntitiesGrams():
    with open('nGrams/entities.pickle', 'rb') as handle:
        entitiesGrams = pickle.load(handle)
    return entitiesGrams
def getBestCombination(ngrams,entities):
    entitiesOneHotVector=[]
    for entity in list(set(entities)):
        entity = entity.split("_")
        entity = [get_lemma(word) for word in entity]
        entityOneHotVector = (getKeyWordsVector(entity)).tostring()
        entitiesOneHotVector.append(entityOneHotVector)
    best_combination = None
    best_combination_key = None
    len_best_combination = 0
    for r in range(len(entitiesOneHotVector)+1):
        for combination in itertools.combinations(entitiesOneHotVector, r):
            combination_key = np.array(list(combination)).tostring()
            if  combination_key in ngrams["whereAtrrsDict"] and len(list(combination)) > len_best_combination:
                best_combination = combination
                best_combination_key = combination_key
                len_best_combination = len(list(combination))
    return best_combination,best_combination_key
def getAttrsProps(attributes,type,query,ngrams,unigram):
    for attr in list(set(attributes)):
        if attr.find(".") != -1:
            attr = attr.split(".")[1]
        attr = attr.split("_")
        attr = [get_lemma(word) for word in attr]
        attrOneHotVector = (getKeyWordsVector(attr)).tostring()   
        if ngrams.get(attrOneHotVector):         
            query[type] += ngrams[attrOneHotVector]
        elif unigram.get(attrOneHotVector):
            query[type] += unigram[attrOneHotVector]
def rankCluster(cluster,queries,ngrams,unigram):
    cluster_queries=[]
    for idx in cluster:
        query = queries[idx]
        query['whereScore']=0
        query['selectScore']=0
        best_combination,best_combination_key = getBestCombination(ngrams,query['entities'])
        if best_combination==None:
            best_combination,best_combination_key = getBestCombination(ngrams,list(query['mappedEntitesDict'].keys()))
        whereAttrsNgrams = ngrams["whereAtrrsDict"][best_combination_key]
        selectAttrsNgrams = ngrams["selectAttrsDict"][best_combination_key]
        whereAttrs = [[atr[0][0],atr[2][0]] if atr[2]!="value" else [atr[0][0]]  for atr in query["whereAttrs"]]
        whereAttrs = flattenList(whereAttrs)
        selectAttrs = [ atr[0]  for atr in query["selectAttrs"] ]
        getAttrsProps(whereAttrs,"whereScore",query,whereAttrsNgrams,unigram["whereAtrrsDict"]) 
        getAttrsProps(selectAttrs,"selectScore",query,selectAttrsNgrams,unigram["selectAttrsDict"])
        cluster_queries.append(query)
    sorting_lambda = lambda q: (-1*len(q["goals"]),-1*q["entities_closeness"] ,q["attributes_coverage"] +q["entities_coverage"],q["whereScore"],q["selectScore"])
    cluster_queries.sort(key=sorting_lambda,reverse=True)
    cluster_queries = list(cluster_queries)
    max_num = min(20,len(cluster_queries))
    cluster_queries = cluster_queries[:max_num]
    return cluster_queries

def rankTopk(ranked_queries,maxNumOfQueries):
    entitiesGrams = loadEntitiesGrams()
    maxClusterScore = 0
    top_ranked_queries = []
    for ranked_query in ranked_queries:
        if len(ranked_query)<10:
            top_ranked_queries.append({'len':len(ranked_query),'score':1,'queries':ranked_query})
            continue
        entities = list(set(ranked_query[0]['entities']))
        cluster_score = 0
        reversedMappedEntitesDict = {value:key for key,value in ranked_query[0]['mappedEntitesDict'].items()}
        for entity in entities: 
            mappedEntity = reversedMappedEntitesDict[entity]
            entity = entity.split("_")
            mappedEntity = mappedEntity.split("_")
            entityOneHotVector = (getKeyWordsVector(entity)).tostring()
            mappedEntityOneHotVector = (getKeyWordsVector(mappedEntity)).tostring()
            if entitiesGrams.get(entityOneHotVector):
                cluster_score += entitiesGrams[entityOneHotVector]
            elif entitiesGrams.get(mappedEntityOneHotVector):
                cluster_score += entitiesGrams[mappedEntityOneHotVector]
        top_ranked_queries.append({'len':len(ranked_query),'score':cluster_score,'queries':ranked_query})
        if cluster_score > maxClusterScore:
            maxClusterScore = cluster_score

    maxClusterScore = max(1,maxClusterScore)
    for cluster in top_ranked_queries:
        if len(cluster["queries"])<10:
            continue
        cluster['score'] = float(cluster['score'])/maxClusterScore
        top_k = int(cluster['score']*maxNumOfQueries)
        cluster['queries'] = cluster['queries'][:top_k]
        cluster['len'] = len(cluster['queries']) 
    return top_ranked_queries
def getRankedQueries(clusters,queries):
    ngrams,unigram = loadNgramsPickle()
    ranked_queries = []
    #clustersLength=[]
    for cluster in clusters:
        ranked = rankCluster(cluster,queries,ngrams,unigram)
        ranked_queries.append({'len':len(ranked),'queries':ranked})
    #maxNumOfQueries = max(clustersLength)
    #ngrams,unigram = {},{}
    #ranked_queries = rankTopk(ranked_queries,maxNumOfQueries)
    return ranked_queries
    

##############
#ngeb 2l ngrams for select attributes , where attributes
#nsort by sum of the propapility of where attributes
#nsort by sum of the propapility of select attributes
############## TO Do
#validate the output query , where condition , nrun 2l query we n4of lw feh 2y errors
