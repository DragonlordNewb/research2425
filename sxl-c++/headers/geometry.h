#include "dependencies.h"

namespace geometry {

	class Dimensional {

		protected:

			int dimension;

		public:

			const int dim() {
				return dimension;
			}

	};

	class CoordinateSystem: public Dimensional {

		private:

			data::Array<Symbol> coordinates;

		public:

			CoordinateSystem() {}
			CoordinateSystem(initializer_list<std::string> labels) {
				data::Array<std::string> arr(labels);
				dimension = arr.getLength();
				coordinates = data::Array<Symbol>(dimension);
				for (int i = 0; i < dim(); i++) {
					coordinates[i] = Symbol(arr.get(i));
				}
			}

			Symbol& x(int index) { return coordinates.get(index); }

	};

	class MetricTensor: public Dimensional {

		private:

			data::RecursiveArray<Expression> covariantTensor;
			Matrix covariant;
			data::RecursiveArray<Expression> contravariantTensor;
			Matrix contravariant;
			CoordinateSystem coordinates;

		public:

			MetricTensor() {}
			MetricTensor(initializer_list<initializer_list<Expression>> values, CoordinateSystem _coordinates, int _dimension=4) {
				dimension = _dimension;
				covariant = Matrix(values);
				contravariant = covariant.inverse();
				coordinates = _coordinates;
				if (dim() != coordinates.dim()) {
					throw std::runtime_error("(SXL error code 3) Metric and coordinate system have incompatible dimensions.");
				}
				covariantTensor = data::RecursiveArray<Expression>(2, _dimension);
				contravariantTensor = data::RecursiveArray<Expression>(2, _dimension);

				for (int i = 0; i < dimension; i++) {
					for (int j = 0; j < dimension; j++) {
						covariantTensor.get({i, j}) = covariant(i, j);
						contravariantTensor.get({i, j}) = contravariant(i, j);
					}
				}
			}

			Expression co(initializer_list<int> indices) { return covariantTensor.get(indices); }
			Expression contra(initializer_list<int> indices) { return contravariantTensor.get(indices); }

	};

	class Tensor: public Dimensional {

		protected:

			data::RecursiveArray<Expression> covariantTensor;
			data::RecursiveArray<bool> covariantTensorComputed;
			data::RecursiveArray<Expression> contravariantTensor;
			data::RecursiveArray<bool> contravariantTensorComputed;
			data::RecursiveArray<Expression> mixedTensor;
			data::RecursiveArray<bool> mixedTensorComputed;

			MetricTensor metric;
			virtual Expression computeCovariant(initializer_list<int> indices) = 0;
			virtual Expression computeContravariant(initializer_list<int> indices) = 0;
			virtual Expression computeMixed(initializer_list<int> indices) = 0;
			int _rank;

		public:

			Tensor(MetricTensor _metric, int __rank) {
				if (__rank <= 0) {
					throw std::runtime_error("(SXL error code 5) Invalid tensor rank.");
				}
				_rank = __rank;
				metric = _metric;
				dimension = metric.dim();
				covariantTensor = data::RecursiveArray<Expression>(rank(), dim());
				covariantTensorComputed = data::RecursiveArray<bool>(rank(), dim());
				contravariantTensor = data::RecursiveArray<Expression>(rank(), dim());
				contravariantTensorComputed = data::RecursiveArray<bool>(rank(), dim());
				mixedTensor = data::RecursiveArray<Expression>(rank(), dim());
				mixedTensorComputed = data::RecursiveArray<bool>(rank(), dim());
				covariantTensorComputed.setAll(false);
				contravariantTensorComputed.setAll(false);
				mixedTensorComputed.setAll(false);
			}

			int rank() const { return _rank; }

			Expression co(initializer_list<int> indices) {
				if (not covariantTensorComputed.get(indices)) {
					covariantTensor.set(indices, computeCovariant(indices));
					covariantTensorComputed.set(indices, true);
				}
				return covariantTensor.get(indices); 
			}

			Expression contra(initializer_list<int> indices) { 
				if (not contravariantTensorComputed.get(indices)) {
					contravariantTensor.set(indices, computeContravariant(indices));
					contravariantTensorComputed.set(indices, true);
				}
				return contravariantTensor.get(indices); 
			}

