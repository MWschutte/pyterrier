from jnius import autoclass, cast, PythonJavaClass, java_method
from utils import *
import pandas as pd
import numpy as np
import os

CollectionDocumentList = autoclass("org.terrier.indexing.CollectionDocumentList")
StringReader = autoclass("java.io.StringReader")
HashMap = autoclass("java.util.HashMap")
TaggedDocument = autoclass("org.terrier.indexing.TaggedDocument")
Tokeniser = autoclass("org.terrier.indexing.tokenisation.Tokeniser")
TRECCollection = autoclass("org.terrier.indexing.TRECCollection")
SimpleFileCollection = autoclass("org.terrier.indexing.SimpleFileCollection")
BasicIndexer = autoclass("org.terrier.structures.indexing.classical.BasicIndexer")
Collection = autoclass("org.terrier.indexing.Collection")
Arrays = autoclass("java.util.Arrays")
Array = autoclass('java.lang.reflect.Array')
ApplicationSetup = autoclass('org.terrier.utility.ApplicationSetup')
Properties = autoclass('java.util.Properties')


class BasicIndex():
    def createCollection(self, docDataframe):
        lst = []
        for index, row in docDataframe.iterrows():
            hashmap = HashMap()
            # all columns, except text are properties and add them to hashmap
            for column, value in row.iteritems():
                if column!="text":
                    hashmap.put(column,value)
            tagDoc = TaggedDocument(StringReader(row["text"]), hashmap, Tokeniser.getTokeniser())
            # print("DOCNO: " + str(hashmap.get("DOCNO")))
            lst.append(tagDoc)
        javaDocCollection = CollectionDocumentList(lst, "null")
        return javaDocCollection

    def __init__(self,collection, path):
        # if collection is a dataframe create a new collection object
        if type(collection)==type(pd.DataFrame([])):
            javaDocCollection = self.createCollection(collection)
            index = BasicIndexer(path, "data")
            index.index([javaDocCollection])


def createDFIndex(index_path, text, *args, **kwargs):
    # if len(text)!=len(metadataa):
    #     throw Exception
    all_metadata={}
    for arg in args:
        if isinstance(arg, pd.Series):
            all_metadata[arg.name]=arg
            assert len(arg)==len(text), "Length of metadata arguments needs to be equal to length of text argument"
        elif isinstance(arg, pd.DataFrame):
            for name, column in arg.items:
                all_metadata[name]=column
                assert len(column)==len(text), "Length of metadata arguments needs to be equal to length of text argument"
        else:
            raise ValueError("Non-keyword args need to be of type pandas.Series or pandas,DataFrame")
    for key, value in kwargs.items():
        if isinstance(value, (pd.Series, list, tuple)):
            all_metadata[key]=arg
            assert len(arg)==len(text), "Length of metadata arguments needs to be equal to length of text argument"
        elif isinstance(arg, pd.DataFrame):
            for name, column in arg.items:
                all_metadata[name]=column
                assert len(column)==len(text), "Length of metadata arguments needs to be equal to length of text argument"
        else:
            raise ValueError("Keyword kwargs need to be of type pandas.Series, list or tuple")

    doc_list=[]
    for text_row, meta_name, meta_column in zip(text, all_metadata.keys(), all_metadata.values()):
        # print(meta_column)
        meta_row=[]
        hashmap = HashMap()

        for column, value in meta_column.iteritems():
            print(meta_name, value)
            hashmap.put(meta_name,value)
        tagDoc = TaggedDocument(StringReader(text_row), hashmap, Tokeniser.getTokeniser())
        doc_list.append(tagDoc)
    javaDocCollection = CollectionDocumentList(doc_list, "null")
    index = BasicIndexer(index_path, "data")
    index.index([javaDocCollection])
    return (os.path.join(index_path, "data.properties"))

def createTRECIndex(index_path, trec_path, doctag="DOC", idtag="DOCNO", skip="DOCHDR",casesensitive="false", trec_class="TRECCollection"):
    trec_props={
        "TrecDocTags.doctag":doctag,
        "TrecDocTags.idtag":idtag,
        "TrecDocTags.skip":skip,
        "TrecDocTags.casesensitive":skip,
        "trec.collection.class": trec_class
    }
    properties = Properties()
    for control,value in trec_props.items():
        properties.put(control,value)
    ApplicationSetup.bootstrapInitialisation(properties)
    asList = Arrays.asList(trec_path)
    trecCol = TRECCollection(asList,"TrecDocTags","","")
    index = BasicIndexer(index_path,"data")
    index.index([trecCol])
    return (os.path.join(index_path, "data.properties"))


def createFilesIndex(index_path, files_path):
    asList = Arrays.asList(files_path)
    simpleColl = SimpleFileCollection(asList,False)
    index = BasicIndexer(index_path,"data")
    index.index([simpleColl])
    return (os.path.join(index_path, "data.properties"))
