import pandas as pd

from Helpers.ExcelSqlHelper import ExcelSqlHelper

excelSheet = ExcelSqlHelper("ExcelFile.db")
data = excelSheet.execute_sql(
    "Select model, section, sgl_code from parts Group by section, model"
)
for d in data:
    print(d)
    break
