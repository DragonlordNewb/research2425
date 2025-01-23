if (g++ $1.cpp -o $1 -lginac -lcln);
then (echo Success);
else (echo Failure);
fi