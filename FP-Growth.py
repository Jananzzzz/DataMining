

from functools import reduce
from collections import Counter
from typing import Dict, List
from queue import Queue
from itertools import combinations

class Node(object):
    def __init__(self, name, fa) -> None:
        self.name = name
        self.fa = fa
        self.children = []
        self.children_name = []

        self.__count = 1
    
    def add_count(self):
        self.__count += 1
    
    @property
    def count(self):
        return self.__count


def DummyFPGrowth(transactions : dict, min_sup : float) -> Dict[str, List[List[str]]]:
    n_sup = round(len(transactions) * min_sup)
    counter = Counter(reduce(lambda x, y : x + y, (v for v in transactions.values())))
    
    item_table = sorted(counter, key=lambda x : counter[x])
    # node
    item_table = {item : {'count' : counter[item], 'node' : []} for item in item_table if counter[item] >= n_sup}

    # reconstruct transaction
    for TID in transactions:
        new_transaction = sorted(transactions[TID], key=lambda x : counter[x], reverse=True)
        transactions[TID] = [t for t in new_transaction if counter[t] >= n_sup]
    del new_transaction

    # build FP-tree
    root = Node('root', None)
    for TID in transactions:
        cur_fa_node = root
        for item in transactions[TID]:
            if item in cur_fa_node.children_name:
                i = cur_fa_node.children_name.index(item)
                cur_fa_node : Node = cur_fa_node.children[i]
                cur_fa_node.add_count()
            else:
                new_node = Node(item, cur_fa_node)
                cur_fa_node.children.append(new_node)
                cur_fa_node.children_name.append(item)
                cur_fa_node = new_node
            if cur_fa_node != root:
                item_table[item]['node'].append(cur_fa_node)
    
    # get conditional pattern base
    conditional_pattern_base = {}
    for item in item_table:
        if item_table[item]['node']:
            if item not in conditional_pattern_base:
                conditional_pattern_base[item] = []
            for node in item_table[item]['node']:
                suffix = []
                cur_node = node.fa
                while cur_node.name != 'root':
                    suffix.append(cur_node.name)
                    cur_node = cur_node.fa
                if suffix:
                    conditional_pattern_base[node.name].append(suffix)
            if len(conditional_pattern_base[item]) == 0:
                del conditional_pattern_base[item]
    
    # count and trim
    for item in conditional_pattern_base:
        sub_counter = Counter(reduce(lambda x, y : x + y, (conditional_pattern_base[item])))
        for i, suffix in enumerate(conditional_pattern_base[item]):
            new_transaction = [item for item in suffix if sub_counter[item] >= n_sup]
            conditional_pattern_base[item][i] = sorted(new_transaction, key=lambda x : sub_counter[x], reverse=True)

    # build sub fp-tree and get path  
    conditional_fp_tree_path : Dict[str, List[Node]] = {}   
    for item in conditional_pattern_base:
        conditional_fp_tree_path[item] = []
        # build sub fp-tree
        root = Node('root', Node)
        for suffix in conditional_pattern_base[item]:
            cur_fa_node = root
            for item_name in suffix:
                if item_name in cur_fa_node.children_name:
                    i = cur_fa_node.children_name.index(item_name)
                    cur_fa_node = cur_fa_node.children[i]
                    cur_fa_node.add_count()
                else:
                    new_node = Node(item_name, cur_fa_node)
                    cur_fa_node.children.append(new_node)
                    cur_fa_node.children_name.append(item_name)
                    cur_fa_node = new_node
        
        # get all the path by BFS
        q = Queue()
        q.put(root)
        while not q.empty():
            cur_node : Node = q.get()
            if cur_node.children:
                for node in cur_node.children:
                    q.put(node)
            else:
                path = []
                while cur_node != root:
                    path.append(cur_node.name)
                    cur_node = cur_node.fa
                conditional_fp_tree_path[item].append(path)
    
    # calculate final result
    result = {item : set() for item in conditional_fp_tree_path}
    for item in conditional_fp_tree_path:
        for path in conditional_fp_tree_path[item]:
            for i, _ in enumerate(path):
                for elements in combinations(path, i + 1):
                    cur_tuple = tuple(list(elements) + [item])
                    result[item].add(cur_tuple)

    # transform to list
    for item, tuple_set in result.items():
        itemsets = [list(itemset) for itemset in tuple_set]
        result[item] = itemsets

    return result

