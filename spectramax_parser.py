import pandas as pd
from csv_parser_meta import CsvParserInterface

class SpectraMaxParser(CsvParserInterface):
    
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

