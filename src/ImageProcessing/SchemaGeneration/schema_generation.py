import cv2
from numpy.core.defchararray import count
from skimage.morphology import skeletonize
import numpy as np
from math import sqrt
from ..remove_lines import *



def generateSchema(entites , relations , shapes_no):
    schema = {}
    multivaluedWeak = {}
    #strong and weak without full primary key
    for e in entites: 
        schema[e["idx"]] = {
            "TableName": e['name'],
            "attributes":{},
            "primaryKey":[],
            "ForgeinKey":[],
            "isWeak":e['isWeak']
        }

        #multivaled table
        multivalued = addAtrributesAndPrimaryKey(schema[e["idx"]],e['attributes'])
        if e["isWeak"]:
            multivaluedWeak[e["idx"]] = multivalued
        else:
            addMultivaluedTable(schema,multivalued,shapes_no,schema[e["idx"]])
            shapes_no+=len(multivalued)

        #loop on relations and add attributes
        addRelationsAttributes(e["relations"] , relations)

    #add weak keys
    for e in entites:
        if(e["isWeak"]):
            addCompositeKey(schema[e["idx"]],e["idx"],e["relations"],relations,schema)
            addMultivaluedTable(schema,multivaluedWeak[e["idx"]],shapes_no,schema[e["idx"]])
            shapes_no+=len(multivaluedWeak[e["idx"]])  

    for r in relations.values():
        if r["isIdentitfying"]:
            continue
        if len(r["entities"])>2:
            ##nary and NM relation
            shapes_no += 1
            addEntitiesAsTables(r["name"],r["entities"] ,r["attributes"] , schema,shapes_no)
        else:
            r1 = r["entities"][0]
            r2 = r["entities"][0] if len(r["entities"]) == 1 else r["entities"][1]
            #print("rel",r1,r2)
            if r1["cardinality"] == '1' and r2["cardinality"] == '1':
                #1 to 1
                if r1["participation"] == 'full':
                    addForgeinKey(r['name'],r1,r2,schema,r["attributes"])
                else:
                    addForgeinKey(r['name'],r2,r1,schema,r["attributes"])

            elif (r1["cardinality"] == '1' and r2["cardinality"] in ['N','M']): 
                addForgeinKey(r['name'],r2,r1,schema,r["attributes"])
            elif (r1["cardinality"] in ['N','M'] and r2["cardinality"] == '1'):
                addForgeinKey(r['name'],r1,r2,schema,r["attributes"])
            else:
                shapes_no += 1
                addEntitiesAsTables(r["name"],r["entities"] ,r["attributes"], schema,shapes_no)

    return schema



def addRelationsAttributes(entityRelation, relations):
    for r in entityRelation:
        if "attributes" not in relations[str(r["bounding_box"])]:
            relations[str(r["bounding_box"])]["attributes"]=[]
            
        relations[str(r["bounding_box"])]["attributes"] += r["attributes"]
        relations[str(r["bounding_box"])]["isIdentitfying"] = r["isIdentitfying"]


def addMultivaluedTable(schema,multivalued,shapes_no,table):
    for (m,dT) in multivalued:
        shapes_no+=1
        schema[shapes_no] = {
                "TableName": table["TableName"] +'_'+ m,
                "attributes":{m:dT},
                "primaryKey":[m],
                "ForgeinKey":[],
                "isWeak":False
            }
        for p in table["primaryKey"]:
            schema[shapes_no]["primaryKey"].append(table["TableName"]+'_'+p)
            schema[shapes_no]["attributes"][table["TableName"]+'_'+p] = table["attributes"][p]
            schema[shapes_no]["ForgeinKey"].append({
                "attributeName": table["TableName"]+'_'+p,
                "ForignKeyTable": table["TableName"],
                "ForignKeyTableAttributeName": p,
                "patricipaction":"full",
                "dataType": table["attributes"][p]
            })



