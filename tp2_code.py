import json
import pandas as pd

# Parser le fichier JSONL

data_input= pd.read_json('products.jsonl', lines=True)
print(data_input.columns())