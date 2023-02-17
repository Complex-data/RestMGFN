import networkx as nx
import pandas as pd
import numpy as np
import scipy
import scipy.sparse as spa
import math
import random

from os import system

class BipartiteNetwork:
    """
    Class for handling bipartite networks using scipy's sparse matrix
    Designed to for large networkx, but functionalities are limited
    """
    def __init__(self):
        pass

    def load_data(
        self, data_path, user_col, item_col,
        rating_col, time_col='None', sep='::'
    ):

        temp_df = pd.read_csv(data_path, sep=sep, engine='python')
        #print(temp_df)
        tuple = self.set_data(temp_df, user_col, item_col, rating_col, time_col)
        return tuple

    def set_data(self, df, user_col, item_col, rating_col, time_col):

        self.df = df
        self.user_col = user_col
        self.item_col = item_col
        self.rating_col = rating_col
        self.time_col = time_col

        tuple = self._index_nodes()
        #self._generate_adj()
        return tuple

    def _index_nodes(self):
        """
        Representing the network with adjacency matrix requires indexing the user
        and item nodes first
        """
        #构建user_id的index数组
        self.user_ids = pd.DataFrame(
            self.df[self.user_col].sort_values(ascending=True).unique(),
            columns=[self.user_col]
        ).reset_index()
        #重命名数组的列名
        self.user_ids = self.user_ids.rename(columns={'index': 'user_index'})
        print(self.user_ids)
        #用户总数
        self.num_of_user = len(self.user_ids)
        print(self.num_of_user)


        #构建item id的index数组
        self.item_ids = pd.DataFrame(
            self.df[self.item_col].sort_values(ascending=True).unique(),
            columns=[self.item_col]
        ).reset_index()
        # 重命名数组的列名
        self.item_ids = self.item_ids.rename(columns={'index': 'item_index'})
        print(self.item_ids)
        #item总数
        self.num_of_item = len(self.item_ids)
        print(self.num_of_item)

        # 构建评分的数组
        self.ratings = pd.DataFrame(
            self.df[self.rating_col].sort_values(ascending=True).unique(),
            columns=[self.rating_col]
        ).reset_index()
        self.ratings = self.ratings.rename(columns={'index': 'rating_index'})
        print(self.ratings)


        self.df = self.df.merge(self.user_ids, on=self.user_col)
        self.df = self.df.merge(self.item_ids, on=self.item_col)
        self.df = self.df.merge(self.ratings, on=self.rating_col)
        print('df is -----------------')
        print(self.df)

        list_ids = self.user_ids["user_id"].values[:]
        list_items =  self.item_ids["item_id"].values[:]
        return (list_ids,list_items)

    def _generate_adj(self):
        """
        Generating the adjacency matrix for the birparite network.
        The matrix has dimension: D * P where D is the number of top nodes
        and P is the number of bottom nodes
        """
        if self.rating_col is None:
            # set weight to 1 if weight column is not present
            weight = np.ones(len(self.df))
        else:
            weight = self.df[self.rating_col]
            #print(weight)

        #print(self.df['user_index'].values)
        matrix = spa.coo_matrix(
            (
                weight,
                (self.df['user_index'].values, self.df['item_index'].values)
            )
        )
        self.W = matrix.toarray()
        self.W_spammed = matrix.toarray()
        print(self.W)
        print(self.W_spammed)

    def generate_degree(self):
        """
        This method returns the degree of nodes in the bipartite network
        """
        #计算用户节点的度
        user_degree = self.df.groupby(self.user_col)[self.rating_col].size()
        self.user_degree = user_degree.to_frame(name='degree').reset_index()
        print(self.user_degree)
        #用户度的平均值
        print(sum(self.user_degree["degree"].values)/len(self.user_degree))

        #计算Item节点的度
        item_degree = self.df.groupby(self.item_col)[self.rating_col].size()
        self.item_degree = item_degree.to_frame(name='degree').reset_index()
        print(self.item_degree)

        # 物品度的平均值
        print(sum(self.item_degree["degree"].values) / len(self.item_degree))

# if __name__ == "__main__":
#     bn = BipartiteNetwork()
#     bn.load_data(
#         #data_path="./test_data/ratings.dat",
#         data_path="./movielens/ratings_spammed.dat",
#         user_col='user_id',
#         item_col='item_id',
#         rating_col='rating',
#         time_col='time'
#     )
#     bn._generate_adj()
#     bn.generate_degree()
#     #bn.IGR()
#     #bn.GR()
#     bn.compute_NFS()


