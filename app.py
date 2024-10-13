from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime, timedelta

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
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
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
    today = datetime.now().strftime('%Y-%m-%d')
    data = load_data()

    if today not in data:
        message = "No tasks for today."
        return render_template('message.html', message=message)

    if request.method == 'POST':
        completed_tasks = request.form.getlist('completed')
        for task in data[today]['tasks']:
            if task['description'] in completed_tasks:
                task['completed'] = True
        save_data(data)
        return redirect(url_for('home'))
    else:
        tasks = data[today]['tasks']
        return render_template('today_tasks.html', tasks=tasks)


def generate_heatmap():
    from calendar import monthrange
    import numpy as np
    import matplotlib.colors as mcolors

    data = load_data()
    dates = []
    completion_rates = []

    for date_str, details in data.items():
        date = pd.to_datetime(date_str)
        total_tasks = len(details['tasks'])
        completed_tasks = sum(1 for task in details['tasks'] if task['completed'])
        completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        dates.append(date)
        completion_rates.append(completion_rate)

    today = datetime.now()
    start_date = datetime(today.year, today.month, 1)
    # Get the last day of the current month
    last_day = monthrange(today.year, today.month)[1]
    end_date = datetime(today.year, today.month, last_day)

    # Create a date range for the current month
    dates_all = pd.date_range(start=start_date, end=end_date)
    # Initialize completion rates for all dates in the month
    completion_dict = {date: 0 for date in dates_all}
    # Update completion rates with actual data
    for date, rate in zip(dates, completion_rates):
        completion_dict[date] = rate

    dates = list(completion_dict.keys())
    completion_rates = list(completion_dict.values())

    # Create a custom colormap
    cmap = plt.get_cmap('YlGn')
    cmap_colors = cmap(np.arange(cmap.N))

    # Set the first color (representing zero completion) to light grey
    light_grey_rgba = np.array([0.9, 0.9, 0.9, 1.0])  # RGBA for light grey
    cmap_colors[0] = light_grey_rgba
    new_cmap = mcolors.ListedColormap(cmap_colors)

    # Generate the heatmap using July
    plt.figure(figsize=(8, 2))
    ax = plt.gca()

    july.heatmap(
        dates,
        completion_rates,
        cmap=new_cmap,
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
    today = datetime.now().strftime('%Y-%m-%d')
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
        message = "Thank you for sharing. Everyday can't be perfect, do your best tomorrow!"
        return render_template('message.html', message=message)
    else:
        return render_template('add_excuse.html')


if __name__ == '__main__':
    app.run(debug=True)
