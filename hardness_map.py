import pandas as pd


class HardnessMap:

    def __init__(self, input_filename):

        self.input_filename = input_filename

        self.dataframe = pd.read_excel(self.input_filename, encoding='utf-16', sep='\t')