# Sample Ingest Function

For Lambda functions, use `main.py` to write your source code. Any dependencies can be listed in `requirements.txt`. If the function requires dependencies outside of what can be installed with pip, such as GDAL, they should be specified in the functions `README.md`.

A typical function directory would look like the following:

```
functions
  +-my_function
    +- main.py
    +- requirements.txt
    +- README.md
```
