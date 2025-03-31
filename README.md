# SF Crime Data Analysis

A data-driven story exploring crime patterns in San Francisco from 2003 to 2015.

## Project Overview
This project analyzes crime data from the San Francisco Police Department to identify patterns in:
- Temporal distribution of crimes
- Geographic hotspots
- Crime category distributions

## Technologies Used
- Jekyll for web presentation
- Python for data analysis
- Matplotlib, Folium, and Bokeh for visualizations

## Local Development
To run this site locally:

1. Install Ruby and Jekyll
```bash
gem install bundler jekyll
```

2. Install dependencies
```bash
bundle install
```

3. Start the Jekyll server
```bash
bundle exec jekyll serve
```

4. View the site at http://localhost:4000

## Data Analysis
The Python scripts for data analysis are in the `scripts` directory. To run them:

1. Install Python requirements
```bash
pip install -r requirements.txt
```

2. Run the analysis script
```bash
python scripts/analyze_crime_data.py
```

## View the Site
The deployed site is available at [https://charlesdark.github.io/](https://charlesdark.github.io/)