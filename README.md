# 🩺 Diabetes Tracker — GUI Version

A desktop application for tracking and analyzing diabetes-related health data, built with Python and Tkinter.
This is the upgraded version of the [CLI-based Diabetes Tracker](https://github.com/babovcristina/diabetes-tracker-python).

---

## Technologies Used

- Python 3
- Tkinter (desktop GUI)
- SQLite (local database)
- CSV (data export)

---

## Features

### 🔐 User Authentication
- Register and log in with a username and password
- Passwords stored securely using SHA-256 hashing
- Each user sees only their own data

### 📋 Measurements (Daily Tracking)
- Add daily measurements: glucose, water intake, steps, carbs
- View all records in a table with automatic status (Normal / Hypoglycemia / Hyperglycemia)
- Modify and delete existing entries

### 🧪 HbA1c (Every 3 Months)
- Add HbA1c values with automatic classification:
  - Normal / Prediabetes / Good control / Consult your doctor
- View history, modify and delete records

### ⚖️ Weight (Monthly Tracking)
- Add weight records
- View history with difference compared to previous entry
- Modify and delete records

### 📊 Analysis & Insights
- **Glucose statistics** — average, minimum, maximum
- **Time-in-range** — percentage of readings in normal, low, and high range
- **HbA1c trend** — comparison of last 5 values with improvement/worsening indicator
- **Weight trend** — comparison of last 5 values
- **Correlation analysis** — Pearson correlation between glucose and carbs, steps, water intake

### 📄 Export to CSV
- Export measurements, HbA1c, and weight data to separate CSV files
- Files saved in the current working directory with a timestamp in the filename

---

## How It Works

### Data Storage
All data is stored locally using SQLite in four tables:
- `users` — stores usernames and hashed passwords
- `measurements` — daily glucose, water, steps, carbs (linked to user)
- `hba1c` — HbA1c values (linked to user)
- `weight` — weight records (linked to user)

### Glucose Status Classification
| Range | Status |
|---|---|
| Below 70 mg/dL | Hypoglycemia |
| 70 – 130 mg/dL | Normal |
| Above 130 mg/dL | Hyperglycemia |

### HbA1c Classification
| Value | Status |
|---|---|
| ≤ 5.6% | Normal |
| 5.7 – 6.4% | Prediabetes |
| 6.5 – 7.0% | Good control |
| Above 7.0% | Consult your doctor |

### Correlation Analysis
Uses the Pearson correlation coefficient (r) to measure relationships between glucose and lifestyle factors:
- r > 0.6 → Strong positive correlation
- r between 0.3 and 0.6 → Moderate positive correlation
- r < -0.3 → Negative correlation (e.g. more steps = lower glucose)

---

## How to Run

1. Make sure Python 3 is installed
2. No additional libraries needed — Tkinter and SQLite are included with Python
3. Run the script:

```bash
python diabetes_tracker_gui.py
```

4. Register a new account or log in
5. Navigate using the sidebar

---

## Project Structure

```
diabetes-tracker-gui/
│
├── diabetes_tracker.py   # Original CLI version
├── diabetes_tracker_gui.py   # GUI version (Tkinter)
├── diabetes_tracker.db       # SQLite database (created on first run)
└── README.md
```

---

## What I Learned

- Building desktop GUIs with Tkinter (windows, frames, widgets, layout)
- Implementing user authentication with password hashing
- Structuring a larger Python project across multiple classes
- Pearson correlation calculation without external libraries
- Exporting structured data to CSV
- Improving an existing project with new features

