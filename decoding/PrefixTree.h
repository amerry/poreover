#ifndef PREFIX_TREE_HPP
#define PREFIX_TREE_HPP

#include <string>
#include <iostream>
#include <vector>
#include <algorithm>
#include <unordered_map>
#include <limits>
#include <functional>
#include <cmath>

#include "Log.h"

#define DEFAULT_VALUE -std::numeric_limits<double>::infinity()

template <class N>
class Node {
public:
  int last;
  N* parent;
  std::vector<N*> children;
  int depth = 0;

  Node(int s, N* p) :last{s}, parent{p} {}
  Node(int s) :last{s}, parent{nullptr} {}
  Node() :last{-1}, parent{nullptr} {}

  int get_last() const { return last; }
  N* get_parent() const { return parent; }

  N* add_child(int c) {
    N* child = new N(c);
    child->parent = static_cast<N*>(this);
    child->depth = this->depth + 1;
    children.push_back(child);
    return child;
  }
};

class PoreOverNode : public Node<PoreOverNode> {
public:
  std::unordered_map<int, double> probability;
  int max_t = 0;

  PoreOverNode(int s, PoreOverNode* p) : Node<PoreOverNode>(s, p) {}
  PoreOverNode(int s) : Node<PoreOverNode>(s) {}
  PoreOverNode() : Node<PoreOverNode>() {}

  double probability_at(int t) const {
   if (probability.count(t) > 0) {
     return probability.at(t);
   } else {
     return DEFAULT_VALUE;
   }
 }

 double last_probability() const {
   return probability.at(max_t);
 }

 void set_probability(int t, double val) {
   probability[t] = val;
   max_t = t;
 }

};

class PoreOverNode2D : public Node<PoreOverNode2D> {
public:
  static const int dim = 2;
  std::unordered_map<int, double> probability[dim];
  int last_t[dim] = {0, 0};

  PoreOverNode2D(int s, PoreOverNode2D* p) : Node<PoreOverNode2D>(s, p) {}
  PoreOverNode2D(int s) : Node<PoreOverNode2D>(s) {}
  PoreOverNode2D() : Node<PoreOverNode2D>() {}

  double probability_at(int n, int t) const {
   if (probability[n].count(t) > 0) {
     return probability[n].at(t);
   } else {
     return DEFAULT_VALUE;
   }
 }

 double probability_at(int t) const {
    return probability_at(0, t) + probability_at(1, t);
}

double joint_probability(int u, int v) const {
   return probability_at(0, u) + probability_at(1, v);
}

 double last_probability() const {
   double prob_sum = 0;
   for (int n=0; n<dim; ++n) {
     prob_sum += probability[n].at(last_t[n]);
   }
   return prob_sum;
    //return probability[0].at(last_t[0]) + probability[1].at(last_t[1]); //2D case
 }

 void set_probability(int i, int t, double val) {
   probability[i][t] = val;
   last_t[i] = t;
 }

};


class FlipFlopNode : public Node<FlipFlopNode>{
public:
  std::unordered_map<int, double> probability;
  std::unordered_map<int, double> probability_flip;
  std::unordered_map<int, double> probability_flop;
  int max_t = 0;

  FlipFlopNode(int s, FlipFlopNode* p) : Node<FlipFlopNode>(s, p) {}
  FlipFlopNode(int s) : Node<FlipFlopNode>(s) {}
  FlipFlopNode() : Node<FlipFlopNode>() {}

   double probability_at(int t) const {
    if (probability.count(t) > 0) {
      return probability.at(t);
    } else {
      return DEFAULT_VALUE;
    }
  }

  double probability_flip_at(int t) const {
   if (probability_flip.count(t) > 0) {
     return probability_flip.at(t);
   } else {
     return DEFAULT_VALUE;
   }
 }

   double probability_flop_at(int t) const {
    if (probability_flop.count(t) > 0) {
      return probability_flop.at(t);
    } else {
      return DEFAULT_VALUE;
    }
  }

  double last_probability() const {
    return probability.at(max_t);
  }

  void set_probability(int t, double flip_val, double flop_val) {
    probability[t] = logaddexp(flip_val, flop_val);
    probability_flip[t] = flip_val;
    probability_flop[t] = flop_val;
    max_t = t;
  }

};

template <class T>
bool node_greater(T n1, T n2) {
  return (n1->last_probability() > n2->last_probability());
}

