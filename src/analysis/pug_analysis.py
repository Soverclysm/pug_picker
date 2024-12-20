import pandas as pd
import numpy as np
import seaborn as sns

class PUGAnalysis:

    def __init__(self, csv_file):
        self.data = pd.read_csv(csv_file)

