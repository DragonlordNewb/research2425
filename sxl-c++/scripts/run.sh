clear
echo "Attempting to compile $1.cpp ..."
if (g++ $1.cpp -o $1 -lginac -lcln -w) then (echo "Successfully compiled with GiNaC and CLN linked, running ..."; ./$1) else (echo "Failure to compile.") fi