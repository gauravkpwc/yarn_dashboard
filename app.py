import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set the title of the Streamlit app
st.title("Data Twin/Analytics in Yarn Industry Operations")

# Generate sample data
dates = pd.date_range(start="2023-01-01", periods=30, freq='D')
plants = ['Plant A', 'Plant B']
machines = ['Machine 1', 'Machine 2', 'Machine 3']
reason_codes = ['RM Shortage', 'Machine Idle', 'Breakages', 'Electrical', 'Mechanical', 'Others']

np.random.seed(42)
data = []

for date in dates:
    for plant in plants:
        for machine in machines:
            utilization = np.random.uniform(80, 92)
            total_downtime = 100 - utilization
            downtime_distribution = {
                'Breakages': total_downtime * 0.4,
                'RM Shortage': total_downtime * 0.25,
                'Mechanical': total_downtime * 0.15,
                'Electrical': total_downtime * 0.1,
                'Machine Idle': total_downtime * 0.05,
                'Others': total_downtime * 0.05
            }
            rm_downgrade = np.random.uniform(1, 3)
            quality_downgrade = np.random.uniform(2, 4)
            packing_downgrade = np.random.uniform(1, 2)
            total_downgrade = rm_downgrade + quality_downgrade + packing_downgrade
            machine_energy = np.random.uniform(28, 32)
            utility_energy = np.random.uniform(40, 50)
            other_energy = 100 - (machine_energy + utility_energy)
            bpt = np.random.uniform(0.7, 1.3)
            even_percent = 91 - (bpt - 0.7) * 10

            data.append({
                'Date': date, 'Plant': plant, 'Machine': machine, 'Utilization': utilization,
                'Downtime': total_downtime, 'RM Shortage': downtime_distribution['RM Shortage'],
                'Machine Idle': downtime_distribution['Machine Idle'], 'Breakages': downtime_distribution['Breakages'],
                'Electrical': downtime_distribution['Electrical'], 'Mechanical': downtime_distribution['Mechanical'],
                'Others': downtime_distribution['Others'], 'RM Downgrade %': rm_downgrade,
                'Quality Downgrade %': quality_downgrade, 'Packing Downgrade %': packing_downgrade,
                'Total Downgrade %': total_downgrade, 'Machine Energy %': machine_energy,
                'Utility Energy %': utility_energy, 'Other Energy %': other_energy,
                'BPT': bpt, 'Even %': even_percent
            })

df = pd.DataFrame(data)

# Sidebar filters
st.sidebar.header("Filters")
selected_plant = st.sidebar.selectbox("Select Plant", options=['All'] + plants)
selected_machine = st.sidebar.selectbox("Select Machine", options=['All'] + machines)
selected_reason = st.sidebar.selectbox("Select Reason Code", options=['All'] + reason_codes)

# Apply filters
filtered_df = df.copy()
if selected_plant != 'All':
    filtered_df = filtered_df[filtered_df['Plant'] == selected_plant]
if selected_machine != 'All':
    filtered_df = filtered_df[filtered_df['Machine'] == selected_machine]

# Utilization Chart
st.subheader("Utilization Over Time")
utilization_df = filtered_df.groupby('Date')['Utilization'].mean().reset_index()
fig_util = px.line(utilization_df, x='Date', y='Utilization', title='Utilization Over Time')
st.plotly_chart(fig_util)

# Downtime Chart and Pie Chart
st.subheader("Downtime Over Time and Reason Distribution")
if selected_reason == 'All':
    downtime_df = filtered_df.groupby('Date')['Downtime'].mean().reset_index()
    reason_cols = ['RM Shortage', 'Machine Idle', 'Breakages', 'Electrical', 'Mechanical', 'Others']
    reason_df = filtered_df[reason_cols].sum().reset_index()
    reason_df.columns = ['Reason', 'Duration']
else:
    downtime_df = filtered_df.groupby('Date')[selected_reason].mean().reset_index()
    downtime_df.columns = ['Date', 'Downtime']
    reason_df = pd.DataFrame({ 'Reason': [selected_reason], 'Duration': [filtered_df[selected_reason].sum()] })

fig_downtime = px.line(downtime_df, x='Date', y='Downtime', title='Downtime Over Time')
fig_pie = px.pie(reason_df, names='Reason', values='Duration', title='Downtime Reason Distribution')

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_downtime)
with col2:
    st.plotly_chart(fig_pie)

# Downgrade Chart (Area Chart)
st.subheader("Downgrade Percentages Over Time")
downgrade_df = filtered_df.groupby('Date')[['RM Downgrade %', 'Quality Downgrade %', 'Packing Downgrade %']].mean().reset_index()
fig_downgrade = px.area(downgrade_df, x='Date', y=['RM Downgrade %', 'Quality Downgrade %', 'Packing Downgrade %'],
                        title='Downgrade Percentages Over Time')
st.plotly_chart(fig_downgrade)

# Energy Intensity Chart
st.subheader("Energy Intensity KWH/KG")
energy_df = filtered_df.groupby('Date')[['Machine Energy %', 'Utility Energy %', 'Other Energy %']].mean().reset_index()
fig_energy = px.line(energy_df, x='Date', y=['Machine Energy %', 'Utility Energy %', 'Other Energy %'],
                     title='Energy Intensity Over Time')
st.plotly_chart(fig_energy)

# BPT and Even% Combo Chart
st.subheader("BPT and Even% Over Time")
combo_df = filtered_df.groupby('Date')[['BPT', 'Even %']].mean().reset_index()
fig_combo = go.Figure()
fig_combo.add_trace(go.Scatter(x=combo_df['Date'], y=combo_df['Even %'], name='Even %', yaxis='y1'))
fig_combo.add_trace(go.Scatter(x=combo_df['Date'], y=combo_df['BPT'], name='BPT', yaxis='y2'))

fig_combo.update_layout(
    title='BPT and Even% Over Time',
    yaxis=dict(title='Even %', side='left'),
    yaxis2=dict(title='BPT', overlaying='y', side='right'),
    xaxis=dict(title='Date')
)
st.plotly_chart(fig_combo)
