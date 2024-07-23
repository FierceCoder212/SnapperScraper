import pandas as pd
import json

from Helpers.SqlLiteHelper import SQLiteHelper


df = pd.read_excel("OldNewSGL.xlsx", sheet_name="Sheet1")
records = []
sgl_dict = pd.Series(df["New SGL Code"].values, index=df["Old SGL Code"]).to_dict()
del df

with open("images.json", "r") as file_to_read:
    all_images_data = json.load(file_to_read)
images_dict = {}
for data in all_images_data:
    images_dict[data["file_name"]] = data["image_url"]
del all_images_data

all_data_db = SQLiteHelper("SnapperDb.db")
read_all_db = all_data_db.get_all()
for db_record in read_all_db:
    print(db_record[0])
    break
