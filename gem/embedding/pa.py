from gem.evaluation import visualize_embedding as viz
from gem.utils import graph_util, plot_util
from .static_graph_embedding import StaticGraphEmbedding
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
sys.path.append(os.path.realpath(__file__))


class PreferentialAttachment(StaticGraphEmbedding):
    """`Preferential Attachment`_.
    Preferential Attachment is based on the assumption that the connection to a 
    node is proportional to its degree. It defines the similarity 
    between the nodes as the product of their degrees.

    Args:
        hyper_dict (object): Hyper parameters.
        kwargs (dict): keyword arguments, form updating the parameters

    Examples:
        >>> from gemben.embedding.pa import PreferentialAttachment
        >>> edge_f = 'data/karate.edgelist'
        >>> G = graph_util.loadGraphFromEdgeListTxt(edge_f, directed=False)
        >>> G = G.to_directed()
        >>> res_pre = 'results/testKarate'
        >>> graph_util.print_graph_stats(G)
        >>> t1 = time()
        >>> embedding = PreferentialAttachment(2)
        >>> embedding.learn_embedding(graph=G, edge_f=None,
                                  is_weighted=True, no_python=True)
        >>> print('PreferentialAttachment:Training time: %f' % (time() - t1))
        >>> viz.plot_embedding2D(embedding.get_embedding(),
                             di_graph=G, node_colors=None)
        >>> plt.show()
    .. _Preferential Attachment:
        https://science.sciencemag.org/content/286/5439/509
    """

    def __init__(self, *hyper_dict, **kwargs):
        ''' Initialize the PreferentialAttachment class

        Args:
            d: dimension of the embedding
        '''
        hyper_params = {
            'method_name': 'preferential_attachment'
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
        if not graph and not edge_f:
            raise Exception('graph/edge_f needed')
        if not graph:
            graph = graph_util.loadGraphFromEdgeListTxt(edge_f)
        graph = graph.to_undirected()
        t1 = time()
        self._X = np.array(
            # list(graph.degree(graph.nodes()).values())
            list(dict(graph.degree()).values())
        ).reshape(graph.number_of_nodes(), 1)
        t2 = time()
        return self._X, (t2 - t1)

    def get_embedding(self):
        return self._X

    def get_edge_weight(self, i, j):
        return self._X[i] * self._X[j]

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
    embedding = PreferentialAttachment(2)
    embedding.learn_embedding(graph=G, edge_f=None,
                              is_weighted=True, no_python=True)
    print('PreferentialAttachment:\n\tTraining time: %f' % (time() - t1))

    viz.plot_embedding2D(embedding.get_embedding(),
                         di_graph=G, node_colors=None)
    plt.show()
