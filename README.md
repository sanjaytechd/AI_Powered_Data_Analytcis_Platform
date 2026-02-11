# AI-Powered Data Analytics Platform

An intelligent data analytics platform that leverages AI agents to provide comprehensive data insights and professional visualizations. Built with CrewAI, Flask, and ECharts for interactive data exploration and analysis.

## 🎯 Features

### Core Capabilities
- **AI-Powered Data Analysis**: Automated data exploration using multi-agent AI systems
- **Comprehensive EDA**: Automatic Exploratory Data Analysis with data profiling, missing values detection, and statistical summaries
- **Natural Language Queries**: Ask questions about your data in plain English
- **Professional Visualizations**: Auto-generated interactive dashboards with multiple chart types (bar, pie, line, scatter, gauge, treemap, heatmap)
- **Multi-File Support**: Handle CSV, Excel (.xlsx, .xls), and large datasets (up to 50MB)

### Intelligence Features
- **Insight Generation**: Automatically generates 10 most useful business insights from datasets
- **Smart Query Resolution**: Handles both generic and specific data queries intelligently
- **Data Processing**: Execute Python code for complex calculations and aggregations
- **Context Awareness**: Maintains chat history for continuous conversation context

### Visualization Features
- **Dynamic Dashboard Generation**: Creates 6-chart comprehensive dashboards with diverse visualizations
- **Gradient Color Schemes**: Professional, vibrant color palettes for visual appeal
- **Interactive Charts**: Hover tooltips, legends, animations, and smooth transitions
- **Real-time Rendering**: ECharts-based visualizations with responsive design

### Data Management
- **SQL Server Integration**: Persistent storage of chat history and conversations
- **Conversation Management**: View, retrieve, and manage past analytics sessions
- **Secure File Uploads**: Sanitized file handling with secure filename processing
- **Data Privacy**: Controlled access to uploaded datasets

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- SQL Server (for database storage)
- Azure OpenAI API credentials (for GPT-4o integration)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   AZURE_OPENAI_API_KEY=<your_api_key>
   AZURE_OPENAI_ENDPOINT=<your_endpoint>
   AZURE_OPENAI_API_VERSION=<your_api_version>
   DB_CONNECTION_STRING=<your_db_connection_string>
   FLASK_ENV=development
   ```

5. **Set up SQL Server Database**
   ```sql
   CREATE DATABASE <your_database_name>;
   
   USE <your_database_name>;
   
   CREATE TABLE ChatHistory (
       Id INT PRIMARY KEY IDENTITY(1,1),
       ChatID NVARCHAR(255) NOT NULL,
       Question NVARCHAR(MAX),
       Insight NVARCHAR(MAX),
       Visualization NVARCHAR(MAX),
       Filename NVARCHAR(255),
       DateTime DATETIME DEFAULT GETDATE()
   );
   
   CREATE INDEX idx_ChatID ON ChatHistory(ChatID);
   CREATE INDEX idx_DateTime ON ChatHistory(DateTime);
   ```

6. **Run the application**
   ```bash
   python app.py
   ```
   The application will start on `http://localhost:<your_port>`

## 🔧 Configuration

### Azure OpenAI Setup
Update the API credentials in `.env` file (see `.env.example` for template):
```env
AZURE_OPENAI_API_KEY=<your_api_key>
AZURE_OPENAI_ENDPOINT=<your_endpoint>
AZURE_OPENAI_API_VERSION=<your_api_version>
AZURE_OPENAI_DEPLOYMENT_URL=<your_deployment_url>
```

### Database Configuration
Update the connection string in `.env` file:
```env
DB_CONNECTION_STRING=<your_db_connection_string>
DB_SERVER=<your_server>
DB_NAME=<your_database_name>
```

**Note**: Store sensitive database credentials in `.env` file, not in source code.

### File Upload Settings
Modify in `app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Max file size (50MB)
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}  # Supported formats
```

## 📁 Project Structure

```
.
├── app.py                      # Flask application & API endpoints
├── insight_agent.py            # AI agent for data insights
├── visualization.py            # Visualization generation agent
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── get_tools/
│   └── agent_tools.py         # Tools for data analysis (get_data_eda, execute_python_code)
├── templates/
│   ├── home.html              # Home page
│   └── index.html             # Main application interface
└── uploads/                   # Uploaded dataset storage
    ├── employee_data.csv
    ├── employee_data_large.csv
    ├── flipkart_sales_10k.csv
    └── sales_data_large.csv
```

## 🔌 API Endpoints

### File Management
- **POST `/upload`**: Upload CSV/Excel files
  - Returns: `{success: true, filepath: string, filename: string}`

### Data Analysis
- **POST `/query`**: Submit data query with visualization options
  - Body: `{query: string, filepath: string, chartEnabled: boolean, chartType: string, filename: string, chatId: string}`
  - Returns: `{chatId: string, response: string, visualization: object}`

