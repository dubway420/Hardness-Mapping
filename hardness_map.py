import pandas as pd
import numpy as np
from openpyxl import Workbook
import os
import seaborn as sns
import matplotlib.pyplot as plt
import ntpath

DEFAULT_X_COLUMN_INT = 5
DEFAULT_Y_COLUMN_INT = 6
DEFAULT_HARDNESS_COLUMN_INT = 9

def multiple_hardness_maps(input_folder_path, output_folder_path="Outputs", threshold=None, save_excel=True, save_image=True, axis_labels=True, vrange='default'):
    
    # Validate the input and output parameter
    validation = path_validation(input_folder_path, output_folder_path)
    
    # If valid, continue
    if validation:
        
        input_folder = validation[0]
        output_folder = validation[1]

        # Iterate through the files in the input folder
        for file in os.listdir(input_folder):
            
            # If it is a .csv file, continue
            if file.endswith('.csv'):

                # Instantiate the hardness map object and call the methods to get and process the data
                hardness_map = HardnessMap(os.path.join(input_folder, file), output_folder, threshold)
                hardness_map.get_data()
                hardness_map.create_hardness_map()

                if save_excel:
                   hardness_map.save_to_excel()

                if save_image:
                    hardness_map.display_hardness_map(axis_labels=axis_labels, vrange=vrange)


def path_validation(input_folder_path, output_folder_path):

    # Check if input_folder_path is absolute
    if not os.path.isabs(input_folder_path):
        input_folder_path = os.path.join(os.getcwd(), input_folder_path) # If not, add the current working directory to it

    # Check if specified input folder exists
    if os.path.isdir(input_folder_path):
       
       # Check if specified input folder contains .csv files
       if not any(fname.endswith('.csv') for fname in os.listdir(input_folder_path)):
           print(f"Warning: the path to the folder of inputs ({input_folder_path}) does not contain .csv files. Please check and try again.")
           return False
       
       # Check if output_folder_path is absolute
       if not os.path.isabs(output_folder_path):
          
          # If not, assume it is in the parent directory to input_folder_path 
          working_folder = os.path.dirname(input_folder_path)
          output_folder_path = os.path.join(working_folder, output_folder_path)

       # If the output_folder_path doesn't exist, create the folder
       if not os.path.isdir(output_folder_path):
           os.mkdir(output_folder_path)


    else:
        print(f"Warning: the path to the folder of inputs ({input_folder_path}) does not exist. Please check and try again.") 
        return False

    return input_folder_path, output_folder_path        

