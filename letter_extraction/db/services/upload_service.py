# reading metadata from docx and storing in array
# need to download docx module first
# i.e. $pip install --pre python-docx

import os
import docx
import nltk
import xlrd
import re
import pandas as pd

#Xlsx and xls scanner function
def xlscanner(filename):
    wb = pd.ExcelFile(filename)
    #headers = ['archive code','addressee','language']
    headlist = []
    totalsheet = len(wb.sheet_names)
    archcol = 0
    wholedoc=[]

    #Goes thru each worksheet
    for ws in range(totalsheet):
        headstart = -1
        letters = []
        sheet = pd.read_excel(wb,wb.sheet_names[ws],header=None,index_col=None)
        #Finds the data header // Goes thru each row
        for i in range (sheet.shape[0]):
            each = []
            for j in range (sheet.shape[1]):
                content = sheet.iloc[i,j]
                if(headstart == -1):
                    each.append((j,content))
                else:
                    each.append((headlist[ws][j][1],content))
                j=j+1

            if (headstart == -1): #Finding header
                m = 0
                for k in each:
                    if(type(k[1]) == str):
                        if (k[1].lower()=='archive code'):
                            archcol = m
                            headstart = i
                            headlist.append(each)
                            break
                    m=m+1
            #Only adds non-empty list to letters
            #Does not add data with no archive number
            if (pd.isnull(each[archcol][1])):
                continue
            if(not all(pd.isnull(s[1]) for s in each)):
                letters.append(each)
            i = i+1
        wholedoc.append(letters)
    return wholedoc

#Fills in non-given metadata as empty string
def filler(myletter):
    indicator = [0,1,2,3,4,5,6,7]
    for i in myletter:
        for j in indicator:
            if (i[0] == j):
                indicator.remove(j)

    #Adds empty string for non-given metadata
    for m in indicator:
        myletter.append( (m, "") )

#Docx scanner function
def docxscanner(filename):
    doc = docx.Document(filename)
    wholedoc = []
    #lists of every letter data
    letters = []
    summary = ''
    letterdata = []
    #regex for splitting \n and \t
    regex = re.compile(r'[\n\r\t]')

    #Stores each paragraph in a list
    for para in doc.paragraphs:
        wholedoc.append(para.text)
    k = 1 #initialise index letter
    j = 0 #initialise receiver and sender indicator
    count = 0
    #Give each words a named entity
    for sentence in wholedoc:
        count = count+1
        sentence = regex.sub("",sentence)
        tokens = nltk.word_tokenize(sentence)
        tagged = nltk.pos_tag(tokens)
        #Finds the Word Index header
        #For each new header, it will initialise a list to store all its data
        #print(sentence, wholedoc[count-1])
        if (len(tagged) == 1):
            if(tagged[0][0] == str(k)):
                if(k!=1):
                    filler(letterdata)
                    letterdata.append((6,summary))
                    letters.append(letterdata)
                summary=''
                k = k+1
                letterdata = []

            #Finds letter reference number (0)
            elif (tagged[0][1] == "JJ"):
                letterdata.append((0,sentence))

            #Finds Letter Addressee (1)
            elif (tagged[0][1] == "NN"):
                letterdata.append((1,sentence))

        #Finds Letter Sender
        if (len(tagged) > 2):
            #amount pages (7)
            if(((tagged[0][1] == "(") or (tagged[0][1] == ".")) and ((tagged[2][1] == "NNS") or (tagged[2][1] == "NN") or (tagged[1][1] == "$"))):
                letterdata.append((7,sentence))

            #Dates (2)
            elif ( (tagged[2][1] == "CD") and ((tagged[1][1] == ",") or (tagged[1][1] == "NNP") or (tagged[1][1] == ":") or (tagged[1][1] == ".") or (tagged[3][1] == ","))):
                letterdata.append((2,sentence))

            #Sender (3) & Addresse (4)
            elif ( (tagged[2][1] == "NNP") and ((tagged[1][1] == ",") or (tagged[1][1] == ":") or (tagged[1][1] == ".")  or (tagged[3][1] == ","))):
                if (j == 0):
                    letterdata.append((3,sentence))
                    j = j+1
                else:
                    letterdata.append((4,sentence))
                    j = j-1

            #Finds Types of letters (5)
            elif ((tagged[0][1] == "NN") and (tagged[1][1] == ",")):
                letterdata.append((5,sentence))

        #ASSUME it is the letter summary if it is longer than 10
        #Summary of letters in (6)
        if(len(tagged) > 10):
            summary = summary+sentence

        if(len(wholedoc) == count):
            letterdata.append((6,summary))
            filler(letterdata)
            letters.append(letterdata)
    return letters

def main(filename):
    #currently only for .docx and .xlsx and .xls files
    if (filename.name.endswith('.docx')):
        return docxscanner(filename)
    elif ((filename.name.endswith('.xlsx')) or (filename.name.endswith('.xls'))):
        return xlscanner(filename)
    else:
        print('Only accept .docx and .xls files')
