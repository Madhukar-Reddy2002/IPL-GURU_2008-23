import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def display(df):
    """Display the dashboard"""
    selected_team = st.sidebar.selectbox("Select a Team", df['batting_team'].unique(), key="team_selection")
    # Filter data by selected team
    filtered_data = df[(df['batting_team'] == selected_team) | (df['bowling_team'] == selected_team)].copy()
    num_matches = len(filtered_data["match_id"].unique())
    team_scores = filtered_data.groupby(['start_date', 'batting_team', 'bowling_team'])[['runs_off_bat', 'extras']].sum().reset_index()
    highest_team_score = team_scores.loc[team_scores['runs_off_bat'].idxmax()]

    st.metric("Highest Team Score", f"{highest_team_score['runs_off_bat'] + highest_team_score['extras']} runs", f" vs {highest_team_score['bowling_team']} on {highest_team_score['start_date']}")
    st.metric("Number of Matches", num_matches)
    
    # Group final match data by year
    final_match_by_year = df.groupby(df['start_date'].dt.year).first()
    cups = (final_match_by_year["winner"] == selected_team).sum()
    runners = (final_match_by_year["team2"] == selected_team).sum()
    runners += (final_match_by_year["team1"] == selected_team).sum()
    runners -= cups
    if cups > 0:
        st.write('**Cups Won: {}**'.format(cups))
    if runners > 0:
        st.write('**Runners : {}**'.format(runners))

    # Function to determine losers based on selected team
    def determine_losers(row):
        if row['team1'] == row['winner']:
            return row['team2']
        else:
            return row['team1']

    # Display table showing match ID, winner, and losers columns grouped by match ID
    match_winner_table = df.groupby('match_id')[['winner', 'team1', 'team2']].first().reset_index()
    match_winner_table['losers'] = match_winner_table.apply(determine_losers, axis=1)

    # Divide the table based on whether the selected team is in the winners or losers column
    winners_df = match_winner_table[match_winner_table['winner'] == selected_team]
    losers_df = match_winner_table[match_winner_table['losers'] == selected_team]

    # Count occurrences where winner is equal to selected team
    winner_counts = winners_df.shape[0]
    st.write(f"Winning Percentage: {(winner_counts/num_matches)*100:.2f} %")

    # Counter for number of times each team occurs in the winning table
    winning_teams_counter = winners_df.groupby('losers').size().reset_index(name='count')
    losing_teams_counter = losers_df.groupby('winner').size().reset_index(name='count')

    # Merge the two tables based on team names
    merged_table = pd.merge(winning_teams_counter, losing_teams_counter, left_on='losers', right_on='winner', how='outer')
    merged_table = merged_table.fillna(0)  # Fill NaN values with 0
    merged_table['total_count'] = merged_table['count_x'] + merged_table['count_y']
    merged_table = merged_table.rename(columns={'count_x': 'wins_as_loser', 'count_y': 'losses_as_winner', 'losers': 'opponent_team'})

    # Calculate winning percentage against each team
    merged_table['winning_percentage'] = (merged_table['wins_as_loser'] / (merged_table['wins_as_loser'] + merged_table['losses_as_winner'])) * 100
    team_scores = filtered_data.groupby(filtered_data['start_date'].dt.year)['runs_off_bat'].sum().reset_index()
    st.area_chart(team_scores.set_index('start_date'))

    """Display the year-wise performance for the selected team"""
    batting_filtered_data = df[df['batting_team'] == selected_team].copy()
    batting_filtered_data['day_of_year'] = batting_filtered_data['start_date'].dt.dayofyear

    daily_scores = batting_filtered_data.groupby([batting_filtered_data['start_date'].dt.year, 'day_of_year'])[['runs_off_bat', 'extras']].sum().reset_index()
    daily_scores['total_score'] = daily_scores['runs_off_bat'] + daily_scores['extras']
    max_scores_per_year = daily_scores.groupby(daily_scores['start_date']).agg({'total_score': 'max'}).reset_index()

    st.subheader(f"Yearly Highest Scores for {selected_team}")
    st.line_chart(max_scores_per_year.set_index('start_date'))

    # Create separate pie charts for each opponent team
    for index, row in merged_table.iterrows():
        opponent_team = row['opponent_team']
        total_matches = row['total_count']
        wins = row['wins_as_loser']
        losses = row['losses_as_winner']

        # Create data for pie chart
        labels = ['Wins', 'Losses']
        sizes = [wins, losses]
        colors = ['green', 'orange']

        # Plot pie chart
        fig, ax = plt.subplots(figsize=(3, 3))
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax.set_title(f'{selected_team} vs {opponent_team} ({total_matches} matches)')
        st.pyplot(fig) 