### Conversation Management
- **GET `/get-conversations`**: Fetch all past conversations
  - Returns: Array of conversation objects
  
- **GET `/get-chat/<chat_id>`**: Retrieve specific chat history
  - Returns: Array of message objects with insights and visualizations
  
- **DELETE `/delete-chat/<chat_id>`**: Delete specific conversation
  - Returns: `{success: true}`
  
- **DELETE `/clear-all`**: Clear all conversations
  - Returns: `{success: true}`

## 🛠️ Core Components

### Insight Agent (`insight_agent.py`)
- Analyzes datasets and generates actionable insights
- Supports both generic overview and specific queries
- Uses CrewAI framework for intelligent reasoning

### Visualization Agent (`visualization.py`)
- Generates professional ECharts visualizations
- Creates multi-chart dashboards
- Applies gradient colors and animations

### Agent Tools (`get_tools/agent_tools.py`)
- **`get_data_eda`**: Load data and return comprehensive EDA information
- **`execute_python_code`**: Execute pandas operations for data processing

## 📊 Supported Visualizations

- **Bar Charts**: Category comparisons with gradient colors
- **Pie Charts**: Proportion visualization with contrasting colors
- **Line Charts**: Trend analysis with multiple series
- **Scatter Plots**: Correlation analysis
- **Gauge Charts**: KPI metrics and progress
- **Treemap**: Hierarchical data representation
- **Heatmap**: Pattern and correlation visualization
- **Dashboards**: 6-chart comprehensive overview

## 🎓 Usage Examples

### Example 1: Upload and Analyze
```bash
# Upload a CSV file
curl -X POST -F "file=@sales_data.csv" http://localhost:<your_port>/upload

# Query the dataset
curl -X POST http://localhost:<your_port>/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the top 5 products by revenue?",
    "filepath": "uploads/sales_data.csv",
    "chartEnabled": true,
    "chartType": "bar",
    "filename": "sales_data.csv",
    "chatId": "chat_123"
  }'
```

### Example 2: Generate Insights
```bash
curl -X POST http://localhost:<your_port>/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Provide insights on this dataset",
    "filepath": "uploads/flipkart_sales_10k.csv",
    "chartEnabled": true,
    "chartType": "dashboard",
    "filename": "flipkart_sales_10k.csv",
    "chatId": "chat_456"
  }'
```

## 🔒 Security Considerations

- **Environment Variables**: Never commit `.env` file. Use `.env.example` as template
- **API Credentials**: Store all API keys in `.env` file, not in source code
- **Database Credentials**: Always use environment variables for database connection strings
- **File Uploads**: All filenames are sanitized using `secure_filename()`
- **SQL Injection**: Uses parameterized queries with pyodbc
- **File Size**: Limited to 50MB max upload
- **Allowed Extensions**: Only CSV and Excel files are accepted
- **Database**: Trusted connection recommended for production
- **Sensitive Data**: Ensure `.gitignore` includes `.env`, `*.key`, and credential files

## 📝 Troubleshooting

### Issue: Database Connection Failed
**Solution**: Verify SQL Server is running and connection string is correct
```bash
# Test connection
sqlcmd -S <your_server> -d <your_database_name>
```

### Issue: API Key Invalid
**Solution**: Verify Azure OpenAI credentials in environment variables
```bash
echo $env:AZURE_OPENAI_API_KEY  # Check if set
```

### Issue: File Upload Fails
**Solution**: Check file size (max 50MB) and extension (.csv, .xlsx, .xls only)

### Issue: Visualization Not Generating
**Solution**: Ensure `chart_enabled` is true and valid chart type is provided

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| flask | 2.3.3 | Web framework |
| pandas | 2.0.3 | Data manipulation |
| openpyxl | 3.1.2 | Excel file handling |
| pyodbc | 4.0.35 | SQL Server connection |
| crewai | 0.1.0 | AI agent framework |
| werkzeug | 2.3.7 | WSGI utilities |
| python-dotenv | 1.0.0 | Environment variables |

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production (Windows)
```bash
# Using Gunicorn (Unix-like) or Waitress (Windows)
waitress-serve --port=<your_port> app:app
```

### Docker
Create `Dockerfile`:
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t ai-analytics .
docker run -p <your_port>:5000 ai-analytics
```

## 📞 Support & Contribution

For issues, feature requests, or contributions, please create an issue or pull request on the repository.

## 📄 License

This project is proprietary and confidential.

## 🎯 Roadmap

- [ ] Real-time data streaming support
- [ ] Custom metric definitions
- [ ] Export reports to PDF/PowerPoint
- [ ] Machine learning predictions
- [ ] Multi-language support
- [ ] Advanced data quality scoring
- [ ] API authentication (OAuth2)
- [ ] User roles and permissions

---

**Last Updated**: February 2026
**Version**: 1.0.0
