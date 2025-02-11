#include "headers/geometry.h"
#include "headers/einstein.h"

namespace library {

    template <typename T>
    class LibraryItem {

        protected:
        
            T item;
            string name; 
            data::Array<string> tags;

        public:

            LibraryItem(T item, string name, initializer_list<string> _tags): item(item), name(name), tags(_tags) {}

            T get() { return item; }
            string getName() { return name; }
            bool matches(string term) {
                if (name.contains(term)) { return true; }
                for (int i = 0; i < tags.getLength(); i++) {
                    if (tags.get(i).contains(term)) { return true; }
                }
                return false;
            }

    };

    template <typename T>
    class LibrarySection {
        
        protected:

            data::List<LibraryItem<T>> items;
            string name;

        public:

            LibrarySection(string name): name(name) {}

            string getName() { return name; }
            int getItemCount() { return items.getLength(); }
            void log(LibraryItem<T> item) { items.append(item); }

            data::List<LibraryItem<T>*> searchByTerm(string term) {
                // Return a list of pointers to the items that match
                data::List<LibraryItem<T>*> results;
                LibraryItem<T> item;
                for (int i = 0; i < getItemCount(); i++) {
                    item = items.get(i);
                    if (item.matches(term)) {
                        results.append(&item);
                    }
                }
                return results;
            }

            data::List<LibraryItem<T>*> searchByTerms(initializer_list<string> terms) {
                data::List<string> termslist(terms);
                data::List<LibraryItem<T>*> results;
                LibraryItem<T> item;
                string term;
                for (int i = 0; i < getItemCount(); i++) {
                    item = items.get(i);
                    for (int j = 0; j < terms.getLength(); terms++) {
                        term = termslist.get(j);
                        if (item.matches(term)) {
                            results.append(&item);
                            break;
                        }
                    }
                }
                return results;
            }

            data::List<T> getByTerm(string term) {
                // Return a list of pointers to the items that match
                data::List<T> results;
                LibraryItem<T> item;
                for (int i = 0; i < getItemCount(); i++) {
                    item = items.get(i);
                    if (item.matches(term)) {
                        results.append(item.get());
                    }
                }
                return results;
            }

            data::List<T> getByTerms(initializer_list<string> terms) {
                data::List<string> termslist(terms);
                data::List<T> results;
                LibraryItem<T> item;
                string term;
                for (int i = 0; i < getItemCount(); i++) {
                    item = items.get(i);
                    for (int j = 0; j < terms.getLength(); terms++) {
                        term = termslist.get(j);
                        if (item.matches(term)) {
                            results.append(item.get());
                            break;
                        }
                    }
                }
                return results;
            }

    }

};