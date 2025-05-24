from flask import Flask, render_template, jsonify, send_file, request, redirect, url_for, session
import os
import pandas as pd
from datetime import datetime
import subprocess
import signal
import psutil
import time
from functools import wraps

app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24)  # Required for session management

# Admin credentials (in a real application, these should be stored securely)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "umu2026"

# Global variable to track if attendance system is running
attendance_process = None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def is_process_running(pid):
    try:
        process = psutil.Process(pid)
        return process.is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def save_final_attendance():
    try:
        # Get today's date for the filename
        today = datetime.now().strftime('%Y-%m-%d')
        attendance_file = os.path.join("Attendance_Excels", f"{today}.csv")
        
        if os.path.exists(attendance_file):
            # Read the current attendance file
            df = pd.read_csv(attendance_file)
            
            # Mark all students who haven't been marked as present as absent
            df.loc[df['Status'].isna(), 'Status'] = 'Absent'
            
            # Save the updated attendance
            df.to_csv(attendance_file, index=False)
            print(f"Final attendance saved for {today}")
    except Exception as e:
        print(f"Error saving final attendance: {str(e)}")

@app.route('/')
def index():
    # Get list of available attendance files
    attendance_files = []
    attendance_folder = "Attendance_Excels"
    if os.path.exists(attendance_folder):
        attendance_files = [f.replace('.csv', '') for f in os.listdir(attendance_folder) if f.endswith('.csv')]
    return render_template('index.html', dates=attendance_files)

@app.route('/start_attendance')
def start_attendance():
    global attendance_process
    if attendance_process is None or not is_process_running(attendance_process.pid):
        try:
            # Start the attendance system
            attendance_process = subprocess.Popen(['python', 'main.py'])
            # Wait a bit to ensure the process started
            time.sleep(2)
            if is_process_running(attendance_process.pid):
                return jsonify({'status': 'success', 'message': 'Attendance system started'})
            else:
                attendance_process = None
                return jsonify({'status': 'error', 'message': 'Failed to start attendance system'})
        except Exception as e:
            attendance_process = None
            return jsonify({'status': 'error', 'message': f'Error starting attendance system: {str(e)}'})
    return jsonify({'status': 'error', 'message': 'Attendance system is already running'})

@app.route('/stop_attendance')
def stop_attendance():
    global attendance_process
    if attendance_process and is_process_running(attendance_process.pid):
        try:
            # Stop the attendance system
            parent = psutil.Process(attendance_process.pid)
            children = parent.children(recursive=True)
            for child in children:
                child.terminate()
            parent.terminate()
            attendance_process = None
            
            # Save final attendance status
            save_final_attendance()
            
            return jsonify({'status': 'success', 'message': 'Attendance system stopped'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Error stopping attendance system: {str(e)}'})
    attendance_process = None
    return jsonify({'status': 'error', 'message': 'Attendance system is not running'})

@app.route('/get_dates')
def get_dates():
    try:
        attendance_folder = "Attendance_Excels"
        print(f"Checking attendance folder: {attendance_folder}")  # Debug log
        
        if os.path.exists(attendance_folder):
            # Get all files in the directory
            all_files = os.listdir(attendance_folder)
            print(f"All files in directory: {all_files}")  # Debug log
            
            # Filter for both CSV and Excel files
            attendance_files = [f for f in all_files if f.endswith(('.csv', '.xlsx'))]
            print(f"Attendance files found: {attendance_files}")  # Debug log
            
            # Extract dates from filenames
            dates = [f.replace('.csv', '').replace('.xlsx', '') for f in attendance_files]
            print(f"Extracted dates: {dates}")  # Debug log
            
            if dates:
                return jsonify({
                    'status': 'success',
                    'dates': sorted(dates, reverse=True)  # Sort dates in descending order
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'No attendance files found'
                })
        
        print(f"Attendance folder not found: {attendance_folder}")  # Debug log
        return jsonify({
            'status': 'error',
            'message': 'Attendance folder not found'
        })
    except Exception as e:
        print(f"Error in get_dates: {str(e)}")  # Debug log
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('view_attendance'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/view_attendance')
@login_required
def view_attendance():
    return render_template('view_attendance.html')

@app.route('/attendance_details')
def attendance_details():
    return render_template('attendance_details.html')

@app.route('/get_attendance/<date>')
@login_required
def get_attendance(date):
    try:
        print(f"Fetching attendance for date: {date}")  # Debug log
        
        # Try CSV first, then Excel
        csv_path = os.path.join("Attendance_Excels", f"{date}.csv")
        excel_path = os.path.join("Attendance_Excels", f"{date}.xlsx")
        
        df = None
        if os.path.exists(csv_path):
            print(f"Reading CSV file: {csv_path}")  # Debug log
            df = pd.read_csv(csv_path)
        elif os.path.exists(excel_path):
            print(f"Reading Excel file: {excel_path}")  # Debug log
            df = pd.read_excel(excel_path)
        else:
            print(f"No file found for date: {date}")  # Debug log
            return jsonify({"error": "File not found"}), 404

        if df is None or df.empty:
            print("No data found in the file")  # Debug log
            return jsonify({"error": "No data found in file"}), 404

        print(f"Attendance DataFrame columns: {df.columns.tolist()}")  # Debug log
        print(f"Attendance DataFrame shape: {df.shape}")  # Debug log

        # Fill NaN values with '-'
        df = df.fillna('-')

        # Convert DataFrame to list of dictionaries
        attendance_data = df.to_dict('records')
        print(f"Number of records: {len(attendance_data)}")  # Debug log
        print(f"Sample record: {attendance_data[0] if attendance_data else 'No records'}")  # Debug log
        
        return jsonify({
            'status': 'success',
            'data': attendance_data,
            'columns': df.columns.tolist()
        })
    except Exception as e:
        print(f"Error in get_attendance: {str(e)}")  # Debug log
        return jsonify({"error": str(e)}), 500

@app.route('/Attendance_Excels/<filename>')
def serve_excel(filename):
    try:
        return send_file(
            os.path.join("Attendance_Excels", filename),
            as_attachment=False,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True) 