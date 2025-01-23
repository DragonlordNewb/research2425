#pragma once
#include <initializer_list>
#include <stdexcept>
#include <iostream>
#include <string>
#include <vector>
#include <sstream>

namespace data {

	template <typename T>
	class Array {

		protected:

			T* elements;
			size_t length;
			bool cleanedUp = false;

			void indexCheck(const int index) { 
				if (index < 0 || index >= length) { 
					std::stringstream ss;
					ss << "array access: index out of range: tried index " << index << " on array of length " << length;
					throw std::out_of_range(ss.str()); 
				}
			}

		public:

			explicit Array() {}
			explicit Array(int l): length(l), elements(new T[l]) {}
			explicit Array(std::initializer_list<T> initList): length(initList.size()), elements(new T[initList.size()]) {
				size_t index = 0; for (const T& value: initList) { elements[index++] = value; }
			}

			explicit Array(std::vector<T> v) {
				length = v.size();
				elements = new T[length];
				size_t index = 0; for (const T& value: v) { elements[index++] = value; }
			}

			T& get(const int index) { indexCheck(index); return elements[index]; } 
			void set(const int index, const T value) { indexCheck(index); elements[index] = value; }
			T& operator[](const int index) { indexCheck(index); return elements[index]; }
			size_t getLength() const noexcept { return length; }

			std::string repr() {
				std::stringstream ss;
				ss << "{";
				for (int i = 0; i < getLength(); i++) {
					ss << get(i);
					if (i != getLength() - 1) {
						ss << " ";
					}
				}
				ss << "}";
				return ss.str();
			}

			void copyTo(Array<T>& other) {
				for (int i = 0; i < getLength() and i < other.getLength(); i++) {
					other.set(i, get(i));
				}
			}

	};


	template <typename T>
	class RecursiveArray {

		private:

			int rank;
			int dimension;
			RecursiveArray<T>* subarrays;
			T* values;

		public:

			explicit RecursiveArray() {}
			explicit RecursiveArray(int _rank, int _dimension=4) {
				rank = _rank;
				dimension = _dimension;
				if (rank == 1) {
					values = new T[dimension];
				} else {
					subarrays = new RecursiveArray<T>[dimension];
					for (int i = 0; i < dimension; i++) {
						subarrays[i] = RecursiveArray(rank - 1, dimension);
					}
				}
			}

			T& get(std::initializer_list<int> indices) {
				if (rank == 1) {
					int index = *indices.begin();
					if (index < 0 or index >= dimension) { 
						throw std::runtime_error("(SXL error code 1) Extradimensional index."); 
					}
				}

				RecursiveArray<T>* ptr = nullptr;
				for (const auto& index: indices) {
					// Check for bad indices
					if (index < 0 or index >= dimension) { 
						throw std::runtime_error("(SXL error code 1) Extradimensional index."); 
					}

					// Get into the first subarray, if necessary
					if (ptr == nullptr) {
						ptr = &(subarrays[index]);
						continue;
					}

					// If we're at the bottom, return the value
					if (ptr->rank == 1) {
						return ptr->values[index];
					}

					// Go another layer down
					ptr = &(ptr->subarrays[index]);
				}

				// If we get here, there weren't enough
				// indices supplies to get to rank 1 so
				// throw an error
				throw std::runtime_error("(SXL error code 2) Insufficient indices passed.");
			}

	};

	template <typename T>
	T sub(T& arr, int start, int stop) noexcept {
		int l = stop - start;
		if (l < 0) { return sub<T>(arr, stop, start); }
		if (l == 0) { return T(0); }
		if (l == 1) { return T({arr[start]}); }
		else {
			T r(l);
			for (int i = start; i < stop; i++) {
				r[i - start] = arr[i];
			}
			return r;
		}
	}

	data::Array<double> vtoa(std::vector<double> v) {
		data::Array<double> r(v.size());
		for (int i = 0; i < v.size(); i++) { r[i] = v[i]; }
		return r;
	}

	std::vector<double> atov(data::Array<double> a) {
		std::vector<double> r(a.getLength());
		for (int i = 0; i < a.getLength(); i++) { r[i] = a[i]; }
		return r;
	}

	template <typename T>
	class Matrix {
	
		protected:

			T* elements;
			size_t rows;
			size_t cols;
			bool cleanedUp = false;

		public:

			Matrix() {}

			Matrix(int rows, int cols): rows(rows), cols(cols) {
				elements = new T[rows * cols];
				size_t index = 0;
			}

			Matrix(std::initializer_list<std::initializer_list<T>> initList) {
				rows = initList.size();
				cols = initList.begin()->size();
				elements = new T[rows * cols];
				size_t index = 0;
				for (auto& row : initList) {
					if (row.size() != cols) {
						throw std::invalid_argument("matrix initialization: all rows must have the same number of columns");
					}
					for (const T& value : row) {
						elements[index++] = value;
					}
				}
			}

			T& get(size_t row, size_t col) {
				if (row >= rows) throw std::out_of_range("matrix access: row out of range");
				if (col >= cols) throw std::out_of_range("matrix access: column out of range");
				return elements[row * cols + col];
			}
			void set(size_t row, size_t col, T value) { elements[row * cols + col] = value; }
			size_t getRows() { return rows; }
			size_t getCols() { return cols; }

