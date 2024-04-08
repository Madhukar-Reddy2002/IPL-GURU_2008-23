import streamlit as st
import pandas as pd
import plotly.express as px
import alltime
import team
import player

# Set page configuration
#st.set_page_config(page_title="IPL Guru", page_icon=":cricket_bat:", layout="wide")

# Load and preprocess data
@st.cache_data
def load_data(data_path):
    df = pd.read_csv(data_path, low_memory=False)
    df['start_date'] = pd.to_datetime(df['date'], dayfirst=True)
    df['total_runs'] = df['runs_off_bat']
    return df

data_path = './new2.csv'
df = load_data(data_path)

# App title and navigation
st.sidebar.title("🏏 IPL Guru By MS")
selected_page = st.sidebar.radio("Go to", ["Year Wise", "All Time Records","Team Wise", "Player Wise"])

if selected_page == "Year Wise":
    st.title("🏏 IPL Guru - Your Ultimate Cricket Companion 🏆")
    selected_year = st.sidebar.selectbox("Select a Year", df['start_date'].dt.year.unique(), key="year_selection")

    # Filter data by selected year
    filtered_data = df[df['start_date'].dt.year == selected_year].copy()

    # Function to display key stats
    def display_key_stats(data, title):
        num_matches = len(data["match_id"].unique())
        striker_runs = data.groupby(['batting_team', 'striker']).agg(
            total_runs=('total_runs', 'sum'),
            fours=('runs_off_bat', lambda x: (x == 4).sum()),
            sixes=('runs_off_bat', lambda x: (x == 6).sum()),
            num_times_striker=('striker', 'count')
        ).reset_index()
        max_runs_player = striker_runs.loc[striker_runs['total_runs'].idxmax()]
        tournament_total_runs = data['total_runs'].sum()
        tournament_fours = (data['runs_off_bat'] == 4).sum()
        tournament_sixes = (data['runs_off_bat'] == 6).sum()
        highest_score = data.groupby(['match_id', 'striker']).total_runs.sum().reset_index()
        max_score = highest_score.total_runs.max()
        max_score_player = highest_score[highest_score['total_runs'] == max_score].iloc[0]
        bowler_wickets = data[(data['wicket_type'].notna()) & (data['wicket_type'] != "run out")].groupby(['bowling_team', 'bowler'])['wicket_type'].count().reset_index()
        bowler_wickets.columns = ['Bowling Team', 'Bowler', 'Wickets']
        max_wickets_bowler = bowler_wickets.loc[bowler_wickets['Wickets'].idxmax()]
        tournament_wickets = bowler_wickets['Wickets'].sum()

        # Get winner and runner-up teams
        final_match = data.sort_values(by='start_date', ascending=False).iloc[0]
        player_ofm = final_match['player_of_match']
        winner_team = final_match['winner']
        if winner_team == final_match['team1']:
            runner_up_team = final_match['team2']
        else:
            runner_up_team = final_match['team1']
        won = f'{final_match["win_by_wickets"]} Wickets '
        if final_match["win_by_wickets"] == 0:
            won = f'{final_match["win_by_runs"]} Runs '
        else:
            won = f'{final_match["win_by_wickets"]} Wickets '

        st.subheader(f"🏆 {title} ({selected_year})")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Number of Matches", num_matches)
            st.metric("Tournament Fours", tournament_fours)
            st.metric("Tournament Sixes", tournament_sixes)
            st.metric("Tournament Total Runs", tournament_total_runs)
            st.metric("Tournament Total Wickets", tournament_wickets)
        with col2:
            st.metric("Highest Individual Score", max_score_player['striker'], f"{max_score_player['total_runs']} runs")
            st.metric("Orange Cap Holder", max_runs_player['striker'], f"{max_runs_player['total_runs']} runs")
            st.metric("Purple Cap Holder", max_wickets_bowler['Bowler'], f"{max_wickets_bowler['Wickets']} wickets")    
            
        with col3:
            st.metric("(Finals) Won By", won)
            st.metric("Winner", winner_team)
            st.metric("Runner-up", runner_up_team)
            st.metric("Player of Match (Finals)", player_ofm)

    # Display key stats
    display_key_stats(filtered_data, "Key Stats")

    # Display important charts
    st.subheader("🔥 Important Charts")

    # Total runs by team and striker
    striker_runs = filtered_data.groupby(['batting_team', 'striker']).agg(
        total_runs=('total_runs', 'sum'),
        balls_faced=('striker', 'count'),
        fours=('runs_off_bat', lambda x: (x == 4).sum()),
        sixes=('runs_off_bat', lambda x: (x == 6).sum()),
        num_times_striker=('striker', 'count')
    ).reset_index()

    striker_runs['strike_rate'] = (striker_runs['total_runs'] / striker_runs['balls_faced']) * 100

    max_runs_player = striker_runs.loc[striker_runs['total_runs'].idxmax()]

    fig_runs = px.bar(striker_runs, x='batting_team', y='total_runs', color='striker', title='Total Runs by Team and Striker', barmode='stack')
    fig_runs.update_layout(xaxis_title='Batting Team', yaxis_title='Total Runs', legend_title='Striker')
    # fig_runs.add_annotation(x=max_runs_player['batting_team'], y=max_runs_player['total_runs'],
    #                         text=f"<b>{max_runs_player['striker']}</b><br>{max_runs_player['total_runs']} runs",
    #                         showarrow=True, arrowhead=7, ax=0, ay=-40, bgcolor='orange', font=dict(color='black', size=14))
    st.plotly_chart(fig_runs, use_container_width=True)

    # Top 10 players by runs scored
    top_scorers = filtered_data.groupby([filtered_data['start_date'].dt.year, 'striker']).agg(
        total_runs=('total_runs', 'sum'),
        balls_faced=('striker', 'count'),
        num_wides=('wides', 'count'),
        num_no_balls=('noballs', 'count'),
        fours=('runs_off_bat', lambda x: (x == 4).sum()),
        sixes=('runs_off_bat', lambda x: (x == 6).sum())
    ).reset_index()

    top_scorers['balls_faced'] = top_scorers['balls_faced'] - top_scorers['num_wides'] - top_scorers['num_no_balls']

    top_scorers['strike_rate'] = (top_scorers['total_runs'] / top_scorers['balls_faced']) * 100

    top_scorers = top_scorers.sort_values(['start_date', 'total_runs'], ascending=[True, False])
    top_scorers['Rank'] = top_scorers.groupby('start_date')['total_runs'].rank(method='dense', ascending=False)
    top_scorers = top_scorers[top_scorers['Rank'] <= 10]
    top_scorers["non_boundaries"] = top_scorers["total_runs"] - top_scorers["fours"] * 4 - top_scorers["sixes"] * 6
    top_scorers["4_boundaries"] = top_scorers["fours"] * 4
    top_scorers["6_boundaries"] = top_scorers["sixes"] * 6

    temp_top_scorers = top_scorers.drop(['start_date', 'non_boundaries', '4_boundaries', '6_boundaries', 'Rank', "num_wides", "num_no_balls"], axis=1)
    temp_top_scorers.set_index('striker', inplace=True)
    # Combined top scorers and stats
    top_scorers_stats = filtered_data.groupby([filtered_data['start_date'].dt.year, 'player_dismissed']).size().reset_index(name='num_times_out')
    combined_data = pd.merge(top_scorers, top_scorers_stats, left_on='striker', right_on='player_dismissed', how='left')
    combined_data['Batt. AVG'] = combined_data['total_runs'] / combined_data['num_times_out']

    temp_combined = combined_data.drop(['start_date_x', 'start_date_y', 'player_dismissed', 'num_times_out', 'non_boundaries', '4_boundaries', '6_boundaries',"num_wides", "num_no_balls"], axis=1)
    temp_combined.set_index('Rank', inplace=True)  # Set 'Rank' column as index
    st.subheader("🏏 This Year Top Scorers and Stats")
    st.write(temp_combined)
    #st.write(temp_top_scorers)

    # Create a line chart for total runs per match
    # Create a line chart for total runs per match by team
    total_runs_per_match_by_team = filtered_data.groupby(['start_date', 'batting_team'])['total_runs'].sum().reset_index()
    fig_runs_per_match = px.line(total_runs_per_match_by_team, x='start_date', y='total_runs', color='batting_team', title='Total Runs per Match by Team')
    st.plotly_chart(fig_runs_per_match, use_container_width=True)

    # Additional charts and insights
    st.subheader("📊 Additional Insights")

    # Centuries with Bowling Team and Additional Metrics
    centuries = filtered_data.groupby([filtered_data['start_date'].dt.date, 'bowling_team', 'striker']).agg(
        total_runs=('total_runs', 'sum'),
        balls_faced=('striker', 'count'),
        fours=('runs_off_bat', lambda x: (x == 4).sum()),
        sixes=('runs_off_bat', lambda x: (x == 6).sum()),
        num_wides=('wides', 'count'),
    ).reset_index()
    full_centuries = centuries[centuries.total_runs >= 100]
    half_centuries = centuries[(centuries.total_runs >= 50) & (centuries.total_runs <= 99)]
    if not full_centuries.empty:
        full_centuries['balls_faced'] = centuries['balls_faced'] - centuries['num_wides']
        full_centuries['strike_rate'] = (centuries['total_runs'] / centuries['balls_faced']) * 100

        full_centuries = full_centuries.sort_values(by='total_runs', ascending=False)
        full_centuries['Rank'] = full_centuries['total_runs'].rank(ascending=False, method='min')
        # Move the 'start_date' column to the second position
        start_date_col = full_centuries.pop('start_date')
        full_centuries.insert(1, 'start_date', start_date_col)
        full_centuries.set_index('Rank', inplace=True)  # Set 'Rank' column as index
        st.subheader(f"👏 Centuries ({selected_year})")
        st.write(full_centuries)
    else:
        st.write('No players scored more than 100 runs in a single match.')
    if not half_centuries.empty:
        half_centuries['balls_faced'] = half_centuries['balls_faced'] - half_centuries['num_wides']
        half_centuries['strike_rate'] = (half_centuries['total_runs'] / half_centuries['balls_faced']) * 100

        half_centuries = half_centuries.sort_values(by='total_runs', ascending=False)
        half_centuries['Rank'] = half_centuries['total_runs'].rank(ascending=False, method='min')
        # Move the 'start_date' column to the second position
        start_date_col = half_centuries.pop('start_date')
        half_centuries.insert(1, 'start_date', start_date_col)
        half_centuries.set_index('Rank', inplace=True)  # Set 'Rank' column as index
        st.subheader(f"👏 Half -Centuries ({selected_year})")
        st.write(half_centuries)
    else:
        st.write('No players scored more than 50 runs in a single match.')

    # Runs distribution
    runs_distribution = filtered_data.groupby('runs_off_bat').size().reset_index(name='count')
    fig_runs_distribution = px.pie(runs_distribution, values='count', names='runs_off_bat', title='Runs Distribution (Fours vs. Sixes)')
    st.subheader(f"🔢 Runs Distribution ({selected_year})")
    st.plotly_chart(fig_runs_distribution, use_container_width=True)

    # Wickets taken by bowler and bowling team
    bowler_wickets = filtered_data[(filtered_data['wicket_type'].notna()) & (filtered_data['wicket_type'] != "run out")].groupby(['bowling_team', 'bowler'])['wicket_type'].count().reset_index()
    bowler_wickets.columns = ['Bowling Team', 'Bowler', 'Wickets']
    max_wickets_bowler = bowler_wickets.loc[bowler_wickets['Wickets'].idxmax()]

    fig_bowlers = px.bar(bowler_wickets, x='Bowling Team', y='Wickets', color='Bowler', title='Wickets Taken by Bowler and Bowling Team', barmode='stack')
    # fig_bowlers.add_annotation(x=max_wickets_bowler['Bowling Team'], y=max_wickets_bowler['Wickets'],
    #                         text=f"<b>{max_wickets_bowler['Bowler']}</b><br>{max_wickets_bowler['Wickets']} wickets",
    #                         showarrow=True, arrowhead=7, ax=0, ay=-40, bgcolor='purple', font=dict(color='white', size=14))
    st.plotly_chart(fig_bowlers, use_container_width=True)

    # Create a line chart for total wickets per match
    # Create a line chart for total wickets per match by team
    total_wickets_per_match_by_team = filtered_data[(filtered_data['wicket_type'].notna()) & (filtered_data['wicket_type'] != "run out")].groupby(['start_date', 'bowling_team'])['wicket_type'].count().reset_index()
    fig_wickets_per_match = px.line(total_wickets_per_match_by_team, x='start_date', y='wicket_type', color='bowling_team', title='Total Wickets per Match by Team')
    st.plotly_chart(fig_wickets_per_match, use_container_width=True)
elif selected_page == "All Time Records":
    alltime.display_all_time_records()
elif selected_page == "Team Wise":
    team.display(df)
    pass
elif selected_page == "Player Wise":
    player.display_player_dashboard(df)
    # Code for Player Wise page
    pass
