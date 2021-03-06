#ifndef LOG_HPP
#define LOG_HPP

#include <limits>
#include <cmath>

#define DEFAULT_VALUE -std::numeric_limits<double>::infinity()

double log_(double x) {
  if (x > 0) {
    return (std::log(x));
  } else {
    return (DEFAULT_VALUE);
  }
}

double logaddexp(double x1, double x2) {
  if (x1 >= x2) {
    return(x1 + log_(1 + exp(x2-x1)));
  } else {
    return(x2 + log_(1 + exp(x1-x2)));
  }
}

#endif
