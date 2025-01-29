clear
echo "    [SXL] Attempting to compile $1.cpp ..."
if (g++ $1.cpp -o $1 -lginac -lcln -w) then (echo "    [SXL] Successfully compiled with GiNaC and CLN linked, running ..."; ./$1; echo "    [SXL] Execution complete.") else (echo "    [SXL] Failure to compile.") fi