			Expression mixed(initializer_list<int> indices) {
				if (not mixedTensorComputed.get(indices)) {
					mixedTensor.set(indices, computeMixed(indices));
					mixedTensorComputed.set(indices, true);
				}
				return mixedTensor.get(indices); 
			}

			void set_co(initializer_list<int> indices, Expression value) { covariantTensor.set(indices, value); covariantTensorComputed.set(indices, true); }
			void set_contra(initializer_list<int> indices, Expression value) { contravariantTensor.set(indices, value); contravariantTensorComputed.set(indices, true); }
			void set_mixed(initializer_list<int> indices, Expression value) { mixedTensor.set(indices, value); mixedTensorComputed.set(indices, true); }

	};

	class Rank1Tensor: public Tensor {

		// The rank-1 tensor (technically a vector) doesn't really care for the 
		// "mixed" array, so it just uses the contravariant and covariant, and
		// the .mixed method just returns the contravariant.

		protected:

			Expression computeCovariant(initializer_list<int> indices) override {
				int i = *(indices.begin()); // Get the first index

				// v_i = g_{ij} v^j	
				Expression result = 0;
				for (int j = 0; j < dim(); j++) {
					result += metric.co({i, j}) * contra({j});
				}
				return result;
			}

			Expression computeContravariant(initializer_list<int> indices) override {
				int i = *(indices.begin());

				// v^i = g^{ij} v_j
				Expression result = 0;
				for (int j = 0; j < dim(); j++) {
					result += metric.contra({i, j}) * co({j});
				}
				return result;
			}

			Expression computeMixed(initializer_list<int> indices) override {
				return contra(indices);
			}

		public:

			Rank1Tensor(MetricTensor _metric): Tensor::Tensor(_metric, 1) {}

			// Expression co(int i) { return co({i}); }
			// Expression contra(int i) { return contra({i}); }
			// Expression mixed(int i) { return mixed({i}); }

			// int rank() const override { return 1; }

	};

	class Rank2Tensor: public Tensor {

		protected:

			Expression computeCovariant(initializer_list<int> indices) override {
				int i = *(indices.begin()); // Get the first index
				int j = indices.begin()[1];

				// T_ij = g_{ik} T^k_j	
				Expression result = 0;
				for (int k = 0; k < dim(); k++) {
					result += metric.co({i, k}) * mixed({k, j});
				}
				return result;
			}

			Expression computeContravariant(initializer_list<int> indices) override {
				int i = *(indices.begin()); // Get the first index
				int j = indices.begin()[1];

				// T^ij = g^{ik} g^{jl} T_{kl}	
				Expression result = 0;
				for (int k = 0; k < dim(); k++) {
					for (int l = 0; l < dim(); l++) {
						result += metric.contra({i, k}) * metric.contra({j, l}) * co({k, l});
					}
				}
				return result;
			}

			Expression computeMixed(initializer_list<int> indices) override {
				int i = *(indices.begin()); // Get the first index
				int j = indices.begin()[1];

				// T^i_j = g_{jk} T^{ik}	
				Expression result = 0;
				for (int k = 0; k < dim(); k++) {
					result += metric.co({j, k}) * contra({i, k});
				}
				return result;
			}

		public:

			Rank2Tensor(MetricTensor _metric): Tensor::Tensor(_metric, 2) {}

			// Expression co(int i, int j) { return co({i, j}); }
			// Expression contra(int i, int j) { return contra({i, j}); }
			// Expression mixed(int i, int j) { return mixed({i, j}); }

			// int rank() const override { return 2; }

	};

	class Rank3Tensor: public Tensor {

		protected:

			Expression computeCovariant(initializer_list<int> indices) override {
				int i = *(indices.begin()); // Get the first index
				int j = indices.begin()[1];
				int k = indices.begin()[2];

				// T_ijk = g_{il} T^l_jk	
				Expression result = 0;
				for (int l = 0; l < dim(); l++) {
					result += metric.co({i, l}) * mixed({l, j, k});
				}
				return result;
			}

