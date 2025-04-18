#pragma once
#include "dependencies.h"

namespace geometry {

	string NO_NAME = "__NO_NAME__"; // to make sure nobody accidentally uses it

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
			data::Array<Symbol> velocities;

		public:

			CoordinateSystem() {}
			CoordinateSystem(initializer_list<std::string> labels) {
				data::Array<std::string> arr(labels);
				dimension = arr.getLength();
				coordinates = data::Array<Symbol>(dimension);
				velocities = data::Array<Symbol>(dimension);
				for (int i = 0; i < dim(); i++) {
					coordinates[i] = Symbol(arr.get(i));
					velocities[i] = Symbol("v^" + arr.get(i));
				}
			}

			Symbol& x(int index) { return coordinates.get(index); }
			Symbol& v(int index) { return velocities.get(index); }
			Expression ddx(Expression e, int index) { return e.diff(x(index)); }

	};

	class MetricTensor: public Dimensional {

		protected:

			data::RecursiveArray<Expression> covariantTensor;
			Matrix covariant;
			data::RecursiveArray<Expression> contravariantTensor;
			Matrix contravariant;
			Expression determinant;

		public:

			CoordinateSystem coordinates;

			MetricTensor() {}
			MetricTensor(initializer_list<initializer_list<Expression>> values, CoordinateSystem _coordinates) {
				dimension = _coordinates.dim();
				covariant = Matrix(values);
				contravariant = covariant.inverse();
				coordinates = _coordinates;
				if (dim() != coordinates.dim()) {
					throw std::runtime_error("(SXL error code 3) Metric and coordinate system have incompatible dimensions.");
				}
				covariantTensor = data::RecursiveArray<Expression>(2, dim());
				contravariantTensor = data::RecursiveArray<Expression>(2, dim());
				determinant = covariant.determinant();

				for (int i = 0; i < dimension; i++) {
					for (int j = 0; j < dimension; j++) {
						covariantTensor.get({i, j}) = covariant(i, j);
						contravariantTensor.get({i, j}) = contravariant(i, j);
					}
				}
			}

			Expression co(vector<int> indices) { return covariantTensor.get(indices); }
			Expression contra(vector<int> indices) { return contravariantTensor.get(indices); }
			Expression det() { return determinant; }

	};

	class Manifold;

	class Tensor: public Dimensional {

		protected:

			data::RecursiveArray<Expression> covariantTensor;
			data::RecursiveArray<bool> covariantTensorComputed;
			data::RecursiveArray<Expression> contravariantTensor;
			data::RecursiveArray<bool> contravariantTensorComputed;
			data::RecursiveArray<Expression> mixedTensor;
			data::RecursiveArray<bool> mixedTensorComputed;

			MetricTensor metric;
			CoordinateSystem coordinates;
			int _rank;

		public:

			Tensor(MetricTensor _metric, int __rank) {
				if (__rank <= 0) {
					throw std::runtime_error("(SXL error code 5) Invalid tensor rank.");
				}
				_rank = __rank;
				metric = _metric;
				coordinates = metric.coordinates;
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

			Expression co(vector<int> indices) {
				if (not covariantTensorComputed.get(indices)) {
					covariantTensor.set(indices, computeCovariant(indices).normal());
					covariantTensorComputed.set(indices, true);
				}
				return covariantTensor.get(indices); 
			}

			Expression contra(vector<int> indices) { 
				if (not contravariantTensorComputed.get(indices)) {
					contravariantTensor.set(indices, computeContravariant(indices).normal());
					contravariantTensorComputed.set(indices, true);
				}
				return contravariantTensor.get(indices); 
			}

			Expression mixed(vector<int> indices) {
				if (not mixedTensorComputed.get(indices)) {
					mixedTensor.set(indices, computeMixed(indices).normal());
					mixedTensorComputed.set(indices, true);
				}
				return mixedTensor.get(indices); 
			}

			virtual Expression computeCovariant(vector<int> indices) { return 0; }
			virtual Expression computeContravariant(vector<int> indices) { return 0; }
			virtual Expression computeMixed(vector<int> indices) { return 0; }

			void set_co(vector<int> indices, Expression value) { covariantTensor.set(indices, value); covariantTensorComputed.set(indices, true); }
			void set_contra(vector<int> indices, Expression value) { contravariantTensor.set(indices, value); contravariantTensorComputed.set(indices, true); }
			void set_mixed(vector<int> indices, Expression value) { mixedTensor.set(indices, value); mixedTensorComputed.set(indices, true); }

			bool isBlank() {
				return covariantTensorComputed.isAll(false) and contravariantTensorComputed.isAll(false) and mixedTensorComputed.isAll(false);
			}

			bool isUnderdetermined() {
				return covariantTensorComputed.isNotAll(true) or contravariantTensorComputed.isNotAll(true) or mixedTensorComputed.isNotAll(true);
			}

			bool isDetermined() { return not isUnderdetermined(); }

			virtual void calculate(Manifold* mf) { throw runtime_error("No calculation method provided."); }
			virtual string name() { return NO_NAME; }

			virtual Expression scalar() = 0;

	};

	class Rank1Tensor: public Tensor {

		// The rank-1 tensor (technically a vector) doesn't really care for the 
		// "mixed" array, so it just uses the contravariant and covariant, and
		// the .mixed method just returns the contravariant.

		protected:

			Expression computeCovariant(vector<int> indices) override {
				int i = *(indices.begin()); // Get the first index

				// v_i = g_{ij} v^j	
				Expression result = 0;
				for (int j = 0; j < dim(); j++) {
					result += metric.co({i, j}) * contra({j});
				}
				return result;
			}

			Expression computeContravariant(vector<int> indices) override {
				int i = *(indices.begin());

				// v^i = g^{ij} v_j
				Expression result = 0;
				for (int j = 0; j < dim(); j++) {
					result += metric.contra({i, j}) * co({j});
				}
				return result;
			}

			Expression computeMixed(vector<int> indices) override {
				return contra(indices);
			}

		public:

			Rank1Tensor(MetricTensor _metric): Tensor::Tensor(_metric, 1) {}
			Rank1Tensor(MetricTensor _metric, int x): Tensor::Tensor(_metric, 1) {
				for (int i = 0; i < dim(); i++) {
					set_co({i}, x);
					set_contra({i}, x);
					set_mixed({i}, x);
				}
			}

			// Expression co(int i) { return co({i}); }
			// Expression contra(int i) { return contra({i}); }
			// Expression mixed(int i) { return mixed({i}); }

			// int rank() const override { return 1; }

			Expression scalar() override { throw runtime_error("Can't find the scalar of a rank-1 tensor."); }

			Rank1Tensor operator+(Rank1Tensor other) {
				Rank1Tensor result(metric);
				for (int i = 0; i < dim(); i++) {
					result.set_co({i}, co({i}) + other.co({i}));
					result.set_contra({i}, contra({i}) + other.contra({i}));
				}
				return result;
			}

			Rank1Tensor operator-(Rank1Tensor other) {
				Rank1Tensor result(metric);
				for (int i = 0; i < dim(); i++) {
					result.set_co({i}, co({i}) - other.co({i}));
					result.set_contra({i}, contra({i}) - other.contra({i}));
				}
				return result;
			}

			Rank1Tensor operator*(Expression s) {
				Rank1Tensor result(metric);
				for (int i = 0; i < dim(); i++) {
					result.set_co({i}, co({i}) * s);
					result.set_contra({i}, contra({i}) * s);
				}
				return result;
			}

			Rank1Tensor operator/(Expression s) {
				Rank1Tensor result(metric);
				for (int i = 0; i < dim(); i++) {
					result.set_co({i}, co({i}) / s);
					result.set_contra({i}, contra({i}) / s);
				}
				return result;
			}

			Expression computeCoordinateGamma() {
				// Compute the Lorentz factor, assuming the spatial components here are 
				// a 3-velocity. Assumes an (n-1)+1-dimensional spacetime.

				Expression s = 0;
				for (int i = 0; i < dim(); i++) {
					for (int j = 0; j < dim(); j++) {
						if (i == 0 and j == 0) {
							s = s + 1;
						} else if (i == 0) {
							s = s + metric.co({0, j}) * contra({j});
						} else if (j == 0) {
							s = s + metric.co({i, 0}) * contra({i});
						} else {
							s = s + metric.co({i, j}) * contra({i}) * contra({j});
						}
					}
				}
				return (Symbol("c") / GiNaC::sqrt(s)).normal(); 
			}

			// Expression coordinateToProper() {
			// 	for 
			// }

	};

	class Rank2Tensor: public Tensor {

		protected:

			Expression computeCovariant(vector<int> indices) override {
				int i = *(indices.begin()); // Get the first index
				int j = indices.begin()[1];

				// T_ij = g_{ik} T^k_j	
				Expression result = 0;
				for (int k = 0; k < dim(); k++) {
					result += metric.co({i, k}) * mixed({k, j});
				}
				return result;
			}

			Expression computeContravariant(vector<int> indices) override {
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

			Expression computeMixed(vector<int> indices) override {
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

			Expression scalar() override {
				Expression val = 0; 
				for (int i = 0; i < dim(); i++) {
					for (int j = 0; j < dim(); j++) {
						val += metric.contra({i, j}) * co({i, j});
					}
				}
				return val;
			}

			Expression contract(Rank1Tensor other) {
				Expression val = 0;
				for (int i = 0; i < dim(); i++) {
					for (int j = 0; j < dim(); j++) {
						val += co({i, j}) * other.contra({i}) * other.contra({j});
					}
				}
				return val;
			}

	};

	class Rank3Tensor: public Tensor {

		protected:

			Expression computeCovariant(vector<int> indices) override {
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

			Expression computeContravariant(vector<int> indices) override {
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

			// Expression computeMixed(initializer_list<int> indices) override {
			// 	int i = *(indices.begin()); // Get the first index
			// 	int j = indices.begin()[1];
			// 	int k = indices.begin()[2];

			// 	// T^i_jk = g_{jl} g_{km} T^{ilm}	
			// 	Expression result = 0;
			// 	for (int l = 0; l < dim(); l++) {
			// 		for (int m = 0; m < dim(); m++) {
			// 			result += metric.co({j, l}) * metric.co({k, m}) * contra({i, l, m});
			// 		}
			// 	}
			// 	return result;
			// }

			Expression computeMixed(vector<int> indices) override {
				int i = *(indices.begin()); // Get the first index
				int j = indices.begin()[1];
				int k = indices.begin()[2];

				// T^i_jk = g^{il} T_{ljk}
				Expression result = 0;
				for (int l = 0; l < dim(); l++) {
					result += metric.contra({i, l}) * co({l, j, k});
				}
				return result;
			}

		public:

			Rank3Tensor(MetricTensor _metric): Tensor::Tensor(_metric, 3) {}

			// Expression co(int i, int j, int k) { return co({i, j, k}); }
			// Expression contra(int i, int j, int k) { return contra({i, j, k}); }
			// Expression mixed(int i, int j, int k) { return mixed({i, j, k}); }

			// int rank() const override { return 3; }

			Expression scalar() override { throw runtime_error("Can't find the scalar of a rank-3 tensor."); }

			Rank1Tensor contractWith_23(Rank1Tensor other) {
				Rank1Tensor result(metric);
				Expression val;
				for (int x = 0; x < dim(); x++) {
					val = 0;
					for (int i = 0; i < dim(); i++) {
						for (int j = 0; j < dim(); j++) {
							val += mixed({x, i, j}) * other.contra({i}) * other.contra({j});
						}
					}
					result.set_contra({x}, val);
				}
				return result;
			}

	};

	class Rank4Tensor: public Tensor {

		protected:

			Expression computeCovariant(vector<int> indices) override {
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

			Expression computeContravariant(vector<int> indices) override {
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

			Expression computeMixed(vector<int> indices) override {
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

			Expression scalar() override {
				Expression val = 0;
				for (int i = 0; i < dim(); i++) {
					for (int j = 0; j < dim(); j++) {
						for (int k = 0; k < dim(); k++) {
							for (int l = 0; l < dim(); l++) {
								val += co({i, j, k, l}) * contra({i, j, k, l});
							}
						}
					}
				}
				return val;
			}

	};

	// === GEODESICS === //

	using Vector = Rank1Tensor;

	// === MANIFOLDS AND DEFINITIONS === //

	class Manifold: public Dimensional {

		private:

			data::List<Tensor*> tensors;

		public:

			MetricTensor metric;

			Manifold() {}
			Manifold(MetricTensor _metric) {
				metric = _metric;
				dimension = metric.dim();
			}

			~Manifold() {
				for (int i = 0; i < getTensorCount(); i++) {
					delete tensors.get(i); // free all pointers
				}
			}

			int getTensorCount() {
				return tensors.getLength();
			}

			Tensor* get(string name) {
				for (int i = 0; i < getTensorCount(); i++) {
					if (tensors.get(i)->name() == name) {
						return tensors.get(i);
					}
				}
				return nullptr;
			}

			Tensor* operator()(string name) {
				return get(name);
			}

			int define(Tensor* t) {
				if (get(t->name()) != nullptr) {
					// Already defined
					return 1;
				}
				t->calculate(this);
				tensors.append(t);
				return 0;
			}

			template <typename T>
			int define() {
				return define(new T(metric));
			}

			Expression co(string name, vector<int> indices) { return get(name)->co(indices); }
			Expression contra(string name, vector<int> indices) { return get(name)->contra(indices); }
			Expression mixed(string name, vector<int> indices) { return get(name)->mixed(indices); }
			Expression scalar(string name) { return get(name)->scalar(); }

	};

	// like, for example, contracting with another tensor

	class TensorOperator {

		public:

			virtual int arity() = 0;

	};

	template <typename InputT, typename OutputT>
	class UnaryTensorOperator: public TensorOperator {

		public:

			int arity() override { return 1; }

			virtual OutputT calculate(InputT input) = 0;
			OutputT operator()(InputT input) { return calculate(input); }

	};

	template <typename InputT1, typename InputT2, typename OutputT>
	class BinaryTensorOperator: public TensorOperator {

		public:

			int arity() override { return 1; }

			virtual OutputT calculate(InputT1 input1, InputT2 input2) = 0;
			OutputT operator()(InputT1 input1, InputT2 input2) = 0;

	};

};

string CCS = "connection coefficients";
string TORSION = "torsion";
string RIEMANN = "riemann";
string RICCI = "ricci";

namespace tensors {

	class ConnectionCoefficients: public geometry::Rank3Tensor {

		// Already included: metric

		public:

			ConnectionCoefficients(geometry::MetricTensor m): geometry::Rank3Tensor(m) {}

			void calculate(geometry::Manifold* mf) override {
				// Manifold is not necessary since this
				// is a metric-only computation

				Expression firstKind;
				for (int i = 0; i < dim(); i++) {
					for (int j = 0; j < dim(); j++) {
						for (int k = 0; k < dim(); k++) {
							Expression e1, e2, e3, m1, m2, m3;
							m1 = metric.co({i, j});
							m2 = metric.co({i, k});
							m3 = metric.co({j, k});
							e1 = coordinates.ddx(m1, k);
							e2 = coordinates.ddx(m2, j);
							e3 = coordinates.ddx(m3, i);
							// cout << "m" << i << j << " [ " << m1 << " ]" << " dd" << coordinates.x(k) << " = " << e1 << endl;;
							firstKind = (e1 + e2 - e3) / 2;
							set_co({i, j, k}, firstKind.normal());
						}
					}
				}

				Expression secondKind = 0;
				for (int i = 0; i < dim(); i++) {
					for (int j = 0; j < dim(); j++) {
						for (int k = 0; k < dim(); k++) {
							secondKind = 0;
							for (int l = 0; l < dim(); l++) {
								secondKind = secondKind + (metric.contra({i, l}) * co({l, j, k}));
							}
							set_contra({i, j, k}, secondKind.normal());
						}
					}
				}
			}

			string name() override { return CCS; }

	};

	class TorsionTensor: public geometry::Rank3Tensor {

		// Already included: metric

		public:

			TorsionTensor(geometry::MetricTensor m): geometry::Rank3Tensor(m) {}

			void calculate(geometry::Manifold* mf) override {
				// Manifold is not necessary since this
				// is a metric-only computation

				Expression val;
				for (int i = 0; i < dim(); i++) {
					for (int j = 0; j < dim(); j++) {
						for (int k = 0; k < dim(); k++) {
							val = mf->mixed(CCS, {i, j, k}) - mf->mixed(CCS, {i, k, j});
							set_mixed({i, j, k}, val.normal());
						}
					}
				}
			}

			string name() override { return TORSION; }

	};

	class RiemannTensor: public geometry::Rank4Tensor {

		public:

			RiemannTensor(geometry::MetricTensor m): geometry::Rank4Tensor(m) {}

			void calculate(geometry::Manifold* mf) override {
				// Manifold is not necessary since this
				// is a metric-only computation

				Expression a, b, e1, e2, e3, e4, e5, e6;

				for (int i = 0; i < dim(); i++) {
					for (int j = 0; j < dim(); j++) {
						for (int k = 0; k < dim(); k++) {
							for (int l = 0; l < dim(); l++) {
								// Compute partial derivatives of Christoffel symbols
								e1 = coordinates.ddx(mf->mixed(CCS, {i, l, j}), k);  // ∂_k Γ^i_jl
								e2 = coordinates.ddx(mf->mixed(CCS, {i, k, j}), l);  // ∂_l Γ^i_jk
								
								a = e1 - e2;

								b = 0;
								for (int m = 0; m < dim(); m++) {
									e3 = mf->mixed(CCS, {i, k, m});  // Γ^i_km
									e4 = mf->mixed(CCS, {m, l, j});  // Γ^m_jl
									e5 = mf->mixed(CCS, {i, l, m});  // Γ^i_lm
									e6 = mf->mixed(CCS, {m, k, j});  // Γ^m_jk

									b = b + (e3 * e4) - (e5 * e6);
								}

								// Store the computed Riemann tensor component
								set_mixed({i, j, k, l}, (a + b).normal());
							}
						}
					}
				}
			}

			string name() override { return RIEMANN; }

	};

	class RicciTensor: public geometry::Rank2Tensor {

		public:

			RicciTensor(geometry::MetricTensor m): geometry::Rank2Tensor(m) {}

			void calculate(geometry::Manifold* mf) override {
				// Manifold is not necessary since this
				// is a metric-only computation

				Expression val;
				for (int i = 0; i < dim(); i++) {
					for (int j = 0; j < dim(); j++) {
						val = 0;
						for (int k = 0; k < dim(); k++) {
							val = val + mf->mixed(RIEMANN, {k, i, k, j});
						}
						set_co({i, j}, val.normal());
					}
				}
			}

			string name() override { return RICCI; }

	};

};

namespace operators {

};