#include "util.h"

namespace algebra {

    enum ExpressionType {
        Constant,   // C
        Variable,   // x
        Function,   // f(x)
        Sum,        // x + y
        Product,    // xy
        Power,      // x^y
        Poly,       // x^n
        Exp,        // e^x
        Ratio,      // x/y
        Logarithm,  // ln(x)
        Derivative, // df/dx
    };

    class Expression {

        private:

            ExpressionType exprt;

            // Numerical coefficient applied to everything
            // - also the value of a Constant
            double coefficient;
           
            // Sums
            Expression* summand1;
            Expression* summand2;

            // Powers
            Expression* base;
            Expression* exponent;

            // Ratios
            Expression* numerator;
            Expression* denominator;

            // Logarithms
            Expression* logarithm;

        public:

            Expression(double coefficient, ExpressionType op, Expression a) {
                if (op == Exponent)
            }
            Expression(double coefficient, Expression a, ExpressionType op, Expression b) {

            }

            ExpressionType type() { return exprt; }

    };

};