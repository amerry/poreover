'''
Unit tests for decoding algorithms
'''

import unittest
import numpy as np
from collections import OrderedDict
from testing import poreover, poreover_profile, joint_profile
import poreover.decoding.prefix_search as prefix_search

class TestForwardAlgorithm(unittest.TestCase):

    def test_label_prob_log(self):
        alphabet = ('A','B','')
        alphabet_dict = {'A':0,'B':1,'':2}

        y = np.array([[0.8,0.1,0.1],[0.1,0.3,0.6],[0.7,0.2,0.1],[0.1,0.1,0.8]])
        examples = ['AAAA','ABBA','ABA','AA','BB','A','B']
        prof=poreover_profile(y,alphabet)

        for label in examples:
            label_int = [alphabet_dict[i] for i in label]
            alpha  = prefix_search.forward(label_int, np.log(y))
            self.assertTrue(np.isclose(alpha[-1,-1], np.log(prof.label_prob(label))))

    def test_label_prob_log_cy(self):
        alphabet = ('A','B','')
        alphabet_dict = {'A':0,'B':1,'':2}

        y = np.array([[0.8,0.1,0.1],[0.1,0.3,0.6],[0.7,0.2,0.1],[0.1,0.1,0.8]], dtype=np.float32)
        examples = ['AAAA','ABBA','ABA','AA','BB','A','B']
        prof=poreover_profile(y,alphabet)

        for label in examples:
            label_int = [alphabet_dict[i] for i in label]
            alpha  = prefix_search.forward(label_int, np.log(y))
            print('CYTHON', alpha[-1,-1],  np.log(prof.label_prob(label)))
            self.assertTrue(np.isclose(alpha[-1,-1], np.log(prof.label_prob(label))))

    def test_prefix_prob_log(self):

        def logsumexp(x):
            from functools import reduce
            return(reduce(np.logaddexp, x))

        alphabet = ('A','B','')
        alphabet_dict = {'A':0,'B':1,'':2}

        def helper(y,l):
            label_int = [alphabet_dict[i] for i in label]
            prof = poreover_profile(y,alphabet)
            alpha  = prefix_search.forward(label_int, np.log(y))
            prefix_prob = logsumexp(prefix_search.forward_vec_no_gap_log(label_int,np.log(y),alpha[-2]))
            print(prefix_prob, prof.prefix_prob(label))
            self.assertTrue(np.isclose(prefix_prob, np.log(prof.prefix_prob(label))))

        y = np.array([[0.8,0.1,0.1],[0.1,0.3,0.6],[0.7,0.2,0.1],[0.1,0.1,0.8]])
        examples = ['AAAA','ABBA','ABA','AA','BB','A','B']

        for label in examples:
            helper(y,label)

class TestDecoding(unittest.TestCase):

    def test_prefix_search_log(self):

        def helper(y):
            alphabet = ('A','B','')
            toy_alphabet = OrderedDict([('A',0),('B',1)])
            prof = poreover_profile(y,alphabet)
            top_label = prof.top_label()
            search_top_label = prefix_search.prefix_search_log(np.log(y),alphabet=toy_alphabet)
            print(top_label[0],np.log(top_label[1]), search_top_label[0],search_top_label[1])
            return((top_label[0] == search_top_label[0]) and np.isclose(np.log(top_label[1]), search_top_label[1]))

        y = np.array([[0.1,0.6,0.3],[0.4,0.2,0.4],[0.4,0.3,0.3],[0.2,0.8,0]])
        self.assertTrue(helper(y))

        y = np.array([[0.7,0.2,0.1],[0.2,0.3,0.5],[0.7,0.2,0.1],[0.05,0.05,0.9]])
        self.assertTrue(helper(y))

        y = np.array([[0.7,0.2,0.1],[0.2,0.3,0.5]])
        self.assertTrue(helper(y))

