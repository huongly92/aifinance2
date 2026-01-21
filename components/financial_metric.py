
from components.excel_processor import ExcelProcessorAdvanced
# from excel_processor import ExcelProcessorAdvanced
map_path = "D:/aifinance_project/data/raw/Map_Complete.xlsx"
processor = ExcelProcessorAdvanced(map_path)   

LEVEL_MAP = 3

FINANCIAL_METRICS = processor.to_nested_dict_advanced(
    ['company_map','bank_map', 'security_map', 'insurance_map',\
     'company_ratio', 'bank_ratio', 'security_ratio', 'insurance_ratio'],
    key_hierarchy=['CAL_GROUP', 'CATEGORY', 'COL'],
    value_columns=['VN_NAME', 'ORDER'],
    filters={
        'LEVEL': {'<=':LEVEL_MAP}, 'CATEGORY': {'in':['BS', 'IS', 'CF', 'ratio'] }
    },
)
# print(FINANCIAL_METRICS)