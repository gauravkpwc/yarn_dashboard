import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

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
            machine_energy = np.random.uniform(280, 320)
            utility_energy = np.random.uniform(400, 500)
            other_energy = np.random.uniform(100, 200)
            bpt = np.random.uniform(0.7, 1.3)
            even_percent = 91 - (bpt - 0.7) * 10

            data.append({
                'Date': date, 'Plant': plant, 'Machine': machine, 'Utilization': utilization,
                'Downtime': total_downtime, 'RM Shortage': downtime_distribution['RM Shortage'],
                'Machine Idle': downtime_distribution['Machine Idle'], 'Breakages': downtime_distribution['Breakages'],
                'Electrical': downtime_distribution['Electrical'], 'Mechanical': downtime_distribution['Mechanical'],
                'Others': downtime_distribution['Others'], 'RM Downgrade %': rm_downgrade,
                'Quality Downgrade %': quality_downgrade, 'Packing Downgrade %': packing_downgrade,
                'Total Downgrade %': total_downgrade, 'Machine Energy': machine_energy,
                'Utility Energy': utility_energy, 'Other Energy': other_energy,
                'BPT': bpt, 'Even %': even_percent
            })

df = pd.DataFrame(data)

# PwC color theme
colors = {
    'orange': '#F05A28',
    'grey': '#A7A9AC',
    'dark_grey': '#58595B',
    'light_grey': '#D1D3D4'
}

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

# Helper function to reduce label density to 25%
def sparse_labels(values, density=4):
    return [f"{val:.1f}" if i % density == 0 else "" for i, val in enumerate(values)]

# Utilization Chart
st.subheader("Utilization Over Time")
utilization_df = filtered_df.groupby('Date')['Utilization'].mean().reset_index()
fig_util = go.Figure()
fig_util.add_trace(go.Scatter(
    x=utilization_df['Date'],
    y=utilization_df['Utilization'],
    mode='lines+markers+text',
    text=sparse_labels(utilization_df['Utilization']),
    textposition='top center',
    name='Utilization',
    line=dict(color=colors['orange'])
))
fig_util.update_layout(title='Utilization Over Time')
st.plotly_chart(fig_util)

# Downtime Chart and Pie Chart
st.subheader("Downtime Over Time and Reason Distribution")
st.caption("Downtime Over Time – % | Reason Distribution – m/c Hrs")

downtime_df = filtered_df.groupby('Date')['Downtime'].mean().reset_index()
fig_downtime = go.Figure()
fig_downtime.add_trace(go.Scatter(
    x=downtime_df['Date'],
    y=downtime_df['Downtime'],
    mode='lines+markers+text',
    text=sparse_labels(downtime_df['Downtime']),
    textposition='top center',
    name='Downtime',
    line=dict(color=colors['dark_grey'])
))
fig_downtime.update_layout(title='Downtime Over Time')

reason_cols = ['RM Shortage', 'Machine Idle', 'Breakages', 'Electrical', 'Mechanical', 'Others']
reason_df = filtered_df[reason_cols].sum().reset_index()
reason_df.columns = ['Reason', 'Duration']
fig_pie = px.pie(reason_df, names='Reason', values='Duration', title='Downtime Reason Distribution', hole=0.3,
                 color_discrete_sequence=[colors['orange'], colors['grey'], colors['dark_grey'], colors['light_grey'], '#CCCCCC', '#999999'])
fig_pie.update_traces(textposition='inside', textinfo='value', texttemplate='%{value:.1f}')

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_downtime)
with col2:
    st.plotly_chart(fig_pie)

# Downgrade Chart as stacked area chart
st.subheader("Downgrade Percentages Over Time")
downgrade_df = filtered_df.groupby('Date')[['RM Downgrade %', 'Quality Downgrade %', 'Packing Downgrade %']].mean().reset_index()
fig_area = go.Figure()
fig_area.add_trace(go.Scatter(
    x=downgrade_df['Date'], y=downgrade_df['RM Downgrade %'], stackgroup='one',
    name='RM Downgrade %', line=dict(color=colors['orange']),
    text=sparse_labels(downgrade_df['RM Downgrade %']),
    mode='lines+text', textposition='top center'
))
fig_area.add_trace(go.Scatter(
    x=downgrade_df['Date'], y=downgrade_df['Quality Downgrade %'], stackgroup='one',
    name='Quality Downgrade %', line=dict(color=colors['grey']),
    text=sparse_labels(downgrade_df['Quality Downgrade %']),
    mode='lines+text', textposition='top center'
))
fig_area.add_trace(go.Scatter(
    x=downgrade_df['Date'], y=downgrade_df['Packing Downgrade %'], stackgroup='one',
    name='Packing Downgrade %', line=dict(color=colors['dark_grey']),
    text=sparse_labels(downgrade_df['Packing Downgrade %']),
    mode='lines+text', textposition='top center'
))
fig_area.update_layout(title='Downgrade Percentages Over Time')
st.plotly_chart(fig_area)

# Energy Intensity Chart as ribbon chart with absolute values and 25% label density
st.subheader("Energy Intensity KWH/KG")
energy_df = filtered_df.groupby('Date')[['Machine Energy', 'Utility Energy', 'Other Energy']].mean().reset_index()
fig_ribbon = go.Figure()
fig_ribbon.add_trace(go.Scatter(
    x=energy_df['Date'], y=energy_df['Machine Energy'], name='Machine Energy',
    line=dict(color=colors['orange']), mode='lines+markers+text', stackgroup='energy',
    text=sparse_labels(energy_df['Machine Energy']),
    textposition='top center'
))
fig_ribbon.add_trace(go.Scatter(
    x=energy_df['Date'], y=energy_df['Utility Energy'], name='Utility Energy',
    line=dict(color=colors['grey']), mode='lines+markers+text', stackgroup='energy',
    text=sparse_labels(energy_df['Utility Energy']),
    textposition='top center'
))
fig_ribbon.add_trace(go.Scatter(
    x=energy_df['Date'], y=energy_df['Other Energy'], name='Other Energy',
    line=dict(color=colors['dark_grey']), mode='lines+markers+text', stackgroup='energy',
    text=sparse_labels(energy_df['Other Energy']),
    textposition='top center'
))
fig_ribbon.update_layout(title='Energy Intensity Over Time (KWH/KG)')
st.plotly_chart(fig_ribbon)
