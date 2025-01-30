#include <iostream>
#include <readline/readline.h>
#include <readline/history.h>
#include <string>
#include <vector>
#include <sstream>

using namespace std;

// Function to process user commands
void processCommand(const std::string& command) {
    if (command == "exit") {
        cout << "\n";
        exit(0);
    } else if (command == "help") {
        cout << "Available commands: help, exit, geodesic, metric, ricci\n";

		// I dunno, placeholders
    } else if (command == "geodesic") {
        cout << "Computing geodesic...\n";
    } else if (command == "metric") {
        cout << "Evaluating metric tensor...\n";
    } else {
        cout << "Unknown command: " << command << "\n";
    }
}

// Main CLI loop
void startCLI() {
    cout << "Spacetime Exploration Library" << endl << "Type any command to continue" << endl << endl;

    char* input;
    while (true) {
        input = readline("> ");  // Display prompt and get user input

        if (!input) break; // Handle Ctrl+D (EOF)

        string command(input);
        free(input); // Readline allocates memory, free it after copying

        if (!command.empty()) {
            add_history(command.c_str()); // Add command to history
            processCommand(command);
        }
    }
}

int main() {
    startCLI();
    return 0;
}
