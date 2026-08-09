# Google Play Store Analytics Internship Project

## Objective
The objective of this project is to analyze the Google Play Store dataset to extract meaningful insights about app performance, user reviews, and category trends. The project involves creating interactive data visualizations and a unified dashboard using Power BI and Python (Dash/Plotly) to help stakeholders understand market dynamics and app success factors.

## Tools Used
- **Python 3.12+**
- **Dash & Plotly** (for interactive web visualizations)
- **Pandas** (for data cleaning and processing)
- **Power BI** (for exploratory data analysis and dashboarding)

## Dataset Names
1. **Play Store Data.csv**: Contains metadata for over 10,000 apps (category, rating, installs, size, price, etc.).
2. **User Reviews.csv**: Contains user reviews with sentiment polarity and subjectivity scores.
3. **Global EV Data 2024.csv**: Additional dataset (kept for reference per project requirements).

## Tasks Overview

### Task 1: Power BI Visualization / Dashboard
- **Description**: An exploratory dashboard built in Power BI to analyze app categories, ratings, and installs.
- **Location**: `task1_powerbi/intership task1.pbix`

### Task 2: Choropleth Map
- **Description**: A global map visualization showing total installs by category using representative countries.
- **Time Restriction**: Available only between 6:00 PM and 8:00 PM IST.

### Task 3: Dual-Axis Chart
- **Description**: A dual-axis chart comparing average installs and revenue for Free vs. Paid apps across the top 3 categories.
- **Time Restriction**: Available only between 1:00 PM and 2:00 PM IST.

### Task 4: Time-Series Line Chart
- **Description**: A line chart showing monthly install trends for specific categories, highlighting months with >20% growth.
- **Time Restriction**: Available only between 6:00 PM and 9:00 PM IST.

### Task 5: Bubble Chart
- **Description**: An interactive bubble chart mapping App Size vs. Average Rating, with bubble size representing total installs.
- **Time Restriction**: Available only between 5:00 PM and 7:00 PM IST.

### Task 6: Stacked Area Chart
- **Description**: A stacked area chart displaying cumulative installs over time for specific categories, with varying opacity based on growth intensity.
- **Time Restriction**: Available only between 4:00 PM and 6:00 PM IST.

## Final Project Structure

```text
Internship_Project/
├── data/
│   ├── Play Store Data.csv
│   ├── User Reviews.csv
│   └── Global EV Data 2024.csv
├── task1_powerbi/
│   └── intership task1.pbix
├── task2/
│   ├── task2.py
│   └── Task2_Documentation.md
├── task3/
│   ├── task3.py
│   └── TASK_3_DOCUMENTATION.md
├── task4/
│   ├── task4.py
│   └── TASK_4_DOCUMENTATION.md
├── task5/
│   ├── task5.py
│   └── Task5_Documentation.md
├── task6/
│   ├── task6.py
│   └── Task6_Documentation.md
├── app.py
├── dashboard.py
├── requirements.txt
├── IMPLEMENTATION_SUMMARY.md
└── README.md
```

## Required Python Packages
To run the python tasks and the dashboard, install the dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

*Key packages:* `dash>=2.18.0`, `pandas>=2.2.0`, `plotly>=5.24.0`, `gunicorn>=22.0.0`

## How to Run the Python Tasks
The project features a unified dashboard that integrates Tasks 2 through 6. 

To launch the dashboard, run:
```bash
python app.py
```
Then, open your web browser and go to `http://localhost:8050/`. 

*Note: Visualizations will only display their respective charts if the current time in the IST (Asia/Kolkata) timezone falls within their specified availability windows. Outside of these hours, a notice will be displayed instead.*
