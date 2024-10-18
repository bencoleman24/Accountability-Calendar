## Accountability Calendar

I wanted to build a tool to help hold myself accountable and become more productive.

How it works:
- Add tasks for the next day and their respective priority level (1-5). The task list cannot be changed once the next day starts. 
- Check off tasks as you do them.
- The next day the square indicating the day on the calendar will turn a shade of green depending on how productive you were. The darker green the better. 
- If you forget to add tasks for the next day, too bad. The square will be grey for that day.

I built it this way to keep myself focused on planning ahead and staying consistent, without letting myself make changes or excuses once the day starts. Speaking of excuses, there is an area on the website where you can add an excuse. The excuses are not saved because your future self probably does not care.

If you are interested in running this on your machine, here are the steps:

### 1. Clone the Repository
Clone the repository to your local machine:

```bash
git clone https://github.com/bencoleman24/Accountability-Calendar.git
cd Accountability-Calendar
```

### 2. Create and Activate a Virtual Environment
Create a virtual environment to keep dependencies organized:

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Run the Flask App
After installing the dependencies, run the Flask app with:
```bash
python app.py
```
This will start the app, and you can access it in your browser at:
http://127.0.0.1:5000/


In the future I may develop this into a externally hosted website or app. But, I'm not sure if that is worth it. There are probably enough to-do apps lol. 