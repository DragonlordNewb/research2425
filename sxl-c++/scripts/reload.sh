echo "Attempting to compile sxl-c++/sxl.cpp ..."
if (g++ sxl-c++/sxl.cpp -o sxl/sxl -lginac -lcln -lreadline -w) then (echo "Successfully compiled with GiNaC and CLN linked.") else (echo "Failure to compile.") fi