			Expression computeContravariant(initializer_list<int> indices) override {
				int i = *(indices.begin()); // Get the first index
				int j = indices.begin()[1];
				int k = indices.begin()[2];

				// T^ij = g^{il} g^{jm} g^{kn} T_{lmn}	
				Expression result = 0;
				for (int l = 0; l < dim(); l++) {
					for (int m = 0; m < dim(); m++) {
						for (int n = 0; n < dim(); n++) {
							result += metric.contra({i, l}) * metric.contra({j, m}) * metric.contra({k, n}) * co({l, m, n});
						}
					}
				}
				return result;
			}

			Expression computeMixed(initializer_list<int> indices) override {
				int i = *(indices.begin()); // Get the first index
				int j = indices.begin()[1];
				int k = indices.begin()[2];

				// T^i_jk = g_{jl} g_{km} T^{ilm}	
				Expression result = 0;
				for (int l = 0; l < dim(); l++) {
					for (int m = 0; m < dim(); m++) {
						result += metric.co({j, l}) * metric.co({k, m}) * contra({i, l, m});
					}
				}
				return result;
			}

		public:

			Rank3Tensor(MetricTensor _metric): Tensor::Tensor(_metric, 3) {}

			// Expression co(int i, int j, int k) { return co({i, j, k}); }
			// Expression contra(int i, int j, int k) { return contra({i, j, k}); }
			// Expression mixed(int i, int j, int k) { return mixed({i, j, k}); }

			// int rank() const override { return 3; }

	};

	class Rank4Tensor: public Tensor {

		protected:

			Expression computeCovariant(initializer_list<int> indices) override {
				int i = *(indices.begin()); // Get the first index
				int j = indices.begin()[1];
				int k = indices.begin()[2];
				int l = indices.begin()[3];

				// T_ijkl = g_{im} T^m_{jkl}
				Expression result = 0;
				for (int m = 0; m < dim(); m++) {
					result += metric.co({i, m}) * mixed({m, j, k, l});
				}
				return result;
			}

			Expression computeContravariant(initializer_list<int> indices) override {
				int i = *(indices.begin()); // Get the first index
				int j = indices.begin()[1];
				int k = indices.begin()[2];
				int l = indices.begin()[3];

				// T^ijkl = g^{im} g^{jn} g^{ko} g^{lp} T_{mnop}	
				Expression result = 0;
				for (int m = 0; m < dim(); m++) {
					for (int n = 0; n < dim(); n++) {
						for (int o = 0; o < dim(); o++) {
							for (int p = 0; p < dim(); p++) {
								result += metric.contra({i, m}) * metric.contra({j, n}) * metric.contra({k, o}) * metric.contra({l, p}) * co({m, n, o, p});
							}
						}
					}
				}
				return result;
			}

			Expression computeMixed(initializer_list<int> indices) override {
				int i = *(indices.begin()); // Get the first index
				int j = indices.begin()[1];
				int k = indices.begin()[2];
				int l = indices.begin()[3];

				// T^i_jkl = g_{jm} g_{kn} g_{lo} T^{imno}	
				Expression result = 0;
				for (int m = 0; m < dim(); m++) {
					for (int n = 0; n < dim(); n++) {
						for (int o = 0; o < dim(); o++) {
							result += metric.co({j, m}) * metric.co({k, n}) * metric.co({l, o}) * contra({i, m, n, o});
						}
					}
				}
				return result;
			}

		public:

			Rank4Tensor(MetricTensor _metric): Tensor::Tensor(_metric, 4) {}

			// Expression co(int i, int j, int k, int l) { return co({i, j, k, l}); }
			// Expression contra(int i, int j, int k, int l) { return contra({i, j, k, l}); }
			// Expression mixed(int i, int j, int k, int l) { return mixed({i, j, k, l}); }

			// int rank() const override { return 4; }

	};

	using Vector = Rank1Tensor;

	class Manifold: public Dimensional {

		private:

			data::List<Tensor*> tensors;
			MetricTensor metric;

		public:

			Manifold() {}
			Manifold(MetricTensor _metric) {
				metric = _metric;
				dimension = metric.dim();
			}

	};

};