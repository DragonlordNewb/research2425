#include "headers/geometry.h"
#include "headers/einstein.h"

namespace library {

    template <typename T>
    class LibraryItem {

        protected:
        
            T item;
            string name; 

        public:

            LibraryItem(T item, string name): item(item), name(name) {}

            T get() { return item; }
            string getName() { return name; }

    };

    template <typename T>
    class LibrarySection {
        
    }

};