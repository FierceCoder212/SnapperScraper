import pandas as pd

from Helpers.ExcelSqlHelper import ExcelSqlHelper

# df = pd.read_excel("ModelList.xlsx", sheet_name="Sheet1")
# records = []
# for i, j in df.iterrows():
#     sgl_code = j["SGL Code"]
#     manufacturer = j["Manufacturer"]
#     model = j["Model"]
#     unique_product_code = j["Unique Product Code"]
#     year = j["Year"]
#     section = j["Section"]
#     record = {
#         "sgl_code": sgl_code,
#         "manufacturer": manufacturer,
#         "model": model,
#         "unique_product_code": unique_product_code,
#         "year": "",
#         "section": section,
#     }
#     records.append(record)
# print(records)
excelSheet = ExcelSqlHelper("ExcelFile.db")
data = excelSheet.execute_sql(
    "Select model, section, sgl_code from parts Group by section, model"
)
for d in data:
    print(d)
    break
