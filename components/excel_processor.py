"""
Excel Processor - Phiên bản nâng cấp với khả năng tùy chỉnh dictionary linh hoạt
Hỗ trợ: chọn key-value tùy ý, nested dictionary, group by, mapping
"""

import pandas as pd
from typing import Union, List, Dict, Any, Optional, Callable
import ast
import warnings
warnings.filterwarnings('ignore')


class ExcelProcessorAdvanced:
    """Class xử lý file Excel với khả năng tùy chỉnh cao"""
    
    def __init__(self, file_path: str):
        """
        Khởi tạo processor với file Excel
        
        Args:
            file_path: Đường dẫn đến file Excel
        """
        self.file_path = file_path
        self.excel_file = pd.ExcelFile(file_path)
        self.sheet_names = self.excel_file.sheet_names    
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Áp dụng filters lên DataFrame
        
        Args:
            df: DataFrame cần lọc
            filters: Dict với key là tên cột và value là điều kiện
                    - Giá trị đơn: so sánh bằng
                    - List/tuple/set: kiểm tra isin
                    - Callable: áp dụng function
                    - Dict với operators: {'>=': 10, '<': 100}
        
        Returns:
            DataFrame đã được lọc
        """
        mask = pd.Series([True] * len(df))
        
        for col, condition in filters.items():
            if col not in df.columns:
                print(f"Cảnh báo: Cột '{col}' không tồn tại")
                continue
            
            # Callable function
            if callable(condition):
                mask &= df[col].apply(condition)
            
            # List/tuple/set - isin
            elif isinstance(condition, (list, tuple, set)):
                mask &= df[col].isin(condition)
            
            # Dict với operators
            elif isinstance(condition, dict):
                for operator, value in condition.items():
                    if operator == '==':
                        mask &= (df[col] == value)
                    elif operator == '!=':
                        mask &= (df[col] != value)
                    elif operator == '>':
                        mask &= (df[col] > value)
                    elif operator == '>=':
                        mask &= (df[col] >= value)
                    elif operator == '<':
                        mask &= (df[col] < value)
                    elif operator == '<=':
                        mask &= (df[col] <= value)
                    elif operator == 'in':
                        mask &= df[col].isin(value)
                    elif operator == 'not_in':
                        mask &= ~df[col].isin(value)
                    elif operator == 'contains':
                        mask &= df[col].astype(str).str.contains(value, na=False)
                    elif operator == 'startswith':
                        mask &= df[col].astype(str).str.startswith(value, na=False)
                    elif operator == 'endswith':
                        mask &= df[col].astype(str).str.endswith(value, na=False)
                    elif operator == 'between':
                        mask &= df[col].between(value[0], value[1])
                    elif operator == 'isnull':
                        mask &= df[col].isnull() if value else df[col].notnull()
                    else:
                        print(f"Cảnh báo: Operator '{operator}' không được hỗ trợ")
            
            # Giá trị đơn - so sánh bằng
            else:
                mask &= (df[col] == condition)
        
        return df[mask]
    
    def to_nested_dict(
        self,
        sheet_name: Union[str, List[str]],
        key_hierarchy: List[str],
        value_columns: Union[str, List[str], None] = None,
        filters: Optional[Dict[str, Any]] = None,
        add_sheet_column: bool = False
    ) -> Dict:
        """
        Tạo nested dictionary theo hierarchy (OPTIMIZED VERSION)
        
        Args:
            sheet_name: Tên sheet hoặc danh sách các tên sheet
            key_hierarchy: Danh sách các cột làm key theo thứ tự (từ ngoài vào trong)
            value_columns: Cột/các cột làm value ở level cuối
            filters: Điều kiện lọc (xem _apply_filters để biết cú pháp)
            add_sheet_column: Nếu True, thêm cột '_sheet_name' vào DataFrame
        
        Returns:
            Nested dictionary
        """
        # ====== HÀM HELPER ĐỂ PARSE STRING → TUPLE ======
        def _parse_tuple_string(value):
            """
            Chuyển string dạng tuple thành tuple thực sự
            VD: "('A', 'B', 'C')" → ('A', 'B', 'C')
            """
            if not isinstance(value, str):
                return value
            
            stripped = value.strip()
            # Kiểm tra có phải dạng tuple không: bắt đầu '(', kết thúc ')', có dấu ','
            if stripped.startswith('(') and stripped.endswith(')') and ',' in stripped:
                try:
                    parsed = ast.literal_eval(stripped)
                    # Chỉ trả về nếu kết quả là tuple
                    if isinstance(parsed, tuple):
                        return parsed
                except (ValueError, SyntaxError):
                    # Nếu parse lỗi thì giữ nguyên string
                    pass
            
            return value
        
        def _parse_nested_dict(d):
            """
            Duyệt đệ quy qua nested dict và parse tất cả string values thành tuple
            """
            if isinstance(d, dict):
                return {k: _parse_nested_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [_parse_tuple_string(item) for item in d]
            else:
                return _parse_tuple_string(d)

        
        # Đọc DataFrame
        if isinstance(sheet_name, str):
            df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
        else:
            dfs = []
            for sheet in sheet_name:
                temp_df = pd.read_excel(self.excel_file, sheet_name=sheet)
                if add_sheet_column:
                    temp_df['_sheet_name'] = sheet
                dfs.append(temp_df)
            df = pd.concat(dfs, ignore_index=True)
        
        # Áp dụng filters
        if filters:
            df = self._apply_filters(df, filters)
        
        # Kiểm tra các cột trong hierarchy
        missing = set(key_hierarchy) - set(df.columns)
        if missing:
            raise ValueError(f"Các cột không tồn tại: {missing}")
        
        # Xác định value_columns
        if value_columns is None:
            value_cols = [col for col in df.columns if col not in key_hierarchy]
        elif isinstance(value_columns, str):
            value_cols = [value_columns]
        else:
            value_cols = list(value_columns)
        
        # Tối ưu: Chỉ giữ các cột cần thiết
        needed_cols = key_hierarchy + value_cols
        df = df[needed_cols]
        
        # Tối ưu: Convert sang records một lần duy nhất
        # Nhanh hơn iterrows() rất nhiều
        records = df.to_dict('records')
        
        # Tối ưu: Pre-calculate một số giá trị
        hierarchy_len = len(key_hierarchy)
        single_value = len(value_cols) == 1
        value_col_name = value_cols[0] if single_value else None
        
        # Tạo nested dict với optimized logic
        result = {}
        
        for record in records:
            current = result
            
            # Traverse hierarchy (unrolled last iteration)
            for i in range(hierarchy_len - 1):
                key = record[key_hierarchy[i]]
                # Tối ưu: Sử dụng setdefault thay vì if-check
                current = current.setdefault(key, {})
            
            # Level cuối cùng
            last_key = record[key_hierarchy[-1]]
            if single_value:
                current[last_key] = record[value_col_name]
            else:
                # Tối ưu: Dictionary comprehension nhanh hơn loop
                current[last_key] = {col: record[col] for col in value_cols}
        
        
        # ====== BƯỚC MỚI: PARSE TẤT CẢ STRING → TUPLE ======
        result = _parse_nested_dict(result)
        
        return result
    
    def to_nested_dict_advanced(
        self,
        sheet_name: Union[str, List[str]],
        key_hierarchy: List[str],
        value_columns: Union[str, List[str], None] = None,
        filters: Optional[Dict[str, Any]] = None,
        add_sheet_column: bool = False,
        drop_duplicates: bool = False,
        sort_by: Optional[Union[str, List[str]]] = None,
        aggregate: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Phiên bản nâng cao của to_nested_dict (OPTIMIZED VERSION)
        
        Args:
            sheet_name: Tên sheet hoặc danh sách các tên sheet
            key_hierarchy: Danh sách các cột làm key theo thứ tự
            value_columns: Cột/các cột làm value ở level cuối
            filters: Điều kiện lọc
            add_sheet_column: Thêm cột '_sheet_name'
            drop_duplicates: Loại bỏ các dòng trùng lặp
            sort_by: Sắp xếp theo cột (hoặc list các cột)
            aggregate: Tổng hợp dữ liệu khi có duplicate keys
                    {'value_col': 'sum'/'mean'/'first'/'last'/'list'}
        
        Returns:
            Nested dictionary
        """
        # ====== HÀM HELPER ĐỂ PARSE STRING → TUPLE ======
        def _parse_tuple_string(value):
            """
            Chuyển string dạng tuple thành tuple thực sự
            VD: "('A', 'B', 'C')" → ('A', 'B', 'C')
            """
            if not isinstance(value, str):
                return value
            
            stripped = value.strip()
            # Kiểm tra có phải dạng tuple không: bắt đầu '(', kết thúc ')', có dấu ','
            if stripped.startswith('(') and stripped.endswith(')') and ',' in stripped:
                try:
                    parsed = ast.literal_eval(stripped)
                    # Chỉ trả về nếu kết quả là tuple
                    if isinstance(parsed, tuple):
                        return parsed
                except (ValueError, SyntaxError):
                    # Nếu parse lỗi thì giữ nguyên string
                    pass
            
            return value
        
        def _parse_nested_dict(d):
            """
            Duyệt đệ quy qua nested dict và parse tất cả string values thành tuple
            """
            if isinstance(d, dict):
                return {k: _parse_nested_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [_parse_tuple_string(item) for item in d]
            else:
                return _parse_tuple_string(d)

        
        # Đọc DataFrame
        if isinstance(sheet_name, str):
            df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
        else:
            dfs = []
            for sheet in sheet_name:
                temp_df = pd.read_excel(self.excel_file, sheet_name=sheet)
                if add_sheet_column:
                    temp_df['_sheet_name'] = sheet
                dfs.append(temp_df)
            df = pd.concat(dfs, ignore_index=True)
        
        # Áp dụng filters
        if filters:
            df = self._apply_filters(df, filters)
        
        # Drop duplicates
        if drop_duplicates:
            df = df.drop_duplicates()
        
        # Sort
        if sort_by:
            df = df.sort_values(sort_by)
        
        # Kiểm tra các cột trong hierarchy
        missing = set(key_hierarchy) - set(df.columns)
        if missing:
            raise ValueError(f"Các cột không tồn tại: {missing}")
        
        # Xác định value_columns
        if value_columns is None:
            value_cols = [col for col in df.columns if col not in key_hierarchy]
        elif isinstance(value_columns, str):
            value_cols = [value_columns]
        else:
            value_cols = list(value_columns)
        
        # Tối ưu: Chỉ giữ các cột cần thiết
        needed_cols = key_hierarchy + value_cols
        df = df[needed_cols]
        
        # Pre-calculate constants
        hierarchy_len = len(key_hierarchy)
        single_value = len(value_cols) == 1
        value_col_name = value_cols[0] if single_value else None
        
        # Tạo nested dict
        result = {}
        
        if aggregate:
            # Path với aggregation - sử dụng groupby (đã tối ưu)
            grouped = df.groupby(key_hierarchy, sort=False)
            
            # Tối ưu: Pre-process aggregation functions
            agg_funcs = {}
            for col in value_cols:
                func = aggregate.get(col, 'first')
                if func == 'list':
                    agg_funcs[col] = ('list', lambda x: x.tolist())
                elif func in ['sum', 'mean', 'first', 'last', 'min', 'max']:
                    agg_funcs[col] = (func, func)
                else:
                    agg_funcs[col] = ('first', 'first')
            
            for keys, group in grouped:
                current = result
                keys_list = keys if isinstance(keys, tuple) else (keys,)
                
                # Traverse hierarchy (optimized with setdefault)
                for i in range(hierarchy_len - 1):
                    current = current.setdefault(keys_list[i], {})
                
                # Level cuối cùng - áp dụng aggregation
                last_key = keys_list[-1]
                
                if single_value:
                    func_name, func = agg_funcs[value_col_name]
                    if func_name == 'list':
                        current[last_key] = func(group[value_col_name])
                    else:
                        current[last_key] = group[value_col_name].agg(func)
                else:
                    current[last_key] = {}
                    for col in value_cols:
                        func_name, func = agg_funcs[col]
                        if func_name == 'list':
                            current[last_key][col] = func(group[col])
                        else:
                            current[last_key][col] = group[col].agg(func)
        
        else:
            # Path không aggregation - tối ưu với to_dict('records')
            records = df.to_dict('records')
            
            for record in records:
                current = result
                
                # Traverse hierarchy (unrolled last iteration)
                for i in range(hierarchy_len - 1):
                    key = record[key_hierarchy[i]]
                    current = current.setdefault(key, {})
                
                # Level cuối cùng
                last_key = record[key_hierarchy[-1]]
                if single_value:
                    current[last_key] = record[value_col_name]
                else:
                    current[last_key] = {col: record[col] for col in value_cols}
        
        
        # ====== BƯỚC MỚI: PARSE TẤT CẢ STRING → TUPLE ======
        result = _parse_nested_dict(result)
        
        return result
    
    def get_keys_from_key(self, data, target_key, level=1):
        """
        Lấy keys ở cấp độ N từ một key cụ thể hoặc đường dẫn keys
        
        Args:
            data: Dictionary
            target_key: Key cần lấy (str: 'company' hoặc list: ['company', 'info'])
            level: Số cấp độ đi sâu vào từ target_key (mặc định = 1)
        
        Returns:
            List keys
        """
        # Chuẩn hóa target_key thành list
        if isinstance(target_key, str):
            key_path = [target_key]
        elif isinstance(target_key, list):
            key_path = target_key
        else:
            return []
        
        # Đi theo đường dẫn key_path để tìm vị trí bắt đầu
        current = data
        for key in key_path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return []  # Không tìm thấy đường dẫn
        
        # Nếu level = 1, trả về keys ngay tại vị trí hiện tại
        if level == 1:
            return list(current.keys()) if isinstance(current, dict) else []
        
        # Đi sâu vào các level tiếp theo
        for _ in range(level - 1):
            next_level = []
            
            if isinstance(current, dict):
                for value in current.values():
                    if isinstance(value, dict):
                        next_level.append(value)
            elif isinstance(current, list):
                for item in current:
                    if isinstance(item, dict):
                        next_level.append(item)
            
            current = next_level
            
            if not current:
                return []
        
        # Lấy keys ở level cuối cùng
        keys = []
        if isinstance(current, list):
            for item in current:
                if isinstance(item, dict):
                    keys.extend(item.keys())
        elif isinstance(current, dict):
            keys = list(current.keys())
        
        return keys
    
    def get_keys_from_multiple_keys(self, data, target_keys, level=1):
        all_keys = set()  # Dùng set thay vì list
        
        for target_key in target_keys:
            keys = self.get_keys_from_key(data, target_key, level)
            all_keys.update(keys)  # update thay vì extend
        
        return list(all_keys)
    
    
# ============================================================================
# VÍ DỤ SỬ DỤNG
# ============================================================================

if __name__ == "__main__":
    file_path = "D:/aifinance_project/data/raw/Map_Complete.xlsx"
    processor = ExcelProcessorAdvanced(file_path)   

    result = processor.to_nested_dict(
        ['company','bank'],
        key_hierarchy=['CAL_GROUP', 'COL'],
        value_columns='ALGO'
    )
    print(result)

    result = processor.to_nested_dict_advanced(
        ['company'],
        key_hierarchy=['CAL_GROUP', 'COL'],
        value_columns='ALGO',
        filters={
            'LEVEL': {'<=':1},
        },
    )
    print(result)

    data = processor.get_keys_from_key(result, 'company', level = 1)
    print(data)