from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime, timedelta
from calendar import monthrange
import numpy as np
import matplotlib.colors as mcolors
import pytz  # Import pytz for timezone handling
import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot
import matplotlib.pyplot as plt
import pandas as pd
import july
from july.utils import date_range
import numpy as np
import matplotlib.colors as mcolors

app = Flask(__name__)

DATA_FILE = 'tasks.json'

# Define US Eastern Time Zone, change if needed
eastern = pytz.timezone('US/Eastern')

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    generate_heatmap()
    return render_template('home.html')

@app.route('/add_tasks', methods=['GET', 'POST'])
def add_tasks():
    # Get tomorrow's date in Eastern Time
    tomorrow = (datetime.now(eastern) + timedelta(days=1)).strftime('%Y-%m-%d')
    data = load_data()

    if request.method == 'POST':
        tasks = request.form.getlist('task')
        importance = request.form.getlist('importance')

        # Existing tasks for tomorrow
        existing_tasks = data.get(tomorrow, {}).get('tasks', [])

        # New tasks from the form
        new_tasks = [{'description': t, 'importance': int(i), 'completed': False} for t, i in zip(tasks, importance)]

        # Combine existing tasks with new tasks
        all_tasks = existing_tasks + new_tasks

        # Save tasks for tomorrow
        data[tomorrow] = {
            'tasks': all_tasks,
            'excuse': data.get(tomorrow, {}).get('excuse', "")
        }
        save_data(data)
        return redirect(url_for('home'))
    else:
        # Retrieve existing tasks for tomorrow if any
        existing_tasks = data.get(tomorrow, {}).get('tasks', [])
        return render_template('add_tasks.html', date=tomorrow, existing_tasks=existing_tasks)

@app.route('/today_tasks', methods=['GET', 'POST'])
def today_tasks():
    # Get today's date in Eastern Time
    today = datetime.now(eastern).strftime('%Y-%m-%d')
    data = load_data()

    if today not in data:
        message = "No tasks for today."
        return render_template('message.html', message=message)

    if request.method == 'POST':
        completed_tasks = request.form.getlist('completed')
        for task in data[today]['tasks']:
            # Toggle task completion based on whether it's in the completed_tasks list
            if task['description'] in completed_tasks:
                task['completed'] = True
            else:
                task['completed'] = False  # Set to False if it's not checked
        save_data(data)
        return redirect(url_for('home'))
    else:
        tasks = data[today]['tasks']
        return render_template('today_tasks.html', tasks=tasks)


def generate_heatmap():

    data = load_data()
    dates = []
    completion_rates = []

    # Get today's date in Eastern Time
    today = datetime.now(eastern).date()

    for date_str, details in data.items():
        date = pd.to_datetime(date_str).date()
        if date < today:
            # Calculate completion rate for past dates
            total_tasks = len(details['tasks'])
            completed_tasks = sum(1 for task in details['tasks'] if task['completed'])
            completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
            dates.append(date)
            completion_rates.append(completion_rate)
        else:
            # Set completion rate to NaN for today and future dates
            dates.append(date)
            completion_rates.append(np.nan)

    # Ensure all dates in the current month are included
    start_date = datetime(today.year, today.month, 1).date()
    last_day = monthrange(today.year, today.month)[1]
    end_date = datetime(today.year, today.month, last_day).date()

    dates_all = pd.date_range(start=start_date, end=end_date).date

    # Initialize completion rates for all dates in the month
    completion_dict = {date: np.nan for date in dates_all}

    # Update completion rates with actual data
    for date, rate in zip(dates, completion_rates):
        completion_dict[date] = rate

    dates = list(completion_dict.keys())
    completion_rates = list(completion_dict.values())

    # Create a custom colormap
    cmap = plt.get_cmap('BuPu')
    cmap_colors = cmap(np.arange(cmap.N))

    # Set the first color (representing zero completion) to light grey
    light_grey_rgba = np.array([0.9, 0.9, 0.9, 1.0])  # Light grey
    cmap_colors[0] = light_grey_rgba
    new_cmap = mcolors.ListedColormap(cmap_colors)

    # Set color for NaN values (e.g., for today and future dates)
    new_cmap.set_bad(color='white')

    # Generate the heatmap using July
    plt.figure(figsize=(8, 2))
    ax = plt.gca()

    norm = norm = mcolors.PowerNorm(gamma=0.5)
    july.heatmap(
        dates,
        completion_rates,
        cmap="github",
        colorbar=False,
        date_label=True,
        month_grid=False,
        horizontal=True,
        ax=ax
    )

    # Optionally adjust text properties
    for text in ax.texts:
        text.set_color('black')
        text.set_fontsize(8)

    plt.savefig('static/heatmap.png', bbox_inches='tight')
    plt.close()

@app.route('/add_excuse', methods=['GET', 'POST'])
def add_excuse():
    # Get today's date in Eastern Time
    today = datetime.now(eastern).strftime('%Y-%m-%d')
    data = load_data()

    if request.method == 'POST':
        excuse = request.form['excuse']
        if today in data:
            data[today]['excuse'] = excuse
            save_data(data)
        else:
            # If there are no tasks for today, create an entry
            data[today] = {
                'tasks': [],
                'excuse': excuse
            }
            save_data(data)

        # Display the message after submitting the excuse
        message = "Thank you for sharing. This excuse will not be saved because your future self probably does not care."
        return render_template('message.html', message=message)
    else:
        return render_template('add_excuse.html')

if __name__ == '__main__':
    app.run(debug=True)
