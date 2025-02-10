#include <iostream>
#include <readline/readline.h>
#include <readline/history.h>
#include <string>
#include <vector>
#include <sstream>

#include "version.h"

using namespace std;

vector<std::string> tokenize(const std::string &input) {
    vector<std::string> tokens;
    istringstream stream(input);
    string token;

    while (stream >> token) {
        tokens.push_back(token);
    }

    return tokens;
}

// Function to process user commands
void processCommand(const std::vector<std::string>& tokens) {
    if (tokens.empty()) return;

    if (tokens[0] == "exit" or tokens[0] == "quit") exit(0);

    if (tokens[0] == "manifold") {
        if (tokens.size() < 3) {
            std::cout << "Usage: manifold <create|define|report> <args>\n";
            return;
        }

        std::string subcommand = tokens[1];

        if (subcommand == "create") {
            if (tokens.size() < 3) {
                std::cout << "Usage: manifold create <metric ID>\n";
                return;
            }
            std::string metricID = tokens[2];
            std::cout << "Creating manifold with metric ID: " << metricID << "\n";
            // Call function to create manifold
        }

        else if (subcommand == "define") {
            if (tokens.size() < 3) {
                std::cout << "Usage: manifold define <tensor name>\n";
                return;
            }
            std::string tensorName = tokens[2];
            std::cout << "Defining tensor on manifold: " << tensorName << "\n";
            // Call function to define tensor
        }

        else if (subcommand == "report") {
            if (tokens.size() < 3) {
                std::cout << "Usage: manifold report <tensor> [--options]\n";
                return;
            }
            
            std::string tensorName = tokens[2];
            bool co = false, contra = false, mixed = false, scalar = false;
            std::vector<int> indices;

            for (size_t i = 3; i < tokens.size(); ++i) {
                if (tokens[i] == "--co") co = true;
                else if (tokens[i] == "--contra") contra = true;
                else if (tokens[i] == "--mixed") mixed = true;
                else if (tokens[i] == "--scalar") scalar = true;
                else if ((tokens[i] == "--indices" or tokens[i] == "-i") && i + 1 < tokens.size()) {
                    // Collect indices
                    for (size_t j = i + 1; j < tokens.size(); ++j) {
                        try {
                            indices.push_back(std::stoi(tokens[j]));
                        } catch (...) {
                            break;
                        }
                    }
                    break; // Stop after parsing indices
                }
            }

            // Output results
            std::cout << "Reporting tensor: " << tensorName << "\n";
            if (co) std::cout << "   - Co-variant components\n";
            if (contra) std::cout << "   - Contravariant components\n";
            if (mixed) std::cout << "   - Mixed components\n";
            if (scalar) std::cout << "   - Scalar component\n";
            if (!indices.empty()) {
                std::cout << "   - Indices: ";
                for (int idx : indices) std::cout << idx << " ";
                std::cout << "\n";
            }

            // Call function to retrieve tensor data
        }
        else {
            std::cout << "Unknown manifold command: " << subcommand << "\n";
        }
    }
    else {
        std::cout << "Unknown command: " << tokens[0] << "\n";
    }
}

void startCLI() {
	cout << "\033[2J\033[1;1H";
    cout << "Spacetime Exploration Library - version " << VERSION_NUMBER << endl << "Enter any command to continue." << endl << endl;

    char* input;
    while (true) {
		cout << endl;
        input = readline("> ");
		cout << endl;
        if (!input) break; // Handle Ctrl+D

        std::string command(input);
        free(input);

        if (!command.empty()) {
            add_history(command.c_str());
            std::vector<std::string> tokens = tokenize(command);
            processCommand(tokens);
        }
    }
}

int main() {
    startCLI();
    return 0;
}