#include "dependencies.h"

namespace geometry {

	class MetricTensor {

		private:

			data::RecursiveArray<Expression> covariantTensor;
			Matrix covariant;
			data::RecursiveArray<Expression> contravariantTensor;
			Matrix contravariant;

		public:

			MetricTensor() {}
			MetricTensor(initializer_list<initializer_list<Expression>> values, int dimension=4) {
				covariant = Matrix(4, 4, values);
				contravariant = covariant.inverse();

				for (i = 0; i < dimension; i++) {
					for (j = 0; j < dimension; j++) {
						covariantTensor.get({i, j}) = covariant(i, j);
						contravariantTensor.get({i, j}) = contravariant(i, j);
					}
				}
			}

	};

	class Tensor {

		private:

			data::RecursiveArray<Expression> covariantTensor;
			data::RecursiveArray<bool> covariantTensorComputed;
			data::RecursiveArray<Expression> contravariantTensor;
			data::RecursiveArray<bool> contravariantTensorComputed;
			data::RecursiveArray<Expression> mixedTensor;
			data::RecursiveArray<bool> mixedTensorComputed;

		public:

			Tensor() {
				covariantTensorComputed.setAll(false);
				contravariantTensorComputed.setAll(false);
				mixedTensorComputed.setAll(false);
			}

			virtual int rank() const rank() = 0;
			
			Expression& co(initializer_list<int> indices) { 
				if (not covariantTensorComputed.get(indices)) {
					
				}
				return covariantTensor.get(indices); 
			}

			Expression& contra(initializer_list<int> indices) { 
				return contravariantTensor.get(indices); 
			}

			Expression& mixed(initializer_list<int> indices) { 
				return mixedTensor.get(indices); 
			}

	};

};