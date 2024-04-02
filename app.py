import streamlit as st
import pandas as pd
import plotly.express as px

# Read your data into a DataFrame
df = pd.read_csv('./new.csv', low_memory=False)

# Convert 'date' column to datetime type
df['date'] = pd.to_datetime(df['date'])

# Streamlit app
st.title("Cricket Dashboard")

# Get unique years from the data
years = df['date'].dt.year.unique()

# Allow the user to select the year
selected_year = st.selectbox("Select Year", years)

# Filter the data based on the selected year
filtered_data = df[df['date'].dt.year == selected_year]

# Calculate total runs
filtered_data['total_runs'] = filtered_data['runs_off_bat']

# Count the number of matches
num_matches = len(filtered_data["match_id"].unique())

# Group data by 'batting_team' and 'striker' and calculate total runs for each combination
striker_runs = filtered_data.groupby(['batting_team', 'striker']).agg(
    total_runs=('total_runs', 'sum'),
    fours=('runs_off_bat', lambda x: (x == 4).sum()),
    sixes=('runs_off_bat', lambda x: (x == 6).sum()),
    num_times_striker=('striker', 'count')  # New column to count the number of times the player has been the striker
).reset_index()

# Find the player with the highest runs
max_runs_player = striker_runs.loc[striker_runs['total_runs'].idxmax()]

# Streamlit layout
col1, col2 = st.columns(2)

with col1:
    # Create a stacked bar chart for total runs by team and striker
    fig = px.bar(striker_runs, x='batting_team', y='total_runs', color='striker', title='Total Runs by Team and Striker', barmode='stack')

    # Update layout
    fig.update_layout(xaxis_title='Batting Team', yaxis_title='Total Runs', legend_title='Striker')

    # Highlight player with highest runs
    fig.add_annotation(x=max_runs_player['batting_team'], y=max_runs_player['total_runs'], text=f"<b>{max_runs_player['striker']}</b><br>{max_runs_player['total_runs']} runs", showarrow=True, arrowhead=7, ax=0, ay=-40, bgcolor='orange', font=dict(color='black', size=14))

    # Plot the chart
    st.plotly_chart(fig)

with col2:
    # Display player with highest runs, total runs, number of innings, and number of times as striker
    st.write(f"<b>Orange Cap Holder:</b> {max_runs_player['striker']}", unsafe_allow_html=True)
    st.write(f"Total runs: {max_runs_player['total_runs']}")
    st.write(f"Number of matches played in {selected_year}: {num_matches}")
    st.write(f"Number of times as striker: {max_runs_player['num_times_striker']}")

# Create a DataFrame to hold bowler-wise wicket counts
bowler_wickets = filtered_data[(filtered_data['wicket_type'].notna()) & (filtered_data['wicket_type'] != "run out")].groupby(['bowling_team', 'bowler'])['wicket_type'].count().reset_index()

# Rename the columns
bowler_wickets.columns = ['Bowling Team', 'Bowler', 'Wickets']

# Find the bowler with the highest wickets
max_wickets_bowler = bowler_wickets.loc[bowler_wickets['Wickets'].idxmax()]

# Streamlit layout
col3, col4 = st.columns(2)

with col3:
    # Create a stacked bar chart for wickets taken by each bowler
    fig_bowlers = px.bar(bowler_wickets, x='Bowling Team', y='Wickets', color='Bowler', title='Wickets Taken by Bowler and Bowling Team', barmode='stack')

    # Highlight bowler with highest wickets as Purple Cap Holder
    fig_bowlers.add_annotation(x=max_wickets_bowler['Bowling Team'], y=max_wickets_bowler['Wickets'], text=f"<b>{max_wickets_bowler['Bowler']}</b><br>{max_wickets_bowler['Wickets']} wickets", showarrow=True, arrowhead=7, ax=0, ay=-40, bgcolor='purple', font=dict(color='white', size=14))

    # Plot the chart for bowlers
    st.plotly_chart(fig_bowlers)

with col4:
    # Display the purple cap holder and his total wickets
    st.write(f"<b>Purple Cap Holder:</b> {max_wickets_bowler['Bowler']}", unsafe_allow_html=True)
    st.write(f"Total wickets: {max_wickets_bowler['Wickets']}")

# Group data by 'date' year and 'striker', and sum the 'total_runs'
top_scorers = filtered_data.groupby([filtered_data['date'].dt.year, 'striker']).agg(
    total_runs=('total_runs', 'sum'),
    fours=('runs_off_bat', lambda x: (x == 4).sum()),
    sixes=('runs_off_bat', lambda x: (x == 6).sum()),
).reset_index()
top_scorers.columns = ['Year', 'Player', 'Total Runs', 'Fours', 'Sixes']

# Sort the data by year and total runs in descending order
top_scorers = top_scorers.sort_values(['Year', 'Total Runs'], ascending=[True, False])

# Create a new column 'rank' to assign ranks within each year
top_scorers['Rank'] = top_scorers.groupby('Year')['Total Runs'].rank(method='dense', ascending=False)

# Filter the top 10 players for each year
top_scorers = top_scorers[top_scorers['Rank'] <= 10]

# Display the table for top scorers
st.write('Top 10 Players by Runs Scored in Each Year')
st.table(top_scorers)

# Find players who scored more than 100 runs in a single match_id
high_scorers = filtered_data.groupby(['match_id', 'striker']).total_runs.sum().reset_index()
centuries = high_scorers[high_scorers.total_runs > 100]

# Sort the centuries DataFrame by total_runs in descending order
if not centuries.empty:
    centuries = centuries.sort_values(by='total_runs', ascending=False)

    # Add a 'Rank' column based on total_runs
    centuries['Rank'] = range(1, len(centuries) + 1)

    st.write('Players Who Scored More Than 100 Runs in a Single Match')
    st.table(centuries)
else:
    st.write('No players scored more than 100 runs in a single match.')

# Find the highest score in a single match by a single player
highest_score = filtered_data.groupby(['match_id', 'striker']).total_runs.sum().reset_index()
max_score = highest_score.total_runs.max()

# Find the player with the highest score
max_score_player = highest_score[highest_score['total_runs'] == max_score].iloc[0]

# Display the player with the highest score
st.write(f"Player with the highest score in a single match: {max_score_player['striker']}, Runs: {max_score_player['total_runs']}")

# Create a histogram for the distribution of runs scored by all players
fig_hist = px.histogram(filtered_data, x='total_runs', nbins=20, title='Distribution of Runs Scored by All Players')
st.plotly_chart(fig_hist)
