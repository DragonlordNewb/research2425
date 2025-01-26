class DatabaseID {

		private:

			int* token;
			int tlen;

		public:

			DatabaseID(int tlen=8): tlen(tlen) {
				srand(time(0));
				token = new int[tlen];
				for (int i = 0; i < tlen; i++) {
					token[i] = rand();
				}
			}

			int getTokenLength() const { return tlen; }
			bool match(int index, int value) { return (token[index] == value); }

			bool operator==(DatabaseID o) {
				if (o.getTokenLength() != getTokenLength()) {
					return false;
				}

				bool equal = true; 
				for (int i = 0; i < getTokenLength(); i++) {
					if (not o.match(i, token[i])) {
						equal = false;
					}
				}
				return equal;
			}

	};

	template <typename T>
	class DatabaseEntry {

		private:

			Array<std::string> fields;
			Array<T> values;
			Array<string> tags;
			int length;
			DatabaseID id;

		public:

			DatabaseEntry(Array<std::string> fields, Array<T> values, Array<string> tags, int dbidl=8): fields(fields), values(values), tags(tags) {
				length = fields.getLength();
				if (values.getLength() != length) {
					throw std::runtime_error("Bad database entry.");
				}
				id = DatabaseID(dbidl);
			}

			int getLength() const { return length; }
			int tagCount() const { return tags.getLength(); }

			bool hasField(std::string field) const {
				for (int i = 0; i < getLength(); i++) {
					if (fields.get(i) == field) { return true; }
				}
				return false;
			}

			bool hasTag(string tag) const {
				for (int i = 0; i < tags.getLength(); i++) {
					if (tags.get(i) == tag) {
						return true;
					}
				}
				return false;
			}

			int getIndex(std::string field) const {
				for (int i = 0; i < getLength(); i++) {
					if (fields.get(i) == field) {
						return i;
					}
				}
				return -1;
			}

			T get(std::string field) const {
				int index = getIndex(field);
				if (index == -1) {
					throw std::runtime_error("Invalid field.");
				}
				return values.get(index);
			}

			void set(std::string field, T value) {
				int index = getIndex(field);
				if (index == -1) {
					throw std::runtime_error("Invalid field.");
				}
				values.set(index, value);
			}

			bool isID(DatabaseID& x) { return id == x; }
			DatabaseID& getID() { return id; }
	
	};

	template <typename T>
	class Database {

		private:

			List<DatabaseEntry> entries;
			int dbidl;

			int index(DatabaseID id) {
				for (int i = 0; i < entries.getLength(); i++) {
					if (entries.get(i).getID() == id) {
						return i;
					}
				}
				return -1;
			}

		public:

			Database(int dbidl=8): dbidl(dbidl) {}

			void enter(Array<std::string> fields, Array<T> values) {
				entries.append(DatabaseEntry(fields, values, dbidl));
			}

			DatabaseEntry& get(DatabaseID id) {
				DatabaseEntry entry;
				for (int i = 0; i < entries.getLength(); i++) {
					entry = entries.get(i);
					if (entry.isID(id)) {
						return entry;
					}
				}
				throw runtime_error("Bad database ID.");
				return DatabaseEntry();
			}

			void modify(DatabaseID id, string field, T value) {
				get(id).set(field, value);
			}

			Array<DatabaseID> match(Array<string> fields, Array<T> values) {
				List<DatabaseID> matches;
				DatabaseEntry entry;
				bool matching = true;

				for (int i = 0; i < entries.getLength(); i++) {
					matching = true;
					entry = entries.get(i);

					for (int j = 0; j < fields.getLength(); j++) {
						if (entry.get(fields.get(i)) != values.get(i)) {
							matching = false;
							break;
						}
					}

					if (matching) {
						matches.append(entry.getID());
					}
				}

				return matches.asArray();
			}

			Array<DatabaseID> search(Array<string> tags) {
				List<DatabaseID> matches;
				DatabaseEntry entry;
				bool matching = true;

				for (int i = 0; i < entries.getLength(); i++) {
					entry = entries.get(i);
					for (int j = 0; j < tags.getLength(); j++) {
						if (entry.hasTag(tags.get(j))) {
							matches.append(entry.getID());
							break;
						}
					}
				}

				return matches.asArray();
			}

	};