class HardnessMap:

    def __init__(self, input_filename, output_folder="", threshold=None):


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

        # The folder to save any outputs to
        self.output_folder = output_folder

        # ===================================================

        # validate and assign any threshold data i.e. if any data is below this value it 
        # will be filtered out. By default this is set to None and no data will be filtered
        self.threshold = None
        self.__threshold_validation__(threshold)

        self.data_extracted = False
        self.hardness_map_created = False
        self.saved_to_excel = False

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

        # The width and breath of the sample
        self.x_range = self.x_unique[-1] - self.x_unique[0]
        self.y_range = self.y_unique[-1] - self.y_unique[0]

        # Count the number of uniques in x and y
        self.x_length = self.x_unique.shape[0]
        self.y_length = self.y_unique.shape[0]

        # Instantiate the hardness map array. At this point, it will all zeros
        self.hardness_map = np.zeros([self.x_length, self.y_length])

        self.data_extracted = True

        
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
    

    def create_hardness_map(self):

       # Check if data has been extracted from the input file
       if not self.data_extracted:
           print("\nWarning: The get_data method has not yet been called. " + \
                 "Hence, there is no data to generate the hardness map. Call " + \
                 "the get_data method before calling this method.\n")
           
           return
                

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

       self.hardness_map_created = True 


    def save_to_excel(self, save_original_data=True, save_filename="", extension=".xlsx"):

        # Check if the hardness map has been generated
        if not self.hardness_map_created:
           print("\nWarning: The create_hardness_map method has not yet been called. " + \
                 "Hence, there is not currently a hardness map to save. Call " + \
                 "the create_hardness_map method before calling this method.\n")
           
           return

        self.save_extension = extension
        self.__save_extension_validation__()

        # If the user does not specify a save filename, use the input filename
        if save_filename == "":
            self.save_filename = os.path.join(self.output_folder, (ntpath.basename(self.filename_noext) + self.save_extension))
        # Else use the user specified name    
        else:
            self.save_filename = os.path.join(self.output_folder, (ntpath.basename(save_filename) + self.save_extension))

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
        for x_inc, row in zip(self.x_unique, self.get_hardness_map()):

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
        # print(self.save_filename)
        wb.save(self.save_filename)

        self.saved_to_excel = True


    def __save_extension_validation__(self):

        # If the user specifies an extension that does not have a fullstop at the start, add one
        if self.save_extension[0] != ".":
            self.save_extension = "." + self.save_extension

        if len(self.save_extension) < 3 or len(self.save_extension.split(".")) > 2:
            print(f"\nWarning: the extension you specified for saving ({self.save_extension}) may not be valid. Consider review.\n")
    

    def display_hardness_map(self, axis_labels=True, vrange='default', ext=".png"):

        # Check if the hardness map has been generated
        if not self.hardness_map_created:
           print("\nWarning: The create_hardness_map method has not yet been called. " + \
                 "Hence, there is not currently a hardness map to display. Call " + \
                 "the create_hardness_map method before calling this method.\n")
           
           return

        # Create a dataframe for the data
        # ====================================================================================
        dict = {}

        for label, row in zip(self.x_unique, self.get_hardness_map()):

           dict[str(label)] = row.tolist()

        self.hardness_map_df = pd.DataFrame(dict, index=self.y_unique.tolist()).transpose()

        
        # ====================================================================================

        # Specify the range for the heat bar
        
        if vrange == "default":
            vmin = self.hardnesses.min()
            vmax = self.hardnesses.max()

            print(vmin)

        elif type(vrange) == list and len(vrange) == 2:

            vmin = vrange[0]
            vmax = vrange[1]

        else:
            print("Warning: the values you specified for vrange are invalid. Either specify a list of integers ([min, max]) or leave as default to use min and max hardnesses.")            
            vmin = self.hardnesses.min()
            vmax = self.hardnesses.max()

        # ====================================================================================


        # Plot the actual graph
        sns.heatmap(self.hardness_map_df, xticklabels=axis_labels, yticklabels=axis_labels, vmin=vmin, vmax=vmax)

        image_save_filename = os.path.join(self.output_folder, ntpath.basename(self.filename_noext)) + ext

        plt.savefig(image_save_filename, bbox_inches='tight')
        plt.close()


    def get_hardness_map(self):

        """ Get the hardness map data, including any threshold filter"""

        # If a data threshold has been specified, filter out all data below this value
        if self.threshold:
            return self.__high_pass__()

        # Otherwise, just obtain the hardness map for processing
        else:
            return self.hardness_map

        # ============================================================================
        

    def __high_pass__(self):

        """ returns a hardness map which has undergone a high pass filter. This means that all values 
        below a certain threshold will be """

        # A boolean array the same shape as the hardness map. Will havea True value for all values above the threshold
        # and will be False for all values below  
        filter = self.hardness_map > self.threshold

        # returns the filtered hardness map
        return self.hardness_map * filter
    

    def __threshold_validation__(self, threshold):

        
        # If no threshold is specified, leave this as the default (None)
        if not threshold:
            return
        
        # If the threshold is an integer, set the object threshold to this value
        if type(threshold) == int:
            self.threshold = threshold
            return

        # If it is anything else, leave it as the default (None)
        print(f"Warning: the threshold you specified ({threshold}) is invalid. Ensure it is an integer > 0. Setting to None.")
        