def addCompositeKey(entity,entityIdx,entityRelations,relations,schema):
    '''
         ForignKey:[
        {
            attributeName:--,   in relations(entity attribute)
            ForignKeyTable:--,  in realtions(entity name)
            ForignKeyTableAttributeName:--, in relations(entity attribute name)
            patricipaction:--, in relations(entity participation)
            dataType:--, in relations
        }
        ]
    '''
    
    #find identifying relation
    for r in entityRelations:
        if r['isIdentitfying']:
            for identifyingEntites in relations[str(r["bounding_box"])]["entities"]:
                if(identifyingEntites["idx"]!=entityIdx):
                    primaryKeysOfEntity = schema[identifyingEntites["idx"]]["primaryKey"]
                    entity["primaryKey"]+= [r['name']+'_'+identifyingEntites["name"]+'_'+n for n in primaryKeysOfEntity]
                    dic = {r['name']+'_'+identifyingEntites["name"]+'_'+n : schema[identifyingEntites["idx"]]["attributes"][n]
                                    for n in primaryKeysOfEntity}
                    entity["attributes"].update(dic)
                    entity["ForgeinKey"]+= [ {
                        "attributeName": r['name']+'_'+identifyingEntites["name"]+'_'+n,
                        "ForignKeyTable": identifyingEntites["name"],
                        "ForignKeyTableAttributeName": n,
                        "patricipaction":identifyingEntites["participation"],
                        "dataType":schema[identifyingEntites["idx"]]["attributes"][n]
                    } for n in primaryKeysOfEntity]
                    


def addAtrributesAndPrimaryKey(entity,attributes):
    mulivalued = []
    for a in attributes:
        if a['isMultivalued']:
             mulivalued.append((a['name'],a['dataType']))
        elif a.get("children") and len(a["children"]):
            addAtrributesAndPrimaryKey(entity,a["children"])
        else:
            entity["attributes"][a['name']] = a['dataType']
            if a['isKey']:
                entity["primaryKey"].append(a['name'])
    return mulivalued


def addEntitiesAsTables(name,entities,attributes,schema,idx):   
    #for e in entities:
    primaryKey = []
    for e in entities:
        primaryKey+=schema[e["idx"]]["primaryKey"]

    schema[idx] = {
                "TableName": name +"_" + "_".join([schema[e["idx"]]["TableName"] for e in entities]),
                "attributes":{attributes[i]["name"] : attributes[i]["dataType"] for i in range(len(attributes))},
                "primaryKey": [],
                "ForgeinKey":[],
                "isWeak":False
            }       
    for e in entities:
        table = schema[e["idx"]]     
        for p in table["primaryKey"]:
            schema[idx]["primaryKey"].append(table["TableName"]+'_'+p)
            schema[idx]["attributes"][table["TableName"]+'_'+p] = table["attributes"][p]
            schema[idx]["ForgeinKey"].append({
                    "attributeName": table["TableName"]+'_'+p,
                    "ForignKeyTable": table["TableName"],
                    "ForignKeyTableAttributeName": p,
                    "patricipaction":"full",
                    "dataType": table["attributes"][p]
                })

def addForgeinKey(name,EntityToUpdate,Entity,schema,rAttributes):
    #add attributes
    dic = { rAttributes[i]["name"] : rAttributes[i]["dataType"] for i in range(len(rAttributes))}
    schema[ EntityToUpdate["idx"]]["attributes"].update(dic)

    #add attributes
    primaryKeysOfEntity = schema[Entity["idx"]]["primaryKey"]
    dic = { Entity["name"]+'_'+name+'_'+n : schema[Entity["idx"]]["attributes"][n] for n in primaryKeysOfEntity}

    #add forign keys
    
    schema[EntityToUpdate["idx"]]["attributes"].update(dic)
    schema[EntityToUpdate["idx"]]["ForgeinKey"]+= [ {
                        "attributeName": Entity["name"]+'_'+name+'_'+n,
                        "ForignKeyTable": Entity["name"],
                        "ForignKeyTableAttributeName": n,
                        "patricipaction":Entity["participation"],
                        "dataType":schema[Entity["idx"]]["attributes"][n]
                    } for n in primaryKeysOfEntity]  

