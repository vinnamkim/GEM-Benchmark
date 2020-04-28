from gem.evaluation import visualize_embedding as viz
from gem.utils import graph_util, plot_util
from .static_graph_embedding import StaticGraphEmbedding
from subprocess import call
import sys
from time import time
import scipy.sparse.linalg as lg
import scipy.sparse as sp
import scipy.io as sio
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import os
disp_avlbl = True
if 'DISPLAY' not in os.environ:
    disp_avlbl = False
    import matplotlib
    matplotlib.use('Agg')


sys.path.append('./')
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


class node2vec(StaticGraphEmbedding):
    """`node2vec`_.
    Node2Vec aim to learn a low-dimensional feature 
    representation for nodes through a stream of random walks. 
    These random walks explore the nodes' variant neighborhoods. 
    Thus, random walk based methods are much more scalable for large 
    graphs and they generate informative embeddings.

    Args:
        hyper_dict (object): Hyper parameters.
        kwargs (dict): keyword arguments, form updating the parameters

    Examples:
        >>> from gemben.embedding.node2vec import node2vec
        >>> edge_f = 'data/karate.edgelist'
        >>> G = graph_util.loadGraphFromEdgeListTxt(edge_f, directed=False)
        >>> G = G.to_directed()
        >>> res_pre = 'results/testKarate'
        >>> graph_util.print_graph_stats(G)
        >>> t1 = time()
        >>> embedding = node2vec(2, 1, 80, 10, 10, 1, 1)
        >>> embedding.learn_embedding(graph=G, edge_f=None,
                                  is_weighted=True, no_python=True)
        >>> print('node2vec:Training time: %f' % (time() - t1))
        >>> viz.plot_embedding2D(embedding.get_embedding(),
                             di_graph=G, node_colors=None)
        >>> plt.show()
    .. _node2vec:
        https://cs.stanford.edu/~jure/pubs/node2vec-kdd16.pdf
    """

    def __init__(self, *hyper_dict, **kwargs):
        ''' Initialize the node2vec class

        Args:
            d: dimension of the embedding
            max_iter: max iterations
            walk_len: length of random walk
            num_walks: number of random walks
            con_size: context size
            ret_p: return weight
            inout_p: inout weight
        '''
        hyper_params = {
            'method_name': 'node2vec_rw'
        }
        hyper_params.update(kwargs)
        for key in hyper_params.keys():
            self.__setattr__('_%s' % key, hyper_params[key])
        for dictionary in hyper_dict:
            for key in dictionary:
                self.__setattr__('_%s' % key, dictionary[key])

    def get_method_name(self):
        return self._method_name

    def get_method_summary(self):
        return '%s_%d' % (self._method_name, self._d)

    def learn_embedding(self, graph=None, edge_f=None,
                        is_weighted=False, no_python=False):
        args = ["gem/c_exe/node2vec"]
        if not graph and not edge_f:
            raise Exception('graph/edge_f needed')
        if edge_f:
            graph = graph_util.loadGraphFromEdgeListTxt(edge_f)
        graphFileName = 'gem/intermediate/%s_n2v.graph' % self._data_set
        embFileName = 'gem/intermediate/%s_%d_n2v.emb' % (
            self._data_set, self._d)
        try:
            f = open(graphFileName, 'r')
            f.close()
        except IOError:
            graph_util.saveGraphToEdgeListTxtn2v(graph, graphFileName)
        args.append("-i:%s" % graphFileName)
        args.append("-o:%s" % embFileName)
        args.append("-d:%d" % self._d)
        args.append("-l:%d" % self._walk_len)
        args.append("-r:%d" % self._num_walks)
        args.append("-k:%d" % self._con_size)
        args.append("-e:%d" % self._max_iter)
        args.append("-p:%f" % self._ret_p)
        args.append("-q:%f" % self._inout_p)
        args.append("-v")
        args.append("-dr")
        args.append("-w")
        t1 = time()
        try:
            call(args)
        except Exception as e:
            print(str(e))
            raise Exception(
                './node2vec not found. Please compile snap, place node2vec in the path and grant executable permission')
        self._X = graph_util.loadEmbedding(embFileName)
        t2 = time()
        call(["rm", embFileName])
        return self._X, (t2 - t1)

    def get_embedding(self):
        return self._X

    def get_edge_weight(self, i, j):
        return np.dot(self._X[i, :], self._X[j, :])

    def get_reconstructed_adj(self, X=None, node_l=None):
        if X is not None:
            node_num = X.shape[0]
            self._X = X
        else:
            node_num = self._node_num
        adj_mtx_r = np.zeros((node_num, node_num))
        for v_i in range(node_num):
            for v_j in range(node_num):
                if v_i == v_j:
                    continue
                adj_mtx_r[v_i, v_j] = self.get_edge_weight(v_i, v_j)
        return adj_mtx_r


if __name__ == '__main__':
    # load Zachary's Karate graph
    edge_f = 'data/karate.edgelist'
    G = graph_util.loadGraphFromEdgeListTxt(edge_f, directed=False)
    G = G.to_directed()
    res_pre = 'results/testKarate'
    graph_util.print_graph_stats(G)
    t1 = time()
    embedding = node2vec(2, 1, 80, 10, 10, 1, 1)
    embedding.learn_embedding(graph=G, edge_f=None,
                              is_weighted=True, no_python=True)
    print('node2vec:\n\tTraining time: %f' % (time() - t1))

    viz.plot_embedding2D(embedding.get_embedding(),
                         di_graph=G, node_colors=None)
    plt.show()
