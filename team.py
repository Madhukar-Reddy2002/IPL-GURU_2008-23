import streamlit as st
import pandas as pd
import plotly.express as px

def display(df):
    """Display the dashboard"""

    selected_team = st.sidebar.selectbox("Select a Team", df['batting_team'].unique(), key="team_selection")

    # Filter data by selected team
    filtered_data = df[(df['batting_team'] == selected_team) | (df['bowling_team'] == selected_team)].copy()

    def get_opponent_team(row):
        if row["team1"] == selected_team:
            return row["team2"]
        else:
            return row["team1"]

    filtered_data["opponent_team"] = df.apply(get_opponent_team, axis=1)

    def get_results(row):
        if row["winner"] == selected_team:
            return "won"
        elif row["winner"] == "Draw":
            return "drawn"
        else:
            return "lost"

    filtered_data["our_team_won"] = df.apply(get_results, axis=1)

    num_matches = len(filtered_data["start_date"].unique())

    team_scores = filtered_data.groupby(['start_date', 'batting_team', 'bowling_team'])[['runs_off_bat', 'extras']].sum().reset_index()
    highest_team_score = team_scores.loc[team_scores['runs_off_bat'].idxmax()]

    st.metric("Highest Team Score", f"{highest_team_score['runs_off_bat'] + highest_team_score['extras']} runs", f" vs {highest_team_score['bowling_team']} on {highest_team_score['start_date']}")
    st.metric("Number of Matches", num_matches)

    final_match_by_year = df.groupby(df['start_date'].dt.year).first()
    cups_info = final_match_by_year[final_match_by_year["winner"] == selected_team][["start_date"]]
    runnerup_years_info = final_match_by_year[(final_match_by_year["team1"] == selected_team) | (final_match_by_year["team2"] == selected_team)]
    runnerup_years_info = runnerup_years_info[runnerup_years_info["winner"] != selected_team][["start_date"]]

    cups = cups_info.shape[0]
    runners = runnerup_years_info.shape[0]

    if cups > 0:
        st.metric("Cups Won", cups)
        years_won = ', '.join(map(str, list(cups_info["start_date"].dt.year)))
        st.metric("Years Won", years_won)

    if runners > 0:
        st.metric("Runners-up", runners)
        years_runnerup = ', '.join(map(str, list(runnerup_years_info["start_date"].dt.year)))
        st.metric("Years Runner-up", years_runnerup)

    team_scores = filtered_data.groupby(filtered_data['start_date'].dt.year)['runs_off_bat'].sum().reset_index()
    st.area_chart(team_scores.set_index('start_date'))

    batting_filtered_data = df[df['batting_team'] == selected_team].copy()
    batting_filtered_data['day_of_year'] = batting_filtered_data['start_date'].dt.dayofyear

    daily_scores = batting_filtered_data.groupby([batting_filtered_data['start_date'].dt.year, 'day_of_year'])[['runs_off_bat', 'extras']].sum().reset_index()
    daily_scores['total_score'] = daily_scores['runs_off_bat'] + daily_scores['extras']
    max_scores_per_year = daily_scores.groupby(daily_scores['start_date']).agg({'total_score': 'max'}).reset_index()

    st.subheader(f"Yearly Highest Scores for {selected_team}")
    st.line_chart(max_scores_per_year.set_index('start_date'))

    match_winner_table = filtered_data.groupby('start_date')[['our_team_won', 'opponent_team']].first().reset_index()

    summary = match_winner_table.groupby('opponent_team').agg(
        matches=('opponent_team', 'count'),
        wins=('our_team_won', lambda x: (x == "won").sum()),
        lost=('our_team_won', lambda x: (x == "lost").sum()),
        drawn=('our_team_won', lambda x: (x == "drawn").sum()),
    ).reset_index()
    # Divide the table based on whether the selected team is in the winners or losers column
    winners_count = match_winner_table[match_winner_table["our_team_won"] == "won"]

    # Count occurrences where winner is equal to selected team
    winner_counts = len(winners_count)
    st.write(f"Winning Percentage: {(winner_counts/num_matches)*100:.2f} %")
    # Create a stacked bar chart using Plotly Express
    fig = px.bar(summary, x='opponent_team', y=['wins', 'lost', 'drawn'],
                 title=f"{selected_team} - Performance Against Each Opponent",
                 labels={'value': 'Number of Matches', 'variable': 'Result'},
                 barmode='stack')
    fig.update_layout(xaxis_tickangle=-90)
    st.plotly_chart(fig, use_container_width=True)
    ###########################
    selected_opponent = st.selectbox("Select an Opponent", df['batting_team'].unique(), key="opponent_selection")
    filtered_data2 = filtered_data[filtered_data["opponent_team"] == selected_opponent]
    #st.write(filtered_data2)
    match_winner_table2 = filtered_data2.groupby('start_date')[['our_team_won', 'city']].first().reset_index()
    #st.write(match_winner_table2)

    summary2 = match_winner_table2.groupby('city').agg(
        matches=('start_date', 'count'),
        wins=('our_team_won', lambda x: (x == "won").sum()),
        lost=('our_team_won', lambda x: (x == "lost").sum()),
        drawn=('our_team_won', lambda x: (x == "drawn").sum()),
    ).reset_index()
    #st.write(summary2)
    fig = px.bar(summary2, x='city', y=['wins', 'lost', 'drawn'],
                 title=f"{selected_team} - Performance in that City against  {selected_opponent}",
                 labels={'value': 'Number of Matches', 'variable': 'Result'},
                 barmode='stack')
    fig.update_layout(xaxis_tickangle=-90)
    st.plotly_chart(fig, use_container_width=True)
    # Divide the table based on whether the selected team is in the winners or losers column
    # winners_count = match_winner_table[match_winner_table["our_team_won"] == "won"]

    # # Count occurrences where winner is equal to selected team
    # winner_counts = len(winners_count)
    # # Create the final pie chart
    # fig = px.pie(names=['Wins', 'Losses', 'Draws'],
    #              values=[win_counts, loss_counts, draw_counts],
    #              title=f"{selected_team} - Performance Over Time",
    #              labels={'value': 'Number of Matches', 'variable': 'Result'})
    # fig.update_traces(textinfo='percent+value')
    # st.plotly_chart(fig)
# Display function call
