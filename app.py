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
fig_util = go.Figure()
fig_util.add_trace(go.Scatter(
    x=utilization_df['Date'],
    y=utilization_df['Utilization'],
    mode='lines+markers+text',
    text=[f"{val:.1f}" for val in utilization_df['Utilization']],
    textposition='top center',
    name='Utilization'
))
fig_util.update_layout(title='Utilization Over Time')
st.plotly_chart(fig_util)

# Downtime Chart and Pie Chart
st.subheader("Downtime Over Time and Reason Distribution")
downtime_df = filtered_df.groupby('Date')['Downtime'].mean().reset_index()
fig_downtime = go.Figure()
fig_downtime.add_trace(go.Scatter(
    x=downtime_df['Date'],
    y=downtime_df['Downtime'],
    mode='lines+markers+text',
    text=[f"{val:.1f}" for val in downtime_df['Downtime']],
    textposition='top center',
    name='Downtime'
))
fig_downtime.update_layout(title='Downtime Over Time')

reason_cols = ['RM Shortage', 'Machine Idle', 'Breakages', 'Electrical', 'Mechanical', 'Others']
reason_df = filtered_df[reason_cols].sum().reset_index()
reason_df.columns = ['Reason', 'Duration']
fig_pie = px.pie(reason_df, names='Reason', values='Duration', title='Downtime Reason Distribution', hole=0.3)
fig_pie.update_traces(textposition='inside', textinfo='percent+label', texttemplate='%{label}: %{percent:.1%}')

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_downtime)
with col2:
    st.plotly_chart(fig_pie)

# Downgrade Chart
st.subheader("Downgrade Percentages Over Time")
downgrade_df = filtered_df.groupby('Date')[['RM Downgrade %', 'Quality Downgrade %', 'Packing Downgrade %']].mean().reset_index()
fig_downgrade = px.bar(downgrade_df, x='Date',
                       y=['RM Downgrade %', 'Quality Downgrade %', 'Packing Downgrade %'],
                       title='Downgrade Percentages Over Time',
                       text_auto='.1f')
fig_downgrade.update_traces(texttemplate='%{value:.1f}', textposition='outside')
st.plotly_chart(fig_downgrade)

# Energy Intensity Chart
st.subheader("Energy Intensity KWH/KG")
energy_df = filtered_df.groupby('Date')[['Machine Energy %', 'Utility Energy %', 'Other Energy %']].mean().reset_index()
fig_energy = go.Figure()
for col in ['Machine Energy %', 'Utility Energy %', 'Other Energy %']:
    fig_energy.add_trace(go.Scatter(
        x=energy_df['Date'],
        y=energy_df[col],
        mode='lines+markers+text',
        text=[f"{val:.1f}" for val in energy_df[col]],
        textposition='top center',
        name=col
    ))
fig_energy.update_layout(title='Energy Intensity Over Time')
st.plotly_chart(fig_energy)
