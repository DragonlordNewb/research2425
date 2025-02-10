#include "util.h"

namespace algebra {

    enum ExpressionType {
        Constant,     // C
        Variable,     // x
        Function,     // f(x)
        Sum,          // x + y
        PlusC,        // x + C (edge case of Sum)
        Product,      // xy
        Power,        // x^y
        Poly,         // x^n (edge case of Power)
        Exp,          // e^x (edge case of Power)
        Ratio,        // x/y
        Inv,          // 1/x (edge case of Ratio)
        Log,          // ln(x)
        Deriva,       // df/dx
        Diff,         // dx
        Transcend,    // sin(x)
        InvTrans,     // arcsin(x)
    };

    class Expression {

        private:

            ExpressionType exprt;

            // Numerical coefficient applied to everything
            // - also the value of a Constant
            double coefficient;

            // Variable/function name
            string var;
           
            // Sums
            Expression* summand1;
            Expression* summand2;
            double summandC;

            // Products
            Expression* term1;
            Expression* term2;

            // Powers
            Expression* base;
            Expression* exponent;
            double constantExponent; // constant base, for Poly cases
            double constantBase; // constant e^base, for Exp cases

            // Ratios
            Expression* numerator;
            Expression* denominator;

            // Logarithms and Transcends
            string expname;
            Expression* argument;

        public:

            Expression(double constantValue) {
                coefficient = constantValue;
                exprt = Constant;
            };

            Expression(string vn, double ce=1) {
                coefficient = ce;
                var = vn; 
                exprt = Variable;
            }

            // Constructor for unary operations (e.g. transcendental functions)
            Expression(Expression a, ExpressionType op) {

            }

            // Constructor for binary operations
            Expression(Expression a, ExpressionType op, Expression b, double ce=1) {
                coefficient = ce;

                if (op == Sum) { 
                    // Check if either operands are constants, if so do PlusC
                    // or straight addition if possible ...
                    exprt = PlusC;
                    if (b.type() == Constant) {
                        if (a.type() == Constant) {
                            Expression(a.coeff() + b.coeff());
                        } else {
                            summand1 = &a;
                            summandC = b.coeff();
                        }
                    } else if (a.type() == Constant) {
                        summand1 = &b;
                        summandC = a.coeff();
                    } else {
                        // ...otherwise, do a regular Sum.
                        exprt = Sum;
                        summand1 = &a;
                        summand2 = &b;
                    }
                }

                if (op == Product) {
                    // Check if either operands are constants, if so just change
                    // the coefficient ...
                    exprt = Constant;
                    if (a.type() == Constant) {
                        if (b.type() == Constant) {
                            Expression(a.coeff() * b.coeff());
                        } else {
                            Expression(*b);
                            coefficient *= a.coeff();
                        }
                    } else if (b.type() == Constant) {
                        a.coeff() = a.coeff() * b.coeff();
                    } else {
                        // ...otherwise, do a regular Product.
                        exprt = Product;
                        term1 = &a;
                        term2 = &b;
                    }
                }

                if (op == Power) {
                    // Check if either operands are constant, if so either change
                    // the coefficient or use a Poly/Exp edge-case optimization...
                    exprt = Power;
                    if (a.type() == Constant) {
                        if (b.type() == Constant) {
                            Expression(pow(a.coeff(), b.coeff()));
                        } else {
                            // ln(a.coeff()) e^b
                            exprt = Exp;
                            constantBase = a.coeff();
                            exponent = &b;
                        }
                    } else if (b.type() == Constant) {
                        exprt = Poly;
                        constantExponent = b.coeff();
                        base = &a;
                    } else {
                        // ...otherwise, do a regular Power.
                        exponent = &b;
                        base = &a;
                    }
                }
            }

            Expression operator+(Expression other) { return Expression(*this, Sum, other); }
            Expression operator*(Expression other) { return Expression(*this, Product, other); }
            Expression operator^(Expression other) { return Expression(*this, Power, other); }
            Expression operator/(Expression other) { return Expression(*this, Ratio, other); }

            ExpressionType type() { return exprt; }
            double& coeff() { return coefficient; }
            
            string repr(bool parenthesize=false) {
                stringstream ss("");

                if (type() == Diff) {
                    ss << coefficient << "d" << var;
                    return ss.str();
                }

                if (type() == Variable) {
                    ss << coefficient << var;
                    return ss.str();
                }

                if (type() == Constant) {
                    ss << coefficient;
                    return ss.str();
                }

                parenthesize = parenthesize or coefficient != 1;
                if (coefficient != 1) { ss << coefficient; }
                if (parenthesize) { ss << "("; }

                if (type() == Sum) {
                    ss << summand1->repr(true) << " + " << summand2->repr(true);
                }
                if (type() == Product) {
                    ss << term1->repr(true) << " * " << term2->repr(true);
                }
                if (type() == Power) {
                    ss << base->repr(true) << " ^ " << exponent->repr(true);
                }
                if (type() == Poly) {
                    ss << base->repr(true) << "^" << constantExponent;
                }
                if (type() == Exp) {
                    ss << "e^" << exponent->repr(true);
                }
                if (type() == Ratio) {
                    ss << numerator->repr(true) << " / " << denominator->repr(true);
                }

                if (parenthesize) { ss << ")"; }

                return ss.str();
            }

    };

};