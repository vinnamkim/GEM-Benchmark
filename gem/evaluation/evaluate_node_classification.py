try: import cPickle as pickle
except: import pickle
from sklearn import model_selection as sk_ms
from sklearn.multiclass import OneVsRestClassifier as oneVr
from sklearn.linear_model import LogisticRegression as lr
# from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score
import numpy as np
import pdb


class TopKRanker(oneVr):
    """Class to get top K ranks."""

    def predict(self, X, top_k_list):
        """This function returns the prediction for top k node labels.
        Args:
            X (Vector): Embedding of the nodes.
            top_k_list (List): list consisting of value to denote top k.
        Returns:
            Numpy Array: Predicted node labels.
        """
        assert X.shape[0] == len(top_k_list)
        probs = np.asarray(super(TopKRanker, self).predict_proba(X))
        prediction = np.zeros((X.shape[0], self.classes_.shape[0]))
        for i, k in enumerate(top_k_list):
            probs_ = probs[i, :]
            labels = self.classes_[probs_.argsort()[-int(k):]].tolist()
            for label in labels:
                prediction[i, label] = 1
        return prediction


def evaluateNodeClassification(X, Y, test_ratio):
    """This function is used to evaluate node classification.
        Args:
            X (Vector) : Embedding values of the nodes.
            Y (Int) : Labels of the nodes.
            test_ratio (Float): Ratio to split the training and testing nodes.
        Returns:
            Numpy Array: Micro and macro accuracy scores.
    """
    X_train, X_test, Y_train, Y_test = sk_ms.train_test_split(
        X,
        Y,
        test_size=test_ratio
    )
    try:
        top_k_list = list(Y_test.toarray().sum(axis=1))
    except:
        top_k_list = list(Y_test.sum(axis=1))
    classif2 = TopKRanker(lr())
    try:
        classif2.fit(X_train, Y_train)
        prediction = classif2.predict(X_test, top_k_list)
    except:
        print('Could not fit node classification model')
        prediction = np.zeros(Y_test.shape)
    micro = f1_score(Y_test, prediction, average='micro')
    macro = f1_score(Y_test, prediction, average='macro')
    return (micro, macro)


def expNC(X, Y, test_ratio_arr,
          rounds, res_pre, m_summ):
    """This function is used to experiment node classification.
        Args:
            X (vector): Embedding values of the nodes.
            Y (Int): Labels of the nodes.
            rounds (Int): The number of times the graph reconstruction is performed.
            res_pre (Str): Prefix to be used to save the result.
            test_ratio_arr (Float): The split used for dividing the traing and testing data.
            m_summ (Str): String to denote the name of the summary file. 
        Returns:
            Numpy Array: Average accuracy.
    """
    print('\tNode Classification:')
    summ_file = open('%s_%s.ncsumm' % (res_pre, m_summ), 'w')
    summ_file.write('Method\t%s\n' % ('\t'.join(map(str, test_ratio_arr))))
    micro = [None] * rounds
    macro = [None] * rounds

    # Remove data points with no class
    # nonZeroIndices = np.where(np.any(Y!=0, axis=1))[0]
    # Y = Y[nonZeroIndices, :]
    # X = X[nonZeroIndices, :]
    for round_id in range(rounds):
        micro_round = [None] * len(test_ratio_arr)
        macro_round = [None] * len(test_ratio_arr)
        for i, test_ratio in enumerate(test_ratio_arr):
            micro_round[i], macro_round[i] = evaluateNodeClassification(
                X,
                Y,
                test_ratio
            )
        micro[round_id] = micro_round
        macro[round_id] = macro_round

        
    pickle.dump([test_ratio_arr, micro, macro],
                open('%s_%s.nc' % (res_pre, m_summ), 'wb'))
    m_avg = (np.array(micro) + np.array(macro)) / 2.0   
        
    if len(test_ratio) > 1:
        summ_file.write('Micro-F1 LR\t%s\n' % ('\t'.join(map(str, micro[0]))))
        summ_file.write('Macro-F1 LR\t%s\n' % ('\t'.join(map(str, macro[0]))))
         # Return the average of micro and macro scores at middle value
        res = list(m_avg[:, len(m_avg) // 2])
    else:
        summ_file.write('Micro-F1 LR\t%s\n' % ('\t'.join(map(str, [np.mean(np.array(micro).reshape(1,len(micro)))]))))
        summ_file.write('Macro-F1 LR\t%s\n' % ('\t'.join(map(str, [np.mean(np.array(macro).reshape(1,len(macro)))]))))
        res = list(m_avg.reshape((1,len(m_avg)))[0])
    summ_file.close()
                        

    return res
