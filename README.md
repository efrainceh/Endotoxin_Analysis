# ENDOTOXIN ANALYSIS TOOL

A ditty piece of code that does the analysis of Endotoxin Raw Data files from the Endotoxin (LAL) Test from Lonza Bioscience.

## Installation

The dist zip folder includes all the files required to run the app in Windows as an exe application. Alternatively, you can just run main.py using python. 
As it stands the app won't work on Macs because of an issue with the location of the logging files. 

## How to Use

### Input:

To app requires 2 files, selected using the GUI:

- **Raw Data File**: a csv file with the data from the plate reader. See test_files for the format.
- **Assay Info File**: a csv file with sample names, sample types (buffer, standard, protein), and sample concentrations (mg/ml). Location of samples, including the standards, is not important. The program will find the standards. See test_files for the format.

### Output:

The GUI prompts the user for a filename and location to save the results:

- **Results Table**: A CSV file with all the results. This will include sample name, sample type, EU/ml and EU/mg (only for protein samples). 

- **Standard Curve**: A JPG file with the standard curve. It will have the same name as the Results Table.

#### GUI:

![GUI](/images/gui.jpg)

### Warnings:

The app raises only two warnings:

- **File Missing**: User is missing an input file
- **Something Went Wrong**: This means something has gone wrong with the analysis, usually because the input files are incorrect or have the wrong format.

Both succesfull and failed runs are logged into the log files, located in the folder dist/logs.

#### File Missing:
![File missing](/images/file_missing.jpg)
#### Something went wrong:
![Something went wrong](/images/something_went_wrong.jpg)