import math

import requests
from Helpers.SqlLiteHelper import SQLiteHelper

name_of_db = "SnapperDb.db"
load_prev_db = SQLiteHelper(name_of_db)
prev_parts = load_prev_db.get_all()
del load_prev_db

records = []

for part in prev_parts:
    sgl_code = part[0]
    section = part[1]
    part_number = part[2]
    description = part[3]
    item_number = part[4]
    section_diagram = part[5]
    record = {
        "id": 0,
        "sglUniqueModelCode": sgl_code,
        "section": section,
        "partNumber": part_number,
        "itemNumber": item_number,
        "description": description,
        "sectonDiagram": section_diagram,
    }
    records.append(record)
    break
page_size = 100000
total_length = len(records)
num_pages = math.ceil(total_length / page_size)

for i in range(num_pages):
    start_index = i * page_size
    end_index = start_index + page_size
    chunk_records = records[start_index:end_index]
    response = requests.post("http://108.181.167.26:8080/AddParts", json=records[0:1])
