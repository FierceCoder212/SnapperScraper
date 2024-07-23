import pandas as pd
import json

from Helpers.SqlLiteHelper import SQLiteHelper
from Models.ImageModel import ImageModel


df = pd.read_excel("OldNewSGL.xlsx", sheet_name="Sheet1")
sgl_dict = pd.Series(df["New SGL Code"].values, index=df["Old SGL Code"]).to_dict()
del df

with open("images.json", "r") as file_to_read:
    all_images_data = json.load(file_to_read)
images_dict = {}

for data in all_images_data:
    images_dict[data["file_name"]] = data["image_url"]
del all_images_data
# updateImage json file

all_data_db = SQLiteHelper("SnapperDb.db")
read_all_db = all_data_db.get_all()
del all_data_db

new_data_base = SQLiteHelper("NewSnapperDb.db")
images: list[ImageModel] = []
records = []
for data in read_all_db:
    new_sgl_model = sgl_dict.get(data[0])
    old_sgl_model = data[0]
    section = data[1]
    part_number = data[2]
    description = data[3]
    item_number = data[4]
    old_section_diagram = data[5]
    new_section_diagram = old_section_diagram.replace(old_sgl_model, new_sgl_model)
    record = {
        "sgl_unique_model_code": new_sgl_model,
        "section": section,
        "part_number": part_number,
        "description": description,
        "item_number": item_number,
        "section_diagram": new_section_diagram,
    }
    images.append(
        ImageModel(
            file_name=new_section_diagram, image_url=images_dict[old_section_diagram]
        )
    )
    records.append(record)
new_data_base._insert_many_records(records)
with open("newImages.json", "w") as json_file:
    json_file.write(json.dumps(images, indent=4))