# 将十个人的事务表示出来
# 利用之前apriori算法的数据，进行事物重构：
'''
dataSet = [[0, 5, 7, 9, 10, 12, 13, 14, 15, 18, 20, 22, 24, 25], [0, 2, 5, 9, 12, 13, 14, 15, 17, 18, 21, 22, 24], [0, 4, 5, 7, 9, 12, 13, 14, 15, 17, 20, 21, 23, 24], [0, 5, 7, 10, 13, 15, 17, 21, 22, 24, 25], [3, 5, 9, 13, 15, 17, 18, 20, 23, 25], [0, 1, 2, 5, 8, 9, 10, 12, 13, 14, 15, 16, 18, 19, 22, 23, 24], [0, 2, 5, 7, 10, 12, 13, 15, 17, 19, 22, 23, 24], [0, 4, 5, 7, 12, 14, 15, 17, 18, 19, 21, 22, 25], [3, 5, 9, 15, 17, 18, 19, 21, 22, 23, 25], [0, 1, 4, 7, 10, 12, 13, 16, 17, 20, 22, 24, 25], [2, 4, 7, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24]]


transactions = {}

for i in range(len(dataSet)):
    tmp = []
    for j in dataSet[i]:
        tmp.append(str(j))
    transactions[str(i)] = tmp
    
print(transactions)
'''
'''
[[0, 5, 7, 9, 10, 12, 13, 14, 15, 18, 20, 22, 24, 25], [0, 2, 5, 9, 12, 13, 14, 15, 17, 18, 21, 22, 24], [0, 4, 5, 7, 9, 12, 13, 14, 15, 17, 20, 21, 23, 24], [0, 5, 7, 10, 13, 15, 17, 21, 22, 24, 25], [3, 5, 9, 13, 15, 17, 18, 20, 23, 25], [0, 1, 2, 5, 8, 9, 10, 12, 13, 14, 15, 16, 18, 19, 22, 23, 24], [0, 2, 5, 7, 10, 12, 13, 15, 17, 19, 22, 23, 24], [0, 4, 5, 7, 12, 14, 15, 17, 18, 19, 21, 22, 25], [3, 5, 9, 15, 17, 18, 19, 21, 22, 23, 25], [0, 1, 4, 7, 10, 12, 13, 16, 17, 20, 22, 24, 25], [2, 4, 7, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24]]
'''
transactions ={'0': ['0', '5', '7', '9', '10', '12', '13', '14', '15', '18', '20', '22', '24', '25'], '1': ['0', '2', '5', '9', '12', '13', '14', '15', '17', '18', '21', '22', '24'], '2': ['0', '4', '5', '7', '9', 
'12', '13', '14', '15', '17', '20', '21', '23', '24'], '3': ['0', '5', '7', '10', '13', '15', '17', '21', '22', '24', '25'], '4': ['3', '5', '9', '13', '15', '17', '18', '20', '23', '25'], '5': ['0', 
'1', '2', '5', '8', '9', '10', '12', '13', '14', '15', '16', '18', '19', '22', '23', '24'], '6': ['0', '2', '5', '7', '10', '12', '13', '15', '17', '19', '22', '23', '24'], '7': ['0', '4', '5', '7', '12', '14', '15', '17', '18', '19', '21', '22', '25'], '8': ['3', '5', '9', '15', '17', '18', '19', '21', '22', '23', '25'], '9': ['0', '1', '4', '7', '10', '12', '13', '16', '17', '20', '22', '24', '25'], '10': ['2', '4', '7', '9', '10', '12', '13', '14', '15', '16', '17', '18', '19', '21', '22', '23', '24']}


if __name__ == "__main__":
    result = DummyFPGrowth(transactions, min_sup=0.6)
    for k, v in result.items():
        print(k, ' : ', v)


