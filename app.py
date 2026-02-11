from flask import Flask, render_template, request, jsonify
from insight_agent import Multi_agent_Conversation
from visualization import execute_visualization_agent
from crewai import LLM
import os
from werkzeug.utils import secure_filename
import pyodbc
import json
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# SQL Server Connection String
# Configure in .env file
DB_CONNECTION_STRING = '<your_db_connection_string>'

llm = LLM(
    model="<your_model>",
    api_version="<your_api_version>",
    base_url="<your_endpoint>",
    api_key="<your_api_key>"
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_to_database(chat_id, question, insight, visualization, filename):
    """Save chat history to SQL Server"""
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        # Convert visualization to JSON string
        viz_json = json.dumps(visualization) if visualization else None
        
        cursor.execute('''
            INSERT INTO ChatHistory (ChatID, Question, Insight, Visualization, Filename, DateTime)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (chat_id, question, insight, viz_json, filename, datetime.now()))
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Chat {chat_id} saved to database")
        return True
    except Exception as e:
        print(f"Database error: {str(e)}")
        return False


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/app')
def app_index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: CSV, XLSX, XLS'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'success': True, 'filepath': filepath, 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# ...existing code...

@app.route('/get-conversations', methods=['GET'])
def get_conversations():
    """Fetch all conversations from SQL Server"""
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT ChatID, Question, Insight, Visualization, Filename, DateTime FROM ChatHistory ORDER BY DateTime DESC')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        conversations = []
        for row in rows:
            conversations.append({
                'chatId': row[0],
                'question': row[1],
                'insight': row[2],
                'visualization': json.loads(row[3]) if row[3] else None,
                'filename': row[4],
                'dateTime': row[5].isoformat() if row[5] else None
            })
        
        return jsonify(conversations)
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get-chat/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    """Fetch specific chat history from SQL Server"""
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        cursor.execute('SELECT Question, Insight, Visualization FROM ChatHistory WHERE ChatID = ? ORDER BY DateTime ASC', (chat_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append({
                'role': 'user',
                'content': row[0]
            })
            messages.append({
                'role': 'assistant',
                'content': row[1],
                'visualization': json.loads(row[2]) if row[2] else None
            })
        
        return jsonify({'messages': messages})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/delete-chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete a specific chat from SQL Server"""
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM ChatHistory WHERE ChatID = ?', (chat_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Chat deleted'})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/clear-all', methods=['DELETE'])
def clear_all():
    """Delete all chats from SQL Server"""
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM ChatHistory')
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'All conversations cleared'})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': str(e)}), 500 

@app.route('/query', methods=['POST'])
def query():
    user_query = request.json.get('query', '')
    filepath = request.json.get('filepath', '')
    chart_enabled = request.json.get('chartEnabled', False)
    chart_type = request.json.get('chartType', 'auto')
    filename = request.json.get('filename', '')
    chat_id = request.json.get('chatId', '')  # Receive chatId from frontend
    
    if not user_query:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    if not filepath:
        return jsonify({'error': 'No dataset provided'}), 400
    
    if not chat_id:
        return jsonify({'error': 'Chat ID missing'}), 400
    
    try:
        # Get response from the agent
        response = Multi_agent_Conversation(user_query, filepath)
        
        visualizations = None
        
        # Only generate visualization if chart is enabled
        if chart_enabled:
            visualizations = execute_visualization_agent(user_query, response, filepath, chart_type)
            visualizations = visualizations.replace('```json','').replace('```','')
            
            # Parse visualization JSON if it's a string
            try:
                if isinstance(visualizations, str):
                    visualizations = json.loads(visualizations)
            except:
                visualizations = {"error": "Could not parse visualization"}
        
        # Save to database with received chatId
        save_to_database(chat_id, user_query, response, visualizations, filename)
        
        return jsonify({
            'chatId': chat_id,
            'response': response,
            'visualization': visualizations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)