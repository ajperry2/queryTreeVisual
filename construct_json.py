import numpy
import json

def addNode(nameString,parent, layer):
    newNode=dict()
    newNode['Name'] = nameString
    newNode['layer']= layer
    newNode['children']=[]
    for child in parent['children']:
        if child['Name'] == nameString: return
    parent['children'].append(newNode)


def findChild(childName,parent):
    for child in parent['children']:
        if child['Name'] == childName:
            return child
    return None


def constructJson(lists,columns:list):
    parentNode = dict()
    parentNode['Name'] = 'Query'
    parentNode['layer'] = ''
    parentNode['children'] = []
    #get column order based on number of unique values
    dataLength = len(lists[0])
    unique_sizes = [0 for x in range(dataLength)]
    for col in range(dataLength):
        store_set = set([x[col] for x in lists])
        unique_sizes[col] = len(store_set)
    order = numpy.argsort(unique_sizes)
    print(order)
    i = 0
    for layer in order:
        for rowNum in range(len(lists)):
            # find correct parent
            parentnode = parentNode
            for iter in range(i):
                parentnode = findChild(str(lists[rowNum][order[iter]]),parentnode)
            #print(lists[rowNum])
            #print(parentnode.Name+'->'+str(lists[rowNum][order[i]]))
            addNode(str(lists[rowNum][order[i]]), parentnode, columns[layer])
        i+=1

    return(json.dumps(parentNode))

