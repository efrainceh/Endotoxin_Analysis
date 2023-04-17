import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer

class DataProcess:
    
    # CONSTANTS VARIABLES
    NUMBER_OF_COL = 12
    NUMBER_OF_ROWS = 8
    COLUMN_NAMES = ["time", "temperature", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    TIME_INTERVAL = 30              # IN SECONDS

    # CREATED VARIABLES
    df = pd.DataFrame
    data_df = pd.DataFrame()
    time_col = ""

    def reset(self):

        self.df = pd.DataFrame()
        self.data_df = pd.DataFrame()
        self.time_col = ""

    def process(self, file_path):

        # READ DATA FROM FILE
        self.df = pd.read_csv(file_path, encoding="ISO-8859-1")

        # CLEAN THE DATA
        self._process_data()

        return self.time_col, self.data_df
    
    def _process_data(self):

        self._dropNonData()
        self._get_time_column()
        self._get_data()

    def _dropNonData(self):

        # SELECT COLUMNS WITH VALUES IN IT
        self.df = self.df.iloc[2:, :14]
        self.df.columns = self.COLUMN_NAMES
        
    def _get_time_column(self):

        # SELECTS TIME COLUMN, REMOVES NaN, RESETS INDEX AND THEN LOOKS FOR THE ~End STRING
        # THAT SIGNIFIES THE END OF TIME VALUES. BECAUSE THE TIMES ARE IN AN ODD FORMAT, IT
        # CALCULATES NEW TIMES BY JUST MULTIPLYING THE INDEX BY 30 sec
        time = self.df["time"] 
        time.dropna(inplace=True)
        time.reset_index(drop=True, inplace=True)
        endIx = time[time == "~End"].index[0]
        self.time_col = [t * self.TIME_INTERVAL for t in range(endIx)]

    def _get_data(self):
        
        # FOR CREATING NEW COLUMN NAMES
        letters = ["A", "B","C", "D", "E", "F", "G", "H"]       

        # FIRST DATA POINT IS AT INDEX 2
        offset = 2

        data = self.df[["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]] 

        for col in data.columns:
            
            # SELECT COLUMN
            data = self.df[col]

            # THERE ARE AS MANY DATA POINTS AS THERE ARE IN time_col. ONE TIME POINT DATA FOR A COLUMN
            # STARTS EVERY 9 ROWS (NUMBER OF ROWS IN WELL PLUS AN EMPTY SPACE)
            col_data = []
            for ix in range(len(self.time_col)):
                time_point_data = [data.loc[row + offset + ix * 9] for row in range(self.NUMBER_OF_ROWS)]
                col_data.append(time_point_data)

            # CREATE COLUMN NAMES
            col_names = [letter + col for letter in letters]

            # ADD DATA TO DATAFRAME
            col_df = pd.DataFrame(col_data, columns=col_names)
            self.data_df = pd.concat([self.data_df, col_df], axis=1)


class Analysis:

    # CONSTANT VARIABLES
    TIME_LIMIT = 0.2
    NUMBER_OF_COL = 12
    NUMBER_OF_ROWS = 8
    COLUMN_NAMES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    INDEX = ["A", "B", "C", "D", "E", "F", "G", "H"]

    # INPUTS 
    time_col = []
    data = []

    # READ FILE VARIABLES
    df = pd.DataFrame()

    #  ANALYSIS VARIABLES
    final_df = pd.DataFrame()
    standards = pd.DataFrame()
    model = ""

    def analyze(self, time_col, data, file_path):

        # ASSIGNMENT
        self.time_col = time_col
        self.data = data.astype(float)
        self.final_df["well"] = self.data.columns
        self._read_file(file_path)

        # ANALYSIS
        self._analyze()

        return self.final_df
    
    def reset(self):

        self.df = pd.DataFrame()
        self.final_df = pd.DataFrame()
        self.standards = pd.DataFrame()
        self.model = ""
    
    def save_plot(self, filepath):

        # CONVERT STANDARD VALUES TO ARRAY
        x = self.standards["time_log"].to_numpy().reshape(-1,1)
        y = self.standards["conc_log"].to_numpy()

        # CREATE VALUES TO PLOT A LINE
        x_line = np.linspace(x[0], x[-1], num=100)
        y_line = self.model.predict(x_line)

        plt.scatter(x, y, s=60, alpha=0.7, edgecolors="k")
        plt.plot(x_line, y_line, color="k")
        plt.xlabel("Log Time")
        plt.ylabel("Log concentration")
        plt.savefig(filepath)
        plt.clf()
        
    def _read_file(self, file_path):
        self.df = pd.read_csv(file_path, encoding="ISO-8859-1")
        self._extract_info("sample_name", [1,9], [1,14])
        self._extract_info("label", [25,33], [1,14])
        self._extract_info("concentration", [13,21], [1,14])
        self.final_df["concentration"] = self.final_df["concentration"].apply(pd.to_numeric)

    def _analyze(self):
        self._get_times_to_reach_limit()
        self._calculateLOG("time_log", "time")
        self._calculateLOG("conc_log", "concentration")
        self._linear_regression()
        self._calculate_samples()

    def _extract_info(self, col_name, rows, cols):

        # SELECT THE CELLS WITH THE SAMPLE INFORMATION
        info_df = self.df.iloc[rows[0]:rows[1], cols[0]:cols[1]]
        info_df.reset_index(drop=True, inplace=True)

        info = []
        # ADD THE VALUES OF EACH COLUMN TO A LIST
        for col in info_df.columns:
            col_as_list = info_df[col].values.tolist()
            info.extend(col_as_list)

        # ADD DATA TO DATAFRAME
        self.final_df[col_name] = info

    def _get_times_to_reach_limit(self):

        times = []
        for col in self.data.columns:

            # IF NO SAMPLE NAME GIVEN, THEN WELL IS ASSUMED EMPTY
            sample = self.final_df.loc[self.final_df["well"] == col, "sample_name"].item()
            if pd.isna(sample):
                time = "N/A"
            else:
                #  GET INDEX AT WHICH TIME IS ABOVE TIME_LIMIT
                time_ix = self._get_time_index(col)
                if time_ix == -1:             # TIME DID NOT GO ABOVE LIMIT
                    time = ">6000"
                else:                           # GET THE TIME
                    time = self.time_col[time_ix]

            times.append(time)

        # ADD TIMES TO DATAFRAME
        self.final_df["time"] = times

    def _get_time_index(self, column_name):
        
        # GET THE INDEX OF THE CELL AT WHICH TIME IS BIGGER THAN THE TIME_LIMIT.
        # IF INDECES IS EMPTY IT MEANS THE SAMPLE NEVER WENT ABOVE TIME_LIMIT, SO
        # THE RESULT WILL BE 0
        indeces = self.data[self.data[column_name] > self.TIME_LIMIT].index.tolist()
        if indeces:
            return indeces[0]
        else:
            return -1
        
    def _calculateLOG(self, new_column, col):

        # ONLY CALCULATE LOG FOR VALUES THAT ARE NUMBER, AND THEREFORE REPRESENT AN ACTUAL TIME OR CONCENTRATION
        self.final_df[new_column] = self.final_df.apply(lambda row: np.log10(row[col]) 
                                                        if self._valid_input(row[col]) else None, axis=1)
        
    def _valid_input(self, value):

        return (isinstance(value, int) or isinstance(value, float)) and value != 0
        
    def _linear_regression(self):

        # SELECT ROWS WHERE THE STANDARDS ARE LOCATED
        self.standards = self.final_df[self.final_df["sample_name"] == "Standard"]

        # CONVERT STANDARD VALUES TO ARRAY
        x = self.standards["time_log"].to_numpy().reshape(-1,1)
        y = self.standards["conc_log"].to_numpy()

        # GET LINEAR REGRESSION MODEL
        self.model = LinearRegression()
        self.model.fit(x, y)        

    def _calculate_samples(self):

        samples_x = self.final_df["time_log"].to_numpy().reshape(-1,1)

        # FILL MISSING VALUES (REPRESENTING EMPTY SAMPLE WELLS) WITH 5, WHICH CORRESPONDS
        # TO APPROXIMATELY 24 H MEASUREMENT 
        imputer = SimpleImputer(missing_values=np.nan, strategy="constant", fill_value=5)
        samples_x = imputer.fit_transform(samples_x)
        
        # PREDICT ENDOTOXIN CONCENTRATION IN SAMPLES AND STANDARDS
        samples_y = self.model.predict(samples_x)
        self.final_df["EU/ml"] = [10 ** samples_y[ix] if samples_x[ix] != 5 else None for ix in range(len(samples_y))]

        # CONVERTING VALUES TO EU/MG FOR PROTEIN SAMPLES
        self.final_df["EU/mg"] = self.final_df.apply(lambda row: row["EU/ml"] / row["concentration"]
                                                    if isinstance(row["label"], str) and row["label"].lower() == "protein" 
                                                    and row["concentration"] != 0
                                                    else None, axis=1)
    