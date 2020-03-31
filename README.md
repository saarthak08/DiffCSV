# DiffCSV
    A python project (flask based web app and command-line script) which takes two 'csv' files as input & produce the difference between them in an output 'csv' file.   
   

## Procedure (For Flask web app):
   - Install Flask (run `pip3 install Flask` in the terminal)
   - Run `flask run`.
   - The files after calculation are stored in the `files` folder in the project directory.
   - `result.csv` can also be downloaded.
   
## Procedure (For command-line script):
   - Switch to `cli` branch and clone the repository.
   - Create a `files` folder in the project directory.
   - Inside `files` folder, create an `Inputs` folder.
   - Place your two input files in files/Inputs/ folder with first file name as input(1).csv and second file name as input(2).csv
   - Run `python cl_script.py`.
   - The output file will be stored at `files/Output` folder in the project directory.
   
## NOTE
   - Differences are calculated by keeping the first column (index = 0) of each of the two input files as primary key. i.e. The value in the first column (index = 0) of the first input file is matched with the values of the first column (index = 0) of the second file and then, the differences between them is calculated.
   - Primary key can be changed by changing primary key index in `config.py` file. Default value is set to 0.