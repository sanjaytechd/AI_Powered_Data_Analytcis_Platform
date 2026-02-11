from crewai import Agent, Task, Crew, Process, LLM
from get_tools.agent_tools import get_data_eda, execute_python_code
import json

llm = LLM(
    model="<your_model>",
    api_version="<your_api_version>",
    base_url="<your_endpoint>",
    api_key="<your_api_key>"
)
def execute_visualization_agent(user_query, agent_response, filepath, chart_type='auto'):
    
    if chart_type == 'dashboard' :
        visualization_instruction = '''
        Generate 6 different visualization plots that provide a comprehensive overview of the dataset.
        Merge all 6 plots into a single dashboard layout (like a PowerBI dashboard).
        The response should be a single JSON object with a dashboard structure.
        
        Requirements:
        - Each chart must be a DIFFERENT type (e.g., bar, pie, line, gauge, scatter, treemap)
        - Apply vibrant, distinct color gradients to each chart
        - For bar charts: use a gradient color scheme where each bar has a different color
        - For pie charts: use bright, contrasting colors
        - Include proper titles, legends, and formatting
        - Make it visually appealing like a professional PowerBI dashboard
        - CRITICAL: Do NOT use Python variables in JSON (like df[...].tolist()) - use static sample data instead
        '''
    else:
        visualization_instruction = f'''
        Generate a single {chart_type if chart_type != 'auto' else 'best-fit'} visualization based on the user query and data.
        
        Requirements:
        - Apply vibrant, gradient colors to the visualization
        - For bar charts: each bar should have a distinct color from a gradient palette
        - For pie charts: use bright, contrasting colors for each slice
        - For line charts: use gradient colors or multiple series with distinct colors
        - Include proper title, legend, and formatting
        - Make it visually polished and professional
        - CRITICAL: Do NOT use Python variables - extract data using execute_python_code tool first
        '''
    
    visualization_agent = Agent(
        role='visualization_agent',
        goal='Generate professional, visually appealing PowerBI-style visualizations with diverse colors and varied chart types.',
                backstory=f'''
        You are an expert in data visualization with deep knowledge of ECharts and PowerBI dashboard design.
        Your task is to generate stunning visualization code with:
        - Diverse chart types that complement each other
        - Vibrant, gradient color schemes
        - Professional styling similar to PowerBI dashboards

        {visualization_instruction}

        Color Palette Guidelines:
        - Use gradients like: ['#FF6B6B', '#FFA06B', '#FFD06B', '#FFFF6B', '#B6FF6B', '#6BFF6B'] for bar charts
        - Use bright contrasting colors for pie charts: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F']
        - Use gradient colors for line charts: multiple series with distinct colors
        - Apply smooth animations and proper spacing
        - use different colors for each element in the chart
        

        CRITICAL RULES - FOLLOW EXACTLY:
        1. OUTPUT ONLY VALID JSON - NO TEXT, NO EXPLANATIONS, NO MARKDOWN
        2. Start response with {{ and end with }}
        3. Do NOT add any words or sentences before or after the JSON
        4. Do NOT use markdown code blocks or backticks
        5. Do NOT include comments in JSON
        6. Each response MUST be parseable as valid JSON
        7. ABSOLUTELY NO JAVASCRIPT FUNCTIONS IN JSON - Use color arrays ONLY
        8. ABSOLUTELY NO PYTHON VARIABLES IN JSON - Use static data only (NO df[...], NO .tolist(), NO Python code)

        Never DO the following:
        1. Dont use any dynamic color functions or callbacks - use static color arrays
        2. Dont use Python variables like df[...].tolist() - use static sample data instead
        3. Dont include any explanations, notes, or text outside the JSON
        4. The above will cause parsing errors - use static arrays instead
    
        Rules for generating visualizations:
        - Use the ECharts library for all visualizations with rich styling
        - The response should ONLY contain valid JSON format - NO explanations or text
        - WORKFLOW:
          1. First use get_data_eda to understand the dataset
          2. Then use execute_python_code to EXTRACT actual data values and save to 'answer' variable
          3. Use those extracted values in the JSON echartsOption - NO PYTHON CODE IN JSON
          4. Store data extraction results in 'answer' variable as dictionaries/lists
        
        -CRITICAL INSTRUCTION - STORING RESULTS IN PYTHON CODE:
            When using the 'execute_python_code' tool, you MUST:
            1. Store your final result in a variable named 'answer'
            2. Never use print() statements
            3. The tool will automatically capture whatever is in the 'answer' variable
            4. Your code must END with: answer = <your_result>
        
        - For single plots, include:
          - `visualizationType`: The type of visualization (bar, pie, line, scatter, gauge, treemap, heatmap)
          - `meta`: Metadata about the visualization (title, description, insights)
          - `echartsOption`: Complete ECharts configuration with colors, animations, and styling
        
        - For dashboard layouts (6 plots), structure as:
          - `visualizationType`: "dashboard"
          - `layouts`: An array of 6 plot objects with DIFFERENT chart types
          - Each plot must have unique colors and styling
          - Arrange plots in a 2x3 grid layout
          - Include titles, legends, and proper spacing
        
        - Steps to FOLLOW STRICTLY:
          1. Use get_data_eda to understand dataset structure
          2. Use execute_python_code to extract all necessary data values FIRST
          3. Store extracted data in 'answer' variable
          4. Use the extracted values DIRECTLY in echartsOption (NOT Python code)
          5. Do NOT use execute_python_code to run ECharts rendering code
          6. Do NOT include any Python variables in the JSON
          7. Each bar/element should have DIFFERENT colors from the gradient palette
          8. Include proper ECharts options like: grid, xAxis, yAxis, tooltip, legend, etc.
        
        - ECharts Best Practices:
          - Add smooth animations: animationDuration: 1000, animationEasing: 'cubicOut'
          - Include interactive tooltips with formatter
          - Use proper grid spacing for readability
          - Add legend with appropriate positioning
        
        - Ensure visualizations are highly relevant to the user query and data provided.
        - FINAL REQUIREMENT: Response must be ONLY JSON with no additional text whatsoever.
        ''',
        tools=[get_data_eda, execute_python_code],
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    task = Task(
        description=f"Generate visualization for query: '{user_query}'\n\nAgent Response: {agent_response}\n\nDataset filepath: {filepath}\n\nCreate a professionally styled visualization with vibrant colors and diverse chart types. CRITICAL: Response must be ONLY valid JSON with no explanations, no text, no markdown formatting, no Python variables, and no special characters.",
        expected_output='Valid JSON object only - no text, no explanations, no markdown code blocks, no Python variables. Start with {{ and end with }}',
        agent=visualization_agent,
    )
    
    crew = Crew(
        agents=[visualization_agent],
        tasks=[task],
        process=Process.sequential
    )
    
    try:
        crew.kickoff()
        task_output = task.output
        result = task_output.raw
        
        # More aggressive cleanup
        result = result.strip()
        result = result.replace("```json", "").replace("```", "").strip()
        result = result.replace('```', '').strip()
        result = result.replace("json\n", "").strip()
        
        # Remove any leading/trailing text before first { and after last }
        start_idx = result.find('{')
        end_idx = result.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            result = result[start_idx:end_idx+1]
        
        return result
    except Exception as e:
        return json.dumps({'error': f'Visualization generation failed: {str(e)}'})