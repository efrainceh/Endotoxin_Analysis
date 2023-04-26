import pandas as pd
import numpy as np
from csv_parser_meta import CsvParserInterface

class ClarioStarParser(CsvParserInterface):
    
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
        self.df = self.df.iloc[7:, :]
        self.df.reset_index(drop=True, inplace=True)

        # TRANSPOSE AND THEN AGAIN SELECT COLUMNS WITH VALUES IN IT
        df_t = self.df.transpose()
        self.df = df_t
        self.df = self.df.iloc[:, 2:]
        self.df.reset_index(drop=True, inplace=True)

        # GET COLUMN NAMES FROM CURRENT SAMPLES. DROP THE REST OF THE NON-INFO
        column_names = self.df.iloc[0].to_list()
        column_names[0] = "time"
        self.df.columns = column_names
        self.df = self.df.iloc[2:, :]
        self.df.reset_index(drop=True, inplace=True)
        
    def _get_time_column(self):

        # SELECTS TIME COLUMN AND THEN CALCULATES NEW TIMES BY JUST MULTIPLYING THE INDEX BY 30 sec
        time = self.df["time"] 
        self.time_col = [t * self.TIME_INTERVAL for t in range(time.size)]

    def _get_data(self):
        
        # CREATING NEW COLUMN NAMES
        letters = ["A", "B","C", "D", "E", "F", "G", "H"]
        numbers = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
        col_names = []

        for number in numbers:
            col_names.extend([letter + number for letter in letters])

        # ADD EACH COLUMN TO DATA DATAFRAME, IF COLUMN DOESN'T EXIST THEN FILL WITH NaN
        for col in col_names:
            
            if col in self.df.columns.to_list():

                # SELECT COLUMN
                col_data = self.df[col].to_list()
            
            else:
                # CREATE COLUMN OF NaN 
                col_data = [np.nan for t in range(len(self.time_col))]

            # ADD DATA TO DATAFRAME
            col_df = pd.DataFrame(col_data, columns=[col])
            self.data_df = pd.concat([self.data_df, col_df], axis=1)

        print(self.data_df.head(10))


p = "./test_files/20230424_EndotoxinRaw.csv"

dp = ClarioStarParser()
dp.process(p)