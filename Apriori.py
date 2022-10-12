import openpyxl 
from pathlib import Path

# 设置最小支持度和置信度
MIN_Support = 0.5
MIN_Conf = 0.6


def DataFactory():
    data_file = Path('FoodPreference.xlsx') 
    wb_obj = openpyxl.load_workbook(data_file)
    sheet = wb_obj.active
    # print the sheet # output: <worksheet "sheet1">

    data_list = []
    data_temp = []
    data_column = []

    # get the data by row 
    for row in sheet.iter_rows(min_row=1):
        for cell in row:
            data_temp.append(cell.value)
        data_list.append(data_temp)
        data_temp = []
    # print(data_list)
    
    label = data_list[0]
    datachunk = data_list[1:]

    dataset = []
    # transform the data_list to a better formatted dataset
    for i in range(len(datachunk)):
        for j in range(26):
            if datachunk[i][j] == 1:
                data_temp.append(j)
        dataset.append(data_temp)
        data_temp = []

    return dataset

def createOneitmeset(dataSet):
    one_itmeset = []
    for transaction in dataSet:             #循环遍历dataset中所有元素，未在列表中则添加
        for item in transaction:
            if not [item] in one_itmeset:
                one_itmeset.append([item])
    one_itmeset.sort()
    return list(map(frozenset, one_itmeset))

def K_itemsetGenerator(K_itemset_prev, K):
    K_itemset = []				#K-项集
    len_prev = len(K_itemset_prev)		#前一项集项数
    for i in range(len_prev):			#二重循环两两组合生成生成新项集
        for j in range(i+1, len_prev):
            L1=list(K_itemset_prev[i])[:K-2];L2=list(K_itemset_prev[j])[:K-2]
            L1.sort();L2.sort()
            if L1==L2:
                K_itemset.append(K_itemset_prev[i]|K_itemset_prev[j])            
    return K_itemset

def filter_itmeset(Data, itmeset):
    item_frequency = {}
    for item in Data:				#循环遍历项集中元素，并记录出现次数至item_frequency字典中
        for element in itmeset:
            if element.issubset(item):                   #issubset方法:若item包含element中所有元素则返回True
                if not element in item_frequency: item_frequency[element] = 1
                else:item_frequency[element] += 1

    numItems = float(len(Data))		#数据集中总的项集个数

    item_filtered = [] 				#频繁项集
    itemSupprotData={}				#项集中各项支持度
    for key in item_frequency:
        support = item_frequency[key]/numItems	#支持度计算：元素出现次数 / 总项集数
        if support>=MIN_Support:				#满足最小支持度添加到频繁项集列表中
            item_filtered.insert(0, key)
        itemSupprotData[key] = support
    return item_filtered, itemSupprotData

def itemset_exhaustion(dataSet):
    one_itmeset = createOneitmeset(dataSet)
    Data = list(map(set, dataSet))
    one_itmeset_filtered, itemSupprotData_union = filter_itmeset(Data, one_itmeset)
    itemset_union = [one_itmeset_filtered]
    K = 2
    while(len(itemset_union[K - 2]) > 0):
        K_itemset = K_itemsetGenerator(itemset_union[K-2], K)
        K_itemset_filtered, K_itemSupprotData = filter_itmeset(Data, K_itemset)
        itemSupprotData_union.update(K_itemSupprotData)
        itemset_union.append(K_itemset_filtered)
        K += 1
    return itemset_union, itemSupprotData_union

def findRelatedItemGroup(K_itemset_freq,itemSupprotData):
    RelatedItemGroup = []
    K = len(K_itemset_freq)
    for i in range(1, K):
        for itemset in K_itemset_freq[i]:
            itemWaitjudge = [frozenset([element]) for element in itemset]
            if(i > 1):
                reunionAcalcConf(itemset,itemWaitjudge,itemSupprotData,RelatedItemGroup)
            else:
                calcConf(itemset,itemWaitjudge,itemSupprotData,RelatedItemGroup)
    return RelatedItemGroup

def calcConf(itemset, itemWaitjudge, itemSupprotData, RelatedItemGroup):
    item_realted = []                   #存储itemWaitjudge项中强关联规则
    for item in itemWaitjudge:
        conf = itemSupprotData[itemset] / itemSupprotData[itemset - item]   #计算置信度
        if conf >= MIN_Conf:            #满足条件 存储并输出
            print (itemset-item,'--->',item,'conf:',conf)
            RelatedItemGroup.append((itemset - item, item, conf))
            item_realted.append(item)
    return item_realted

def reunionAcalcConf(itemset, itemWaitjudge, itemSupprotData, RelatedItemGroup):
    K = len(itemWaitjudge[0])               #K:当前项集的项数
    if (len(itemset) > (K + 1)):            #当当前项集项数已经组合到(父项集项数 - 1)时无需再次递归组合，否则继续在组合
        itemset_reunion = K_itemsetGenerator(itemWaitjudge, K + 1)      #项集包含项再组合，项数为当前项数 + 1
        itemset_reunion_filtered = calcConf(itemset, itemset_reunion, itemSupprotData, RelatedItemGroup)  #计算置信度并进行滤除
        if(len(itemset_reunion_filtered) > 1):               #如果没有强关联规则存在，后续的也无须递归再组合计算置信度
            reunionAcalcConf(itemset, itemset_reunion_filtered, itemSupprotData, RelatedItemGroup)   #存在强关联规则，递归在组合计算置信度

if __name__=='__main__':
    dataSet = DataFactory()
    L,supportData=itemset_exhaustion(dataSet)
    rules = findRelatedItemGroup(L,supportData)

