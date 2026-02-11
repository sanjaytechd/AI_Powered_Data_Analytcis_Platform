from crewai.tools import tool
import pandas as pd
import json
from io import StringIO
import sys

# Global variable to store loaded dataframe
loaded_dataframe = None

@tool('get_data_eda')
def get_data_eda(filepath: str) -> str:
    '''
    Load a CSV or Excel file and return comprehensive EDA information including:
    - Dataset shape, columns, data types
    - Missing values summary
    - Basic statistics
    - Sample data
    '''
    global loaded_dataframe
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
        else:
            return "Error: Unsupported file format. Use CSV or Excel files."
        
        loaded_dataframe = df
        
        data_types_dict = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        eda_info = {
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "data_types": data_types_dict,
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
            "basic_stats": df.describe().to_dict(),
            "sample_data": df.head(5).to_dict(),
            "memory_usage": str(df.memory_usage(deep=True).sum() / 1024**2) + " MB"
        }
        
        return json.dumps(eda_info, indent=2)
    except Exception as e:
        return f"Error loading dataset: {str(e)}"
    
@tool('execute_python_code')
def execute_python_code(code: str) -> str:
    '''
    Execute Python code for data processing and analysis.
    The global 'df' variable contains the loaded dataset.
    
    IMPORTANT: Always store results in a variable called 'answer' at the end of your code.
    
    Examples:
    1. For aggregations: answer = df.groupby('Brand')['Revenue'].sum().sort_values(ascending=False).head(5)
    2. For calculations: answer = df['Revenue'].sum()
    3. For filtering: answer = df[df['Category'] == 'Electronics']
    
    Return results as JSON string.
    '''
    global loaded_dataframe
    
    if loaded_dataframe is None:
        return "Error: No dataset loaded. Use get_data_eda first."
    
    try:
        # Create a safe execution environment
        local_env = {
            'df': loaded_dataframe,
            'pd': pd,
            'json': json,
            'answer': None
        }
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            # Execute the code
            exec(code, local_env)
            result = local_env.get('answer', None)
        except Exception as exec_error:
            sys.stdout = old_stdout
            return f"Error in code execution: {str(exec_error)}"
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        # Return the evaluated result
        if result is not None:
            if isinstance(result, pd.DataFrame):
                return result.to_json(orient='records', indent=2, default_handler=str)
            elif isinstance(result, pd.Series):
                return json.dumps(result.to_dict(), indent=2, default=str)
            elif isinstance(result, dict):
                return json.dumps(result, indent=2, default=str)
            elif isinstance(result, list):
                return json.dumps(result, indent=2, default=str)
            else:
                return str(result)
        
        return output if output else "Code executed successfully"
    
    except Exception as e:
        sys.stdout = old_stdout
        return f"Error: {str(e)}"