			void copyTo(Matrix<T>& other) {
				for (int i = 0; i < getRows() and i < other.getRows(); i++) {
					for (int j = 0; j < getCols() and j < other.getCols(); j++) {
						other.set(i, j, get(i, j));
					}
				}
			}

	};

	template <typename T>
	class ListElement {

		protected:

			T value;
			ListElement<T>* next;

			bool locked;

		public:

			explicit ListElement(T value): value(value), next(nullptr), locked(false) {}

			void reveal() { locked = false; }
			void hide() { locked = true; }

			T& getValue() { return value; }
			void setValue(T value_) { value = value_; }

			ListElement<T>* getNext() { return next; }
			void setNext(ListElement<T>* next_) { next = next_; }

	};

	template <typename T>
	class List {

		protected:

			ListElement<T>* head;

			bool locked;
			bool cleanedUp = false;
			int length = 0;

		public:

			// Constructors and destructors

			explicit List(): head(nullptr), locked(false) {}

			List(std::initializer_list<T> initList) {
				head = nullptr;
				locked = false;
				int i = 0;
				for (const auto& val : initList) {
					append(val);
				}
			}

			~List() {
				if (not cleanedUp) { cleanup(); }
			}

			void cleanup() {
				if (not cleanedUp) {
					ListElement<T>* current = head;
					ListElement<T>* nextNode;

					while (current != nullptr) {
						nextNode = current->getNext();
						delete current;
						current = nextNode;
					}
					cleanedUp = true;
				}
			}

			// Writing

			void prepend(T value) {
				ListElement<T>* newSLLE = new ListElement<T>(value);

				if (head != nullptr) { newSLLE->setNext(head); }

				head = newSLLE;

				length++;
			}

			void insert(T value, int index) {
				ListElement<T>* newSLLE = new ListElement<T>(value);

				if (index == 0) {
					prepend(value);
					return;
				}

				ListElement<T>* current = head;
				for (int i = 0; i < index - 1 && current != nullptr; i++) { current = current->getNext(); }

				if (current == nullptr) {
					append(value);
					return;
				}

				newSLLE->setNext(current->getNext());
				current->setNext(newSLLE);

				length++;
			}

			void append(T value) {
				ListElement<T>* newSLLE = new ListElement<T>(value);

				if (head == nullptr) {
					head = newSLLE;
				} else {
					ListElement<T>* current = head;
					while (current->getNext() != nullptr) {
						current = current->getNext();
					}

					current->setNext(newSLLE);
				}

				length++;
			}

			void remove(int index) {
				if (head == nullptr) { return; }

				if (index == 0) {
					head = head->getNext();
					return;
				}

				ListElement<T>* current = head;
				for (int i = 0; i < index - 1 && current != nullptr; i++) { current = current->getNext(); }

				if (current == nullptr || current->getNext() == nullptr) { return; }

				ListElement<T>* temp = current->getNext();
				current->setNext(temp->getNext());
				delete temp;

				length--;
			}

			void set(int index, T value) {
				ListElement<T>* current = head;
				for (int i = 0; i < index && current != nullptr; i++) { current = current->getNext(); }

				if (current == nullptr) {
					return T();
				}

				current->setValue(value);
			}

			// Reading

			T& get(int index) {
				ListElement<T>* current = head;
				for (int i = 0; i < index && current != nullptr; i++) { current = current->getNext(); }

				if (current == nullptr) {
					throw std::runtime_error("invalid pointer in list (possible out-of-range error)");
				}

				return current->getValue();
			}

			int getLength() const {
				return length;
			}

			bool contains(T value) const {
				ListElement<T>* current = head;
				for (int i = 0; current != nullptr; i++) { 
					if (current->getValue() == value) { return true; } 
					current = current->getNext(); 
				}
				return false;
			}

			int find(T value, int skip=0) const {
				ListElement<T>* current = head;
				int i;
				for (int j = skip; j >= 0; j--) {
					for (i = 0; i < getLength() && current != nullptr && current->getValue() != value; i++) { current = current->getNext(); }
				}
				if (current == nullptr) {
					return -1; // not found but not fatal
				}
				return i; 
			}

			List<int> match(T value) const {
				List<int> results;

				ListElement<T>* current = head;
				for (int i = 0; i < getLength() && current != nullptr; i++) { 
					if (current->getValue() == value) { results.append(i); }
					current = current->getNext(); 
				}

				return results;
			}

			std::string repr() {
				std::stringstream ss;
				ss << (std::string)("[");
				int len = getLength();
				for (int i = 0; i < len; i++) {
					ss << get(i);
					if (i != len - 1) {
						ss << (std::string)(", ");
					}
				}
				ss << (std::string)("]");
				return ss.str();
			}

			Array<T> asArray() {
				Array<T> a(getLength());
				for (int i = 0; i < getLength(); i++) {
					a.set(i, get(i));
				}
				return a;
			}

			List<T> asList(Array<T> arr) {
				List<T> result;
				for (int i = 0; i < arr.getLength(); i++) {
					result.append(arr.get(i));
				}
				return result;
			}

	};

};