class TestPairDecoding(unittest.TestCase):

    '''
    def test_pair_label_prob(self):
        alphabet = ('A','B','')
        alphabet_dict = {'A':0,'B':1,'':2}

        y1 = np.array([[0.8,0.1,0.1],[0.1,0.3,0.6],[0.7,0.2,0.1],[0.1,0.1,0.8]])
        y2 = np.array([[0.7,0.2,0.1],[0.2,0.3,0.5],[0.7,0.2,0.1],[0.05,0.05,0.9]])
        examples = ['AAAA','ABBA','ABA','AA','BB','A','B']

        profile1=poreover_profile(y1,alphabet)
        profile2=poreover_profile(y2,alphabet)
        joint_prof = joint__profile(profile1, profile2)

        for label in examples:
            label_int = [alphabet_dict[i] for i in label]
            alpha,_,_  = prefix_search.pair_forward(label_int,y1,y2)
            self.assertTrue(np.isclose(pair_label_prob(alpha), joint_prof.label_prob(label)))
    '''

    def test_pair_prefix_search_log(self):
        def helper(y1,y2):
            alphabet = ('A','B','')
            toy_alphabet = OrderedDict([('A',0),('B',1)])

            profile1= poreover_profile(y1,alphabet)
            profile2=poreover_profile(y2,alphabet)
            joint_prof = joint_profile(profile1, profile2)

            top_label = joint_prof.top_label()
            search_top_label = prefix_search.pair_prefix_search_log(np.log(y1),np.log(y2),alphabet=toy_alphabet)

            print(top_label[0],np.log(top_label[1] / joint_prof.prob_agree), search_top_label[0],search_top_label[1])
            return((top_label[0] == search_top_label[0]) and np.isclose(np.log(top_label[1] / joint_prof.prob_agree), search_top_label[1]))

        y1 = y2 = np.array([[0.1,0.6,0.3],[0.4,0.2,0.4],[0.4,0.3,0.3],[0.2,0.8,0]])
        self.assertTrue(helper(y1,y2))

        y1 = np.array([[0.8,0.1,0.1],[0.1,0.3,0.6],[0.7,0.2,0.1],[0.1,0.1,0.8]])
        y2 = np.array([[0.7,0.2,0.1],[0.2,0.3,0.5],[0.7,0.2,0.1],[0.05,0.05,0.9]])
        self.assertTrue(helper(y1,y2))

        y1 = np.array([[0.8,0.1,0.1],[0.1,0.3,0.6],[0.7,0.2,0.1],[0.1,0.1,0.8]])
        y2 = np.array([[0.7,0.2,0.1],[0.2,0.3,0.5]])
        self.assertTrue(helper(y1,y2))

        y1 = y2 = np.array([[0,0,1],[1,0,0],[0,1,0]])
        self.assertTrue(helper(y1,y2))

    def test_pair_prefix_search_log_cy(self):
        def helper(y1,y2):
            alphabet = ('A','B','')
            toy_alphabet = OrderedDict([('A',0),('B',1)])

            profile1= poreover_profile(y1,alphabet)
            profile2=poreover_profile(y2,alphabet)
            joint_prof = joint_profile(profile1, profile2)

            top_label = joint_prof.top_label()
            search_top_label = prefix_search.pair_prefix_search_log_cy(np.log(y1),np.log(y2),alphabet=toy_alphabet)

            print(top_label[0],np.log(top_label[1] / joint_prof.prob_agree), search_top_label[0],search_top_label[1])
            return((top_label[0] == search_top_label[0]) and np.isclose(np.log(top_label[1] / joint_prof.prob_agree), search_top_label[1]))

        y1 = y2 = np.array([[0.1,0.6,0.3],[0.4,0.2,0.4],[0.4,0.3,0.3],[0.2,0.8,0]])
        self.assertTrue(helper(y1,y2))

        y1 = np.array([[0.8,0.1,0.1],[0.1,0.3,0.6],[0.7,0.2,0.1],[0.1,0.1,0.8]])
        y2 = np.array([[0.7,0.2,0.1],[0.2,0.3,0.5],[0.7,0.2,0.1],[0.05,0.05,0.9]])
        self.assertTrue(helper(y1,y2))

        y1 = np.array([[0.8,0.1,0.1],[0.1,0.3,0.6],[0.7,0.2,0.1],[0.1,0.1,0.8]])
        y2 = np.array([[0.7,0.2,0.1],[0.2,0.3,0.5]])
        self.assertTrue(helper(y1,y2))

        y1 = y2 = np.array([[0,0,1],[1,0,0],[0,1,0]])
        self.assertTrue(helper(y1,y2))

    def test_prob_agree_log(self):
        def helper(y1,y2):
            alphabet = ('A','B','')
            toy_alphabet = OrderedDict([('A',0),('B',1)])
            profile1= poreover_profile(y1,alphabet)
            profile2=poreover_profile(y2,alphabet)
            joint_prof = joint_profile(profile1, profile2)

            gamma = prefix_search.pair_gamma_log(np.log(y1),np.log(y2))
            print('log(Z):',gamma[0,0],np.log(joint_prof.prob_agree))
            self.assertTrue(np.isclose(gamma[0,0], np.log(joint_prof.prob_agree)))

        y1 = np.array([[0.8,0.1,0.1],[0.1,0.3,0.6],[0.7,0.2,0.1],[0.1,0.1,0.8]])
        y2 = np.array([[0.7,0.2,0.1],[0.2,0.3,0.5],[0.7,0.2,0.1],[0.05,0.05,0.9]])
        helper(y1,y2)

        y1 = np.array([[0.8,0.1,0.1],[0.1,0.3,0.6],[0.7,0.2,0.1],[0.1,0.1,0.8]])
        y2 = np.array([[0.7,0.2,0.1],[0.2,0.3,0.5]])
        helper(y1,y2)

        y1 = y2 = np.array([[0,0,1],[1,0,0],[0,1,0]])
        helper(y1,y2)

    def test_prob_agree_log_cy(self):
        def helper(y1,y2):
            alphabet = ('A','B','')
            toy_alphabet = OrderedDict([('A',0),('B',1)])
            profile1= poreover_profile(y1,alphabet)
            profile2=poreover_profile(y2,alphabet)
            joint_prof = joint_profile(profile1, profile2)

            gamma = prefix_search.decoding_cy.pair_gamma_log(np.log(y1).astype(np.float64),np.log(y2).astype(np.float64))
            print('log(Z):',gamma[0,0],np.log(joint_prof.prob_agree))
            self.assertTrue(np.isclose(gamma[0,0], np.log(joint_prof.prob_agree)))

        y1 = np.array([[0.8,0.1,0.1],[0.1,0.3,0.6],[0.7,0.2,0.1],[0.1,0.1,0.8]])
        y2 = np.array([[0.7,0.2,0.1],[0.2,0.3,0.5],[0.7,0.2,0.1],[0.05,0.05,0.9]])
        helper(y1,y2)

        y1 = np.array([[0.8,0.1,0.1],[0.1,0.3,0.6],[0.7,0.2,0.1],[0.1,0.1,0.8]])
        y2 = np.array([[0.7,0.2,0.1],[0.2,0.3,0.5]])
        helper(y1,y2)

        y1 = y2 = np.array([[0,0,1],[1,0,0],[0,1,0]])
        helper(y1,y2)

class TestUtils(unittest.TestCase):

    def test_remove_gaps(self):
        self.assertEqual(prefix_search.remove_gaps(['A','','B']), 'AB')
        self.assertEqual(prefix_search.remove_gaps(['A','-','B']), 'AB')
        self.assertEqual(prefix_search.remove_gaps(['-','A','A','-','','-','B']), 'AAB')
        self.assertEqual(prefix_search.remove_gaps('A-B'),'AB')

    def test_greedy_search(self):
        alphabet = ['A','B','-']

        y = np.array([[0.5,0.1,0.4],[0.5,0.1,0.4],[0.5,0.1,0.4],[0.,0.1,0.9]])
        self.assertEqual(prefix_search.greedy_search(y, alphabet),'AAA')

        y = np.array([[0.5,0.1,0.4]])
        self.assertEqual(prefix_search.greedy_search(y, alphabet),'A')

        y = np.array([[0,0,1]])
        self.assertEqual(prefix_search.greedy_search(y, alphabet),'')

        y = np.array([[0.5,0.5,0.]])
        self.assertEqual(prefix_search.greedy_search(y, alphabet),'A')

if __name__ == '__main__':
    unittest.main()
