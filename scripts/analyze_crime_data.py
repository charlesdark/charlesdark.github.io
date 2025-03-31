import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, HoverTool, LabelSet
from bokeh.layouts import column
import numpy as np
import os
from datetime import datetime

# Set style for all plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def clean_coordinates(df):
    """Clean coordinate data by removing invalid values."""
    # Remove rows with NaN coordinates
    df = df.dropna(subset=['Latitude', 'Longitude'])
    
    # Remove rows with invalid coordinates (outside San Francisco bounds)
    # San Francisco coordinates are approximately:
    # Latitude: 37.7 to 37.8
    # Longitude: -122.5 to -122.4
    df = df[
        (df['Latitude'].between(37.7, 37.8)) &
        (df['Longitude'].between(-122.5, -122.4))
    ]
    
    return df

def load_data():
    """Load and validate the crime data."""
    try:
        # Try multiple potential paths to find the data file
        potential_paths = ["data/crime_data_cleaned.csv", "../data/crime_data_cleaned.csv", "./data/crime_data_cleaned.csv"]
        
        df = None
        for path in potential_paths:
            try:
                if os.path.exists(path):
                    print(f"Found data file at {path}")
                    df = pd.read_csv(path)
                    break
            except:
                continue
        
        if df is None:
            raise FileNotFoundError("Could not find crime_data_cleaned.csv in any of the expected locations")
            
        # Convert date column to datetime
        df['Incident Date'] = pd.to_datetime(df['Incident Date'])
        # Validate required columns
        required_columns = ['Incident Date', 'Latitude', 'Longitude', 'Incident Category']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Clean coordinate data
        df = clean_coordinates(df)
        print(f"Loaded {len(df)} valid records after cleaning coordinates")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        raise

# 1. Time Series Analysis
def create_time_series(df):
    """Create time series visualization of crime incidents."""
    try:
        # Group by date and count incidents
        daily_crimes = df.groupby('Incident Date').size().reset_index(name='count')
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.plot(daily_crimes['Incident Date'], daily_crimes['count'], linewidth=2)
        plt.title('Daily Crime Incidents in San Francisco', fontsize=14)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Number of Incidents', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        # Add trend line
        z = np.polyfit(range(len(daily_crimes)), daily_crimes['count'], 1)
        p = np.poly1d(z)
        plt.plot(daily_crimes['Incident Date'], p(range(len(daily_crimes))), "r--", alpha=0.8)
        
        plt.tight_layout()
        plt.savefig('assets/images/time_series.png', dpi=300, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Error creating time series plot: {e}")
        raise

# 2. Map Visualization
def create_crime_map(df):
    """Create interactive map visualization of crime locations."""
    try:
        # Create a map centered on San Francisco
        m = folium.Map(location=[37.7749, -122.4194], zoom_start=12)
        
        # Take a smaller sample to make the map performant
        sample_size = min(500, len(df))  # Reduced from 1000 to 500 for better performance
        df_sample = df.sample(n=sample_size, random_state=42)
        
        # Track unique categories for legend
        unique_categories = df_sample['Incident Category'].unique()
        
        # Add markers for each crime location
        for idx, row in df_sample.iterrows():
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=3,
                color='red',
                fill=True,
                popup=f"Category: {row['Incident Category']}<br>Date: {row['Incident Date'].strftime('%Y-%m-%d')}",
                tooltip=row['Incident Category']
            ).add_to(m)
        
        # Add a legend
        legend_html = '''
        <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
            <h4>Crime Map - San Francisco</h4>
            <p>Red dots represent crime locations</p>
            <p>Click on dots for more information</p>
            <p>Sample of 500 incidents shown</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Save the map
        m.save('assets/images/crime_map.html')
    except Exception as e:
        print(f"Error creating crime map: {e}")
        raise

# 3. Interactive Bokeh Visualization
def create_interactive_viz(df):
    """Create interactive Bokeh visualization of crime categories."""
    try:
        # Count crimes by category and get top 10 for simplicity
        crime_counts = df['Incident Category'].value_counts().head(10)
        
        # Create lists for the data
        categories = list(crime_counts.index)
        counts = list(crime_counts.values)
        
        # Create a new figure
        p = figure(width=800, height=400, title="Top 10 Crime Categories in San Francisco")
        
        # Create the bar chart
        source = ColumnDataSource(data=dict(
            categories=categories,
            counts=counts,
            x=list(range(len(categories)))
        ))
        
        # Add bars
        bars = p.vbar(x='x', top='counts', width=0.8, source=source)
        
        # Add x-axis labels
        p.xaxis.ticker = list(range(len(categories)))
        p.xaxis.major_label_overrides = {i: cat for i, cat in enumerate(categories)}
        
        # Customize the plot
        p.title.text_font_size = '14pt'
        p.xaxis.axis_label = 'Crime Category'
        p.yaxis.axis_label = 'Number of Incidents'
        
        # Rotate x-axis labels
        p.xaxis.major_label_orientation = np.pi/4
        
        # Add hover tool
        hover = HoverTool(renderers=[bars])
        hover.tooltips = [
            ('Category', '@categories'),
            ('Count', '@counts')
        ]
        p.add_tools(hover)
        
        # Save the plot
        output_file('assets/images/interactive_viz.html')
        save(p)
    except Exception as e:
        print(f"Error creating interactive visualization: {e}")
        raise

def main():
    """Main function to run all visualizations."""
    try:
        # Create directories if they don't exist
        os.makedirs('assets/images', exist_ok=True)
        
        # Load data
        print("Loading data...")
        df = load_data()
        
        # Generate all visualizations
        print("Creating time series visualization...")
        create_time_series(df)
        
        print("Creating crime map...")
        create_crime_map(df)
        
        print("Creating interactive visualization...")
        create_interactive_viz(df)
        
        print("All visualizations created successfully!")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main() 