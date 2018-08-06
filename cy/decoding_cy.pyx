# cython: infer_types=True
cimport cython
cimport numpy as np
import numpy as np
#from scipy.special import logsumexp

cdef extern from "math.h":
    double log(double m)
    double exp(double m)

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

cdef double LOG_0 = -9999
cdef double LOG_1 = 0

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(True)   # Deactivate negative indexing.
def forward_vec_log(int s, int i, double [:,:] y, double [:] previous=None):
    '''
    Arguments:
        s: character index
        i: label index
        y: softmax probabilities
        previous: last column
    1d forward algorithm: Just calculates one column on the character s.
    '''

    cdef Py_ssize_t t_max = y.shape[0]
    cdef Py_ssize_t t

    fw_np = np.zeros(t_max, dtype=DTYPE) + LOG_0
    cdef double [:] fw = fw_np

    assert(i==0 or previous is not None)

    for t in range(t_max):
        if i==0:
            if t==0:
                fw[t] = y[t,s]
            else:
                fw[t] = y[t,-1]+fw[t-1]
        elif t==0:
            if i==1:
                fw[t] = y[t,s]
        else:
            fw[t] = log(exp(y[t,-1]+fw[t-1]) + exp(y[t,s]+previous[t-1]))
    return(fw_np)

# define optmized math functions using exp and log from math.h
cdef double sum(double [:] x):
    cdef Py_ssize_t x_max = x.shape[0]
    cdef double total = 0
    cdef Py_ssize_t i
    for i in range(x_max):
        total += x[i]
    return(total)

cpdef double logsumexp(double [:] x):
    cdef Py_ssize_t x_max = x.shape[0]
    cdef double total = 0
    cdef Py_ssize_t i
    for i in range(x_max):
        total += exp(x[i])
    return(log(total))

@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def pair_gamma_log(double [:,:] y1, double [:,:] y2):

    cdef Py_ssize_t U = y1.shape[0]
    cdef Py_ssize_t V = y2.shape[0]
    cdef Py_ssize_t alphabet_size = y1.shape[1]
    cdef Py_ssize_t u, v, t

    # intialization
    cdef np.ndarray[DTYPE_t, ndim=2] gamma_np = np.zeros(shape=(U+1,V+1), dtype=DTYPE) + LOG_0
    cdef double [:,:] gamma_ = gamma_np

    cdef np.ndarray[DTYPE_t, ndim=2] gamma_ast_np = np.zeros(shape=(U+1,V+1), dtype=DTYPE) + LOG_0
    cdef double [:,:] gamma_ast = gamma_ast_np
    cdef double gamma_eps, gamma_ast_eps, gamma_ast_ast

    gamma_[U,V] = LOG_1
    gamma_ast[U,V] = LOG_1

    for v in range(V):
        gamma_[U,v] = sum(y2[v:,alphabet_size-1])
    for u in range(U):
        gamma_[u,V] = sum(y1[u:,alphabet_size-1])

    for u in reversed(range(U)):
        for v in reversed(range(V)):
            # individual recursions
            gamma_eps = gamma_[u+1,v] + y1[u,alphabet_size-1]
            gamma_ast_eps = gamma_ast[u,v+1] + y2[v,alphabet_size-1]

            # method 1
            #total1 = logsumexp(np.add(y1[u,:alphabet_size-1], y2[v,:alphabet_size-1]))

            # method 2
            total2 = 0
            for t in range(0,alphabet_size-1):
                total2 += exp(y1[u,t]+y2[v,t])

            gamma_ast_ast = gamma_[u+1,v+1] + log(total2)

            # storing DP matrices
            gamma_ast[u,v] = log(exp(gamma_ast_eps) + exp(gamma_ast_ast))
            gamma_[u,v] = log(exp(gamma_eps) + exp(gamma_ast[u,v]))

    return(gamma_np)

# doesn't seem to be faster than vectorized numpy
@cython.boundscheck(False)  # Deactivate bounds checking
@cython.wraparound(False)   # Deactivate negative indexing.
def pair_prefix_prob_log(double [:,:] alpha_ast_ast, double [:,:] gamma):
    cdef Py_ssize_t U = alpha_ast_ast.shape[0]
    cdef Py_ssize_t V = alpha_ast_ast.shape[1]
    cdef Py_ssize_t u, v
    cdef double prefix_prob = 0
    for v in range(V):
        for u in range(U):
            prefix_prob += exp(alpha_ast_ast[u,v] + gamma[u+1,v+1])
    return(log(prefix_prob) - gamma[0,0])
