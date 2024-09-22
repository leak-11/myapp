import pandas as pd
import plotly.express as px
import streamlit as st

# Step 1: Load and Prepare the Dataset
url = 'https://linked.aub.edu.lb/pkgcube/data/9a5d5d78f2f1e8bacbf858385cb6f5fa_20240905_122326.csv'
df = pd.read_csv(url)
df.dropna(subset=["PercentageofEducationlevelofresidents-highereducation"], inplace=True)

# Step 2: Create Streamlit Layout
st.title('Interactive Visualizations: Education Data in Lebanon')

# Introduction section
st.write("""
This application allows you to explore the relationship between illiteracy rates and dropout percentages, 
as well as university education levels across different governorates in Lebanon.
""")

# Section Header: Filter Controls
st.header("Explore the Data Using Filters")

st.write("""
Use the filters below to interact with the data and customize your visualizations. 

**NB:** 
- These filters will affect both the scatter and box plots.
- If you manually select governorates, it will override the automatic filtering by the sliders.
- Refresh the page if you want to start over with the default settings.
""")

# 1. Range Slider: Dropout Percentage
dropout_range = st.slider(
    'Select Dropout Percentage Range:',
    min_value=float(df['PercentageofSchooldropout'].min()),
    max_value=float(df['PercentageofSchooldropout'].max()),
    value=(float(df['PercentageofSchooldropout'].min()), float(df['PercentageofSchooldropout'].max()))
)

# 2. Slider for Illiteracy Percentage (keep this as requested)
illiteracy_range = st.slider(
    'Select Illiteracy Percentage Range:', 
    min_value=float(df['PercentageofEducationlevelofresidents-illeterate'].min()), 
    max_value=float(df['PercentageofEducationlevelofresidents-illeterate'].max()), 
    value=(
        float(df['PercentageofEducationlevelofresidents-illeterate'].min()), 
        float(df['PercentageofEducationlevelofresidents-illeterate'].max())
    )
)

# Filter data based on the selected dropout and illiteracy ranges
df_filtered = df[
    (df['PercentageofSchooldropout'] >= dropout_range[0]) & (df['PercentageofSchooldropout'] <= dropout_range[1]) &
    (df['PercentageofEducationlevelofresidents-illeterate'] >= illiteracy_range[0]) & 
    (df['PercentageofEducationlevelofresidents-illeterate'] <= illiteracy_range[1])
]

# New Feature: Checkbox to include/exclude governorates with above-average university education levels
avg_university_percentage = df['PercentageofEducationlevelofresidents-university'].mean()

include_above_avg_university = st.checkbox(
    'Include only governorates with above-average university education levels', value=False
)

if include_above_avg_university:
    df_filtered = df_filtered[
        df_filtered['PercentageofEducationlevelofresidents-university'] > avg_university_percentage
    ]

# Prepare the filtered data for scatter plot
df_scatter_filtered = df_filtered[['refArea', 'PercentageofEducationlevelofresidents-illeterate', 'PercentageofSchooldropout']]
df_grouped = df_scatter_filtered.groupby('refArea').mean().reset_index()

# Convert `refArea` for clarity
df_grouped['refArea'] = df_grouped['refArea'].astype(str)
df_grouped['refArea'] = df_grouped['refArea'].apply(lambda x: x.rsplit('/', 1)[-1] if pd.notna(x) and '/' in x else x)

# Section Header: Scatter Plot
st.header("Scatter Plot: Illiteracy vs Dropout Percentage")

# Interactive multi-select for governorates
selected_governorates = st.multiselect(
    "Select Governorates for Scatter Plot:",
    options=df_grouped['refArea'].unique(),
    default=df_grouped['refArea'].unique()
)

# Filter based on selected governorates
filtered_scatter_data = df_grouped[df_grouped['refArea'].isin(selected_governorates)]

# Scatter Plot: Illiterate Percentage vs. Dropout Percentage
fig_scatter = px.scatter(
    filtered_scatter_data,
    x='PercentageofEducationlevelofresidents-illeterate',
    y='PercentageofSchooldropout',
    color='refArea',
    title='Relation between Illiterate Percentage and Dropout Percentage',
    labels={
        'PercentageofEducationlevelofresidents-illeterate': 'Illiterate Percentage (%)',
        'PercentageofSchooldropout': 'Dropout Percentage (%)'
    },
    color_discrete_sequence=px.colors.qualitative.Plotly  
)

fig_scatter.update_layout(width=800, height=800)
st.plotly_chart(fig_scatter)

# Explanation of the Scatter Plot
st.markdown("""
**Explanation of Scatter Plot:**  
This scatter plot shows the relationship between illiteracy and dropout rates in different governorates.
You can filter the data using the controls above to compare regions and identify patterns between education levels and dropout rates.
""")

# Prepare data for box plot
df_box_filtered = df_filtered[['refArea', 'PercentageofEducationlevelofresidents-university']]
df_box_grouped = df_box_filtered.groupby('refArea').mean().reset_index()

df_box_grouped['refArea'] = df_box_grouped['refArea'].astype(str)
df_box_grouped['refArea'] = df_box_grouped['refArea'].apply(lambda x: x.rsplit('/', 1)[-1] if pd.notna(x) and '/' in x else x)

# Section Header: Box Plot
st.header("Box Plot: University Education Levels")

# Multi-select for box plot
selected_box_governorates = st.multiselect(
    "Select Governorates for Box Plot:",
    options=df_box_grouped['refArea'].unique(),
    default=df_box_grouped['refArea'].unique()
)

# Filter based on selected governorates for box plot
filtered_box_data = df_box_grouped[df_box_grouped['refArea'].isin(selected_box_governorates)]

# Box Plot: University Education Levels
fig_box = px.box(
    filtered_box_data,
    x='refArea',
    y='PercentageofEducationlevelofresidents-university',
    points="all",  # Display all data points within the box plot
    title="Distribution of University Education Levels Across Selected Governorates"
)

fig_box.update_layout(
    xaxis_title="Governorates", 
    yaxis_title="University Education Level (%)",
    width=800, 
    height=800
)
st.plotly_chart(fig_box)

# Explanation of the Box Plot
st.markdown("""
**Explanation of Box Plot:**  
This box plot illustrates the distribution of university education levels across different governorates. 
The box plot helps you see how university education varies in selected regions, and the points show all data points within the range.
""")
