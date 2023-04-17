import os
import tkinter as tk
from tkinter import *
from tkinter import filedialog


import sys

from analysis import *
from log import Logger

class GUI(tk.Tk):

    # CONSTANTS
    SCREEN_HEIGHT = 150
    SCREEN_WIDHT = 600
    NUMBER_OF_ROWS = 3
    NUMBER_OF_COLS = 3
    PLACE_HOLDER_STRING = " " * 50
    WARNING_MESSAGES = ["At least one file is missing", "Something went wrong, check your input files"]

    # INSTANCES OF CLASSES TO PROCESS AND ANALYZE THE DATA, AND LOG ERRORS 
    dp = DataProcess()
    al = Analysis()
    logger = Logger()

    # FILE PATHS PROVIDED BY THE USER
    raw_data_filepath = ""
    assay_info_filepath = ""

    # MAP TO KEEP TRACK OF THE LABELS IN THE WINDOW
    labels = {}

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        self._loadGUI()

    def _loadGUI(self):

        self.title("Endotoxin Analysis")
        self._set_grid()
        self._add_label("raw_data", "Raw Data:", 1, 1)
        self._add_label("assay_info", "Assay Info:", 1, 2)
        self._add_button("File", self._get_raw_data, 2, 1)
        self._add_button("File", self._get_assay_info, 2, 2)
        self._add_label("data_path", self.PLACE_HOLDER_STRING, 3, 1)
        self._add_label("info_path", self.PLACE_HOLDER_STRING, 3, 2)
        self._add_button("Run", self._run, 2, 3)
        self._add_warning(self.PLACE_HOLDER_STRING, 3, 3)

    def _set_grid(self):
        self.geometry("{}x{}".format(self.SCREEN_WIDHT, self.SCREEN_HEIGHT))
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=10)
        for row in range(1, self.NUMBER_OF_ROWS + 1):
            self.rowconfigure(row, weight=1)

    def _run(self):

        # LET USER KNOW IF IT TRIES TO RUN THE PROGRAM WITHOUT UPLOADING A FILE
        if self.raw_data_filepath == "" or self.assay_info_filepath == "":
            self.labels["warning"].config(text = self.WARNING_MESSAGES[0])
            return
        else:
            self.labels["warning"].config(text = self.PLACE_HOLDER_STRING)
            self.update()

        try:

            # READ AND CLEAN THE RAW DATA FILE
            time, data = self.dp.process(self.raw_data_filepath)

            # ANALYZE THE DATA. RETURNS A DATAFRAME 
            results = self.al.analyze(time, data, self.assay_info_filepath)
        
        except Exception as e:

            self.labels["warning"].config(text = self.WARNING_MESSAGES[1])
            self._log(self.WARNING_MESSAGES[1], e)
            self._reset()
            return

        # WRITE RESULTS TO A CSV FILE IN A USER SPECIFIED LOCATION
        self._save_file(results)

        # RESET THE DataProcess AND Analysis INSTANCES SO THAT THE USER CAN DO A NEW RUN
        self._reset()

        self._log("Succesfull Run")

    def _add_label(self, label_name, _text, _col, _row):

        self.labels[label_name] = Label(self, text = _text)
        self.labels[label_name].grid(column=_col, row=_row)

    def _add_button(self, _text, _command, _col, _row):

        btn = Button(self, text = _text, command = _command)
        btn.grid(column=_col, row=_row)

    def _add_warning(self, _text, _col, _row):

        self.labels["warning"] = Label(self, text=_text, fg="red")
        self.labels["warning"].grid(column=_col, row=_row)

    def _get_raw_data(self):

        # GET THE FILE PATH FROM THE USER SELECTION
        self.raw_data_filepath = self._browse_files()

        # ADD A LABEL NEXT TO THE BUTTON TO INDICATE FILE HAS BEEN LOADED
        filename = os.path.basename(self.raw_data_filepath)
        self.labels["data_path"].config(text = filename)

    def _get_assay_info(self):

         # GET THE FILE PATH FROM THE USER SELECTION
        self.assay_info_filepath = self._browse_files()

        # ADD A LABEL NEXT TO THE BUTTON TO INDICATE FILE HAS BEEN LOADED
        filename = os.path.basename(self.assay_info_filepath)
        self.labels["info_path"].config(text = filename)

    def _browse_files(self):

        filepath = filedialog.askopenfilename(initialdir = "/", 
                                            title= "Select a File", 
                                            filetypes = (("CSV files", "*.csv"),))
        return filepath
    
    def _save_file(self, results):

        filepath = filedialog.asksaveasfilename(initialdir = "/", 
                                            title= "Select a File", 
                                            filetypes = (("CSV files", "*.csv"),))
        
        if filepath: 
            results.to_csv(filepath)
            fig_path = os.path.splitext(filepath)[0] + ".jpg"
            self.al.save_plot(fig_path)
        else:
            self._reset()
            
    def _reset(self):
        self.dp.reset()
        self.al.reset()

    def _log(self, message, exception = None):

        log_message = "\n\t{}\n\tRaw_Data_File: {}\n\tAssay_Info_File: {}".format(message, self.raw_data_filepath, self.assay_info_filepath)
        self.logger.log(log_message, exception)
        