template <class TNode>
class PrefixTree {
public:
    std::string alphabet;
    TNode root;

    PrefixTree(std::string a) : alphabet{a} {}

    // expand children if node hasn't been expanded
    std::vector<TNode> expand(TNode n) {
      if (n->children.size() == 0) {
        for (int i=0; i < alphabet.length(); i++) {
          n->add_child(i);
        }
      }
      return n->children;
    }

    // trace path back to root and output label
    std::string get_label(TNode n) {
      std::string label = "";
      TNode prefix = n;
      while (prefix) {
        label = alphabet[prefix->last] + label;
        prefix = prefix->parent;
      }
      return label;
    }

};

class PoreOverPrefixTree : public PrefixTree<PoreOverNode*> {
public:
  int gap_char;
  int t_max;
  double **y;

  PoreOverPrefixTree(double **d, int v, std::string a) : PrefixTree<PoreOverNode*>(a), y{d}, t_max{v} {
    gap_char = alphabet.length();
    root = new PoreOverNode(gap_char);
    root->probability[-1] = 0;
    double blank_sum = 0;
    for (int i=0; i<t_max; i++) {
      blank_sum += y[i][gap_char];
      root->probability[i] = blank_sum;
    }
  }

  void update_prob(PoreOverNode* n, int t) {
    double a = n->parent->probability_at(t-1);
    double b = y[t][n->last];
    double emit_state = a+b;

    double c = n->probability_at(t-1);
    double d = y[t][gap_char];
    double stay_state = c+d;

    n->set_probability(t, logaddexp(emit_state, stay_state));
  }

};

class PoreOverPrefixTree2D : public PrefixTree<PoreOverNode2D*> {
public:
  static const int dim = 2;
  int gap_char;
  int t_max[dim];
  double **y[dim];

  PoreOverPrefixTree2D(double **d1, int u, double **d2, int v, std::string a) : PrefixTree<PoreOverNode2D*>(a) {
    y[0] = d1;
    y[1] = d2;
    t_max[0] = u;
    t_max[1] = v;
    gap_char = alphabet.length();
    root = new PoreOverNode2D(gap_char);
    root->probability[0][-1] = 0;
    root->probability[1][-1] = 0;
    for (int i=0; i<dim; ++i) {
      double blank_sum = 0;
      for (int t=0; t<t_max[i]; ++t) {
        blank_sum += y[i][t][gap_char];
        root->probability[i][t] = blank_sum;
      }
    }

  }

  void update_prob(PoreOverNode2D* n, int i, int t) {

    if (n->probability[i].count(t) == 0) {
      double a = n->parent->probability_at(i, t-1);
      double b = y[i][t][n->last];
      double emit_state = a+b;

      double c = n->probability_at(i, t-1);
      double d = y[i][t][gap_char];
      double stay_state = c+d;

      n->set_probability(i, t, logaddexp(emit_state, stay_state));
    }
  }

};

class FlipFlopPrefixTree : public PrefixTree<FlipFlopNode*> {
public:
  int flipflop_size = alphabet.length();
  int t_max;
  double **y;

  FlipFlopPrefixTree(double **d, int v, std::string a) : PrefixTree<FlipFlopNode*>(a), y{d}, t_max{v} {
    root = new FlipFlopNode(flipflop_size);
    root->probability[-1] = 0;
    root->probability_flip[-1] = log(0.5);
    root->probability_flop[-1] = log(0.5);
  }

  void update_prob(FlipFlopNode* n, int t) {
    double stay_flip = n->probability_flip_at(t-1) + y[t][n->last];
    double stay_flop = n->probability_flop_at(t-1) + y[t][n->last + flipflop_size];

    double emit_flip, emit_flop;

    if (n->parent->last == n->last) {
      emit_flip = n->parent->probability_flop_at(t-1) + y[t][n->last];
      emit_flop = n->parent->probability_flip_at(t-1) + y[t][n->last + flipflop_size];
    } else {
      emit_flip = logaddexp(n->parent->probability_flip_at(t-1), n->parent->probability_flop_at(t-1)) + y[t][n->last];
      emit_flop = DEFAULT_VALUE;
    }

    n->set_probability(t, logaddexp(emit_flip, stay_flip), logaddexp(emit_flop, stay_flop));
  }

};

#endif
