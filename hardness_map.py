import pandas as pd
import numpy as np
from openpyxl import Workbook
import os

DEFAULT_X_COLUMN_INT = 5
DEFAULT_Y_COLUMN_INT = 6
DEFAULT_HARDNESS_COLUMN_INT = 9

class HardnessMap:

    def __init__(self, input_filename):

        self.input_filename = input_filename

        # Check that the file exists 
        # ===================================================
        if not os.path.isfile(self.input_filename):
            print(f"\nWarning: a file with the filename you specified ({self.input_filename}) can not be found.\n")


        # Split the filename into the name and extension
        # ===================================================
        filename_split = os.path.splitext(self.input_filename)

        self.filename_noext = filename_split[0]
        self.file_ext = filename_split[1]

        # Check that the extension is .csv
        if not self.file_ext == ".csv":
            print(f"\nWarning: the filename you specified ({self.input_filename}) is not a .csv file.\n")


    def get_data(self, encoding='utf-16', delineator='\t', header_row=0):    

        self.encoding = encoding
        self.delineator = delineator
        self.header_row = header_row

        # Extracts data from the worksheet
        self.dataframe = pd.read_csv(self.input_filename, encoding='utf-16', sep='\t', header=0)

        # Gets the column headers and assigns them to an object variable 'keys'
        self.keys = self.dataframe.keys()

        # Ensure that the default columns are valid - if not this class method will reassign them or throw an error
        assert(self.__default_column_verification__())

        # Extract the x and y columns
        self.x = self.dataframe[self.keys[self.x_column]].values
        self.y = self.dataframe[self.keys[self.y_column]].values

        # Extract the hardnesses
        self.hardnesses = self.dataframe[self.keys[self.hardness_column]].values

        # Create ordered arrays of the unique values from the x and y columns
        self.x_unique = np.unique(self.x)
        self.y_unique = np.unique(self.y)

        # Count the number of uniques in x and y
        self.x_length = self.x_unique.shape[0]
        self.y_length = self.y_unique.shape[0]

        # Instantiate the hardness map array. At this point, it will all zeros
        self.hardness_map = np.zeros([self.x_length, self.y_length])

        

    def __default_column_verification__(self):
        
        self.x_column = DEFAULT_X_COLUMN_INT
        self.y_column = DEFAULT_Y_COLUMN_INT
        self.hardness_column = DEFAULT_HARDNESS_COLUMN_INT

    # Validating x value column
    # =====================================================================
        x_found = False

        if "XAbs" in self.keys[self.x_column]:
            x_found = True

        else:
            print(f"\nThe X values were not found in the column which normally contains them (default: {DEFAULT_X_COLUMN_INT}).\n") 

            for i, key in enumerate(self.keys):

                if "XAbs" in key:
                    print(f"\nX values were found in column index {i}. Overriding default value of {DEFAULT_X_COLUMN_INT}. Recommend the user reviews the source file. Continuing... \n")
                    self.x_column = i
                    x_found = True
                    break

    
    # Validating y value column
    # =====================================================================
        y_found = False

        if "YAbs" in self.keys[self.y_column]:
            y_found = True

        else:
            print(f"\nThe Y values were not found in the column which normally contains them (default: {DEFAULT_Y_COLUMN_INT}).\n") 

            for i, key in enumerate(self.keys):

                if "YAbs" in key:
                    print(f"\nY values were found in column index {i}. Overriding default value of {DEFAULT_Y_COLUMN_INT}. Recommend the user reviews the source file. Continuing... \n")
                    self.y_column = i
                    y_found = True
                    break     

    # Validating hardness column
    # =====================================================================
        hardness_found = False

        if "Hardness" in self.keys[self.hardness_column]:
            hardness_found = True

        else:
            print(f"\nThe hardness values were not found in the column which normally contains them (default: {DEFAULT_HARDNESS_COLUMN_INT}).\n") 

            for i, key in enumerate(self.keys):

                if "Hardness" in key:
                    print(f"\nHardness were found in column index {i}. Overriding default value of {DEFAULT_HARDNESS_COLUMN_INT}. Recommend the user reviews the source file. Continuing... \n")
                    self.hardness_column = i
                    hardness_found = True
                    break                   


        return x_found * y_found * hardness_found        
    

    def get_hardness_map(self):

        # Iterate through the unique x values
       for i, x_value in enumerate(self.x_unique):
    
            # The indices of the values where x is equal to the x value in this iteration 
            x_match_ind = np.argwhere(self.x==x_value)

            # Get the equivalent y values corresponding to the matched values 
            y_values = self.y[x_match_ind]

            # Get the hardnesses corresponding to the matched values
            hardness = self.hardnesses[x_match_ind]

            # Iterate through the matches values and assign the hardnesses to the map
            for y_value, hardness_value in zip(y_values, hardness):

                # Get the y index of the hardness map corresponding to the y value
                j = np.argwhere(self.y_unique==y_value)[0][0]

                # Assign these values to the hardness map
                self.hardness_map[i, j] = hardness_value


    def save_to_excel(self, save_original_data=True, save_filename="", extension=".xlsx"):

        self.save_extension = extension
        self.__save_extension_validation__()

        # If the user does not specify a save filename, use the input filename
        if save_filename == "":
            self.save_filename = self.filename_noext + self.save_extension
        # Else use the user specified name    
        else:
            self.save_filename = save_filename + self.save_extension

        # Instantiate the Excel workbook
        wb = Workbook()
        ws = wb.active   

        ws.title = "Map"

        # append the x values to the top row of the excel sheet
        first_row_list = self.y_unique.tolist()

        # place a blank cell top left
        first_row_list.insert(0, " ")

        # Write the first row to the sheet
        ws.append(first_row_list)

        # Write each row of the hardness map to the Excel sheet
        for x_inc, row in zip(self.x_unique, self.hardness_map):

            row_list = row.tolist()

            # Put the x increment in the left most column
            row_list.insert(0, x_inc)
            ws.append(row_list)


        if save_original_data:
            ws2 = wb.create_sheet("Original")

            original_data = self.dataframe.values

            ws2.append(self.keys.to_list())
            for row in original_data:
                ws2.append(row.tolist())

        # Save the sheet
        wb.save(self.save_filename)

    def __save_extension_validation__(self):

        # If the user specifies an extension that does not have a fullstop at the start, add one
        if self.save_extension[0] != ".":
            self.save_extension = "." + self.save_extension

        if len(self.save_extension) < 3 or len(self.save_extension.split(".")) > 2:
            print(f"\nWarning: the extension you specified for saving ({self.save_extension}) may not be valid. Consider review.\n")
    