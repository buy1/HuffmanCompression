from __future__ import print_function
import os, sys
from Queue import PriorityQueue
from collections import Counter
import Queue 
import heapq
import struct
import pdb
import binascii
class Node:
    def __init__(self,name,freq):
        self.parent = None
        self.left = None
        self.right = None
        self.name = name
        self.freq = freq

class MinNodePriorityQueue(PriorityQueue):
    def __init__(self):
        self.queue=[]
    def isEmpty(self):
        return len(self.queue)==0
    def isSizeOne(self):
        return len(self.queue)==1
    def push(self,node):
        self.queue.append(node);
    def size(self):
        return len(self.queue)
    def pop(self):
        try:
            min = 0
            for i in range(len(self.queue)):
                if self.queue[i].freq < self.queue[min].freq:
                    min = i
            item = self.queue[min]
            del self.queue[min]
            return item
        except IndexError:
            print()
            exit()

def buildFreqTable(plaintext):
    freq_table=Counter()
    for letter in plaintext:
        freq_table[letter] += 1
    #TODO: Potential fix needed when decoding because letters of the same frequencies are arbitrarily ordered
    return freq_table

def buildPriorityQueue(freq_table):
    PriorityQueue = MinNodePriorityQueue()
    for item,freq in freq_table.iteritems():
        # print ("added %s: %d"%(item, freq))
        PriorityQueue.push(Node(item,freq))
    return PriorityQueue
def buildTree(pqueue):
    while pqueue.size()>1:
        left = pqueue.pop()
        right = pqueue.pop()

        newName = right.name + left.name
        newFreq = right.freq + left.freq
        newParent = Node(newName,newFreq)

        # if right.freq <= left.freq:
            # newParent.left = right
            # newParent.right = left
        # else:
        newParent.left = left
        newParent.right = right
        pqueue.push(newParent)

    return pqueue.pop()
def rebuildTree(tree):
    stack=[]
    nodesadded=0
    for i in range(len(tree)):
        if tree[i] == 'L':
            stack.append((Node(tree[i+1],0)))
            nodesadded+=1
        elif tree[i] == 'I':
            if len(stack) < 2:
                pdb.set_trace()
                return stack.pop()
            right = stack.pop()
            left = stack.pop()
            parent = Node(left.name+right.name,1)
            #TODO: might have to compare for order left and right
            parent.left = left 
            parent.right= right
            stack.append(parent)
            nodesadded+=1
    return stack.pop()
def postOrderPrint(rootNode):
    if not rootNode:
        return ""
    left = postOrderPrint(rootNode.left)
    right = postOrderPrint(rootNode.right)
    if not left and not right: # if leaf
        return "L" + rootNode.name
    else: # if interior node
        return left + right + "I"

def printTree(rootNode):
    if not rootNode:
        return
    printTree(rootNode.left)
    printTree(rootNode.right)
    print(rootNode.name,end='')

def buildEncodingTable(node):
    encodingtable={}
    def rbuildEncodingTable(node,currentpath):
        if not node: # null node
            return ""
        elif not node.left and not node.right: # no children
            encodingtable[node.name] = currentpath
            return
        else:
            rbuildEncodingTable(node.left,currentpath+"0")
            rbuildEncodingTable(node.right,currentpath+"1")

    rbuildEncodingTable(node,"")
    return encodingtable

def buildEncodedText(encodingtable, plaintext):
    return_string=""
    for letter in plaintext:
        if letter in encodingtable:
            return_string += encodingtable[letter]
        else:
            print ("string not in table")
    filllen = 8-len(return_string)%8
    padding = bin(0)[2:].zfill(filllen)
    print("padding added: " + str(filllen))
    padinf = "{0:08b}".format(filllen)
    return_string = padinf + return_string + padding
    return return_string
def toByteArray(padded_encoded_text):
    assert(len(padded_encoded_text)%8==0)
    b = bytearray()
    for i in range(0,len(padded_encoded_text), 8):
        byte = padded_encoded_text[i:i+8]
        b.append(int(byte,2))
    return b
def encode(fpplaintext,fpciphertext):
    with open(fpplaintext, "r") as plaintext:
        with open(fpciphertext,"w") as ciphertext:
            path = os.getcwd() + "/" + fpplaintext
            plaintext_cp = plaintext.read()
            freq_table = buildFreqTable(plaintext_cp)
            print(freq_table)
            pqueue = buildPriorityQueue(freq_table)
            numOfLeaves = pqueue.size()
            tree = buildTree(pqueue)
            encodingtable = buildEncodingTable(tree)
            # plaintext is already at the end
            encodedtext = buildEncodedText(encodingtable,plaintext_cp)
            treestring = postOrderPrint(tree)

            ciphertext.write(str(3*numOfLeaves-1)+":")
            ciphertext.write(str(os.path.getsize(path))+":")
            ciphertext.write(treestring)
            ciphertext.write(toByteArray(encodedtext))
def readFileInfo(plaintext):
    tree=""
    encoded=""
    x=1
    for i,line in enumerate(plaintext.split(":")):
        if i == 0: 
            treesize = line
        elif i==1:
            filesize = line
        else:
            for char in line:
                if x <= int(treesize):
                    tree+=char 
                else:
                    encoded+=char
                x+=1
                    
    return (tree,filesize,encoded)
# removes the padding from encoded text
def removePad(padlength,encodetext):
    return encodetext[:-1*padlength]
# converts hex to string of bits
#https://stackoverflow.com/questions/18815820/convert-string-to-binary-in-python
def hextobin(padLessEncodedText):
    return_str=""
    for char in padLessEncodedText:
        return_str += ''.join(format(x, 'b') for x in bytearray(char))
    return return_str

def decodetext(rebuilt_tree,filesize,encodedtext):
    padlength = int(hextobin(encodedtext[0]),2)
    wo_padinfo_encodetext = encodedtext[1:]
    pdb.set_trace()

    binaryencodedtext = hextobin(wo_padinfo_encodetext)
    padLessEncodedText = binaryencodedtext[:-1*padlength]

    cur_node = rebuilt_tree
    ret_string = ""
    debuglist=[]
    for i,bit in enumerate(padLessEncodedText):
        intbit = int(bit)
        debuglist.append(intbit)
        if intbit:
            cur_node = cur_node.right
        else:
            cur_node = cur_node.left
        if not cur_node.left and not cur_node.right:
            ret_string += cur_node.name
            cur_node = rebuilt_tree

    return ret_string

def decode(fpplaintext,fpciphertext):
    with open(fpplaintext, "w") as plaintext:
        with open(fpciphertext,"r") as compressedtext:
            compressed_cp = compressedtext.read()
            tree, filesize, encodedtext = readFileInfo(compressed_cp)
            rebuilt_tree = rebuildTree(tree)
            decoded = decodetext(rebuilt_tree,filesize,encodedtext)
            plaintext.write(decoded)

mode = sys.argv[1]
if mode in 'encode':
    fpplaintext = sys.argv[2]
    fpciphertext = sys.argv[3] + ".hzip"
    encode(fpplaintext,fpciphertext)
elif mode in 'decode':
    fpcompressedtext = sys.argv[2]
    fpplaintext = sys.argv[3]
    #pdb.set_trace()
    decode(fpplaintext,fpcompressedtext)
else:
    print("mode 1:encode\nmode 2:decode")
    exit(1)


