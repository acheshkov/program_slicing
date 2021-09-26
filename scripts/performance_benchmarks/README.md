## Performance test for Block Slicing

### Usage

1. ```$ pip3 install ./program_slicing```
2. ```$ cd scripts/performance_benchmarks```
3. ```$ pip3 install -r requirements.txt```
4. ```$ cd block_slices```
5. Script parameters: 

`--dir` folder with java files

`-i` number of iterations to run all files, default is 1

Run ```$ python3 check_performance.py --dir dataset -i 2```
where dataset is teh folder with java files and number of iterations is 2.


You should have access to global network to use pip.
Python 3.8 with corresponding C compiler is required.
Run Python Console to check the version of C compiler.

___
#### Last reported result

PC info:

`RAM 64GiB` 

`CPU Intel(R) Xeon(R) Gold 6266C CPU @ 3.00GHz`:

The algorithm was run for 15 java files with 100 ncss. The procedure was run 10 time(s) for more accurate calculations.

Total time of running 15 java methods (script was executed 10 times) is 28.0 secs.

Average time for 1 method: 1.867 secs. 

Min time of 1 method: 0.000 secs, 

max time of 1 method: 12.000 secs, 

median: 0.000 secs, 

quantile 75%: 2.000 secs, 

quantile 95%: 12.000 secs