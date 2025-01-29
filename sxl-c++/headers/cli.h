#include <iostream>
#include <string>
#include <vector>

using namespace std;

class SXL {

    public:

        vector<string> split(string& s, const string& delimiter) {
            vector<string> tokens;
            size_t pos = 0;
            string token;
            while ((pos = s.find(delimiter)) != string::npos) {
                token = s.substr(0, pos);
                tokens.push_back(token);
                s.erase(0, pos + delimiter.length());
            }
            tokens.push_back(s);

            return tokens;
        }

        vector<string> readCommand() {
                cout << " > ";
                string cmd;
                cout.flush();
                cin >> cmd;
                cout.flush();
                cout << endl;
                return split(cmd, " ");
        }

        void parseCommand(vector<string> cmds) {
            for (int i = 0; i < cmds.size(); i++) {
                cout << cmds[i] << endl;
            }
        }

        void operator<<(string command) {
            parseCommand(command);
        }

};