#Movielens数据处理，（缩小数据的规模）
# if __name__ == "__main__":
#     bn = BipartiteNetwork()
#     list_ids = bn.load_data(
#         #data_path="./test_data/ratings.dat",
#         data_path="movielens/rating-6000-4000.dat",
#         #data_path="./artificial_data/rating.txt",
#         user_col='user_id',
#         item_col='item_id',
#         rating_col='rating',
#         time_col='time'
#     )
#     bn._generate_adj()
#     bn.generate_degree()
#     print(len(list_ids))
#     print(list_ids[0])
#
#
#
#
#     f = open("movielens/rating-6000-4000.dat", 'r')
#     records = []
#     f.readline()
#     for line in f.readlines():
#         records.append(line.strip('\n'))
#     print(len(records))
#     f.close()
#
#     select_ids = set()
#     while len(select_ids) < 5000:
#         index = random.randint(0,6039)
#         select_ids.add(list_ids[index])
#     print(select_ids)
#
#
#     list_filter = []
#     for i in records:
#         if (int(i.split("::")[0]) not in select_ids) \
#                 and ((1000 < int(i.split("::")[1]) < 1300) \
#                 or (1500 < int(i.split("::")[1]) < 1800) \
#                 or (3000 < int(i.split("::")[1]) < 3200) \
#                 or (500 < int(i.split("::")[1]) < 800)):
#             list_filter.append(i)
#     print(list_filter)
#
#     f = open("movielens/rating-1000.dat", 'w')
#     f.write("user_id::item_id::rating::time\n")
#     for i in list_filter:
#         f.write(i+"\n")
#     f.close()


#AmzonMusicData数据处理
# if __name__ == "__main__":
#     f = open("AmazonMusicData/1.uid-aid-rating-time", 'r')
#     f1 = open("AmazonMusicData/amazon-ratings.dat",'w')
#     f1.write("user_id::item_id::rating::time\n")
#     count = 0
#     for line in f.readlines():
#         list = line.strip("\n").split("\t")
#         #if count%3:
#         f1.write(list[0]+"::"+list[1]+"::"+list[2]+"::"+list[3]+"\n")
#         #count += 1
#     f.close()
#     f1.close()

#AmzonMusicData数据处理(去掉重复的数据)
if __name__ == "__main__":
    
    f = open("AmazonMusicData/ratings.dat", 'r')
    f.readline()
    f1 = open("AmazonMusicData/ratings.dat-1",'w')
    f1.write("user_id::item_id::rating\n")
    list1 = []
    list2 = []
    for line in f.readlines():
        list1.append(line.strip("\n"))
        list2.append(line.strip("\n").split("::")[0]+"::"+line.strip("\n").split("::")[1])
    #print(list1[145])
    #print(list2[145])
    list3 = []
    list4 = []
    for i in range(len(list2)):
        #print(list2[i])
        if list2[i] not in list3:
            list3.append(list2[i]) 
            list4.append(list1[i])
    print(len(list4))

    for line in list4:
        f1.write(line+"\n")
    f.close()
    f1.close()





#Netflix数据处理，过滤user和item，达到指定值
# if __name__ == "__main__":
#     bn = BipartiteNetwork()
#     tuple = bn.load_data(
#         #data_path="./test_data/ratings.dat",
#         data_path="Netflix/netflix_movie_rating.dat",
#         #data_path="./artificial_data/rating.txt",
#         user_col='user_id',
#         item_col='item_id',
#         rating_col='rating',
#         time_col='time'
#     )
#     bn._generate_adj()
#     bn.generate_degree()
#
#     list_ids = tuple[0]
#     list_items = tuple[1]
#
#     print(len(list_items))
#
#
#
#
#     f = open("Netflix/netflix_movie_rating-1.dat", 'r')
#     records = []
#     f.readline()
#     for line in f.readlines():
#         records.append(line.strip('\n'))
#     print(len(records))
#     f.close()
#
#     select_ids = set()
#     while len(select_ids) < 10483:
#         index = random.randint(0,17733)
#         select_ids.add(list_ids[index])
#     print(select_ids)
#
#
#     list_filter = []
#     for i in records:
#         if (int(i.split("::")[1]) not in select_ids):
#             list_filter.append(i)
#     print(list_filter)
#
#     f = open("Netflix/netflix_movie_rating-2.dat", 'w')
#     f.write("user_id::item_id::rating::time\n")
#     for i in list_filter:
#         f.write(i+"\n")
#     f.close()

#Netflix数据集处理：保留item度小于1000
# if __name__ == "__main__":
#     df = pd.read_csv("Netflix/netflix_movie_rating-2.dat", sep="::", engine='python')
#     print(df)
#     #user_degree = self.df.groupby(self.user_col)[self.rating_col].size()

#     df_count = df.groupby("item_id")["item_id"].size()
#     df_count = df_count.to_frame(name='count').reset_index()
#     df_count = df_count[df_count["count"] < 1700]
#     print(df_count)
#     list_less_1000 = df_count["item_id"].values
#     print(len(list_less_1000))
#     df_filter = df[df["item_id"].isin(list_less_1000)]
#     print(df_filter)
#     df_filter.to_csv("Netflix/netflix_movie_rating-3.dat",index=False,header=True)

#     f = open("Netflix/netflix_movie_rating-3.dat", 'r')
#     f1 = open("Netflix/netflix_movie_rating_10426_6874.dat", 'w')
#     f1.write("user_id::item_id::rating::time\n")
#     f.readline()
#     for line in f.readlines():
#         f1.write(line.strip("\n").split(",")[0]+"::"+line.strip("\n").split(",")[1]+"::"
#                  +line.strip("\n").split(",")[2]+"::"+line.strip("\n").split(",")[3]+"\n")
#     f.close()
#     f1.close()