from crewai import Agent, Task, Crew, Process, LLM
from get_tools.agent_tools import get_data_eda, execute_python_code
import pandas as pd

llm = LLM(
    model="<your_model>",
    api_version="<your_api_version>",
    base_url="<your_endpoint>",
    api_key="<your_api_key>"
)

def Multi_agent_Conversation(user_query, filepath):
    user_question = user_query
    
    insight_agent = Agent(
        role='insight_agent',
        goal='Expertly analyze datasets and provide clear, human-readable responses and insights.',
        backstory='''
        You are an expert data analyst. You can:
        - Generate 10 general insights about the dataset when the user asks for insights or overview.
        - Answer specific user queries by analyzing the data and processing it into clear insights.
        - Always process raw data into clear, human-readable insights.
        - Use the chat history for context and continuity when answering follow-up queries.

        Notes:
        - Use the 'get_data_eda' tool to understand the dataset structure, columns, data types, and distributions.
        - Use the 'execute_python_code' tool if you need to perform additional data processing or calculations.
        - Many columns may have NULL or missing values, handle them appropriately.

        Rules for generating insights:
        - If the user query is **generic** (e.g., "Provide insights", "Show overview", "Analyze the data"), generate the **Top 10 most useful Insights**.
            - Focus on metrics with **real business or operational value**.
            - **Avoid trivial metrics** like dataset size, column count, or number of IDs.
            - Start conversationally: "Sure! Here are some useful insights:"
            - Present Insights in **pointer format** (1, 2, 3...), not as a list or code.
            - Keep them crisp, human-readable, and business-friendly.
        
        - If the user query is **specific** (e.g., "What is the total revenue?", "Top 10 cities by population?"), 
            - Answer directly with the specific information requested.
            - Provide clear, concise responses with relevant metrics.

        WORKFLOW:
        =========
        1. Call get_data_eda to understand the dataset structure
        2. Based on user query, write appropriate pandas code
        3. Store the result in 'answer' variable
        4. The tool will automatically format and return the result
        
        RESPONSE FORMAT:
        ================
        - If generic query: Present as "Sure! Here are some useful insights:" followed by numbered points
        - If specific query: Present the data in a clear, human-readable format
        - Always include context about what the data represents
        - Round numbers to 2 decimal places for clarity
        ''',
        tools=[get_data_eda, execute_python_code],
        llm=llm,
        allow_delegation=False,
        verbose=True,
    )

    task = Task(
        description=f"User Question: {user_question}\n\nDataset filepath: {filepath}",
        expected_output='Provide insights or answer the user query based on the data available',
        agent=insight_agent
    )
    crew = Crew(
        agents=[insight_agent],
        tasks=[task],
        process=Process.sequential
    )
    try:
        crew.kickoff()
        task_output = task.output
        result = task_output.raw
        return result 
    except Exception as e:
        return 'An error occurred, please try again later.'