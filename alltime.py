import streamlit as st
import pandas as pd
import numpy as np

def display_all_time_records():
    st.title("🌍 IPL All Time Records")
    st.sidebar.title("IPL Records")

    # Get data from the database
    data_path = './new2.csv'
    df = pd.read_csv(data_path)
    df['start_date'] = pd.to_datetime(df['date'], dayfirst=True)

    def display_key_stats(data):
        num_matches = len(data["match_id"].unique())

        # Batters stats
        batter_stats = data.groupby(['striker']).agg(
            total_runs=('runs_off_bat', 'sum'),
            extras=('extras', 'sum'),
            balls_faced=('striker', 'count'),
            wides_faced=('wides', 'count'),
            num_matches=('match_id', 'nunique'),
            num_outs=('player_dismissed', lambda x: (~x.isna()).sum()),
            fours=('runs_off_bat', lambda x: (x == 4).sum()),
            sixes=('runs_off_bat', lambda x: (x == 6).sum()),
            num_times_striker=('striker', 'count')
        ).reset_index()

        # Calculate batting average
        batter_stats['batting_avg'] = batter_stats['total_runs'] / (batter_stats['num_outs'] + 1e-9)  # Add 1e-9 to avoid division by zero
        batter_stats.loc[batter_stats['batting_avg'] == np.inf, 'batting_avg'] = np.nan  # Replace infinite values with NaN

        # Filter batters with at least 50 unique matches and more than 150 balls faced
        filtered_batting_stats = batter_stats[(batter_stats['num_matches'] >= 50) & (batter_stats['balls_faced'] > 150)]

        # Dismissals
        dismissals = data.groupby(['player_dismissed']).agg(
            num_times_out=('player_dismissed', lambda x: (~x.isna()).sum())
        ).reset_index().sort_values('num_times_out', ascending=False)

        # Best Batters
        max_runs_player = batter_stats.loc[batter_stats['total_runs'].idxmax()]
        max_sr_player = filtered_batting_stats.loc[(filtered_batting_stats['total_runs'] / (filtered_batting_stats['balls_faced'] - filtered_batting_stats['wides_faced'])).idxmax()]
        max_fours_player = batter_stats.loc[batter_stats['fours'].idxmax()]
        max_sixes_player = batter_stats.loc[batter_stats['sixes'].idxmax()]
        max_batting_avg_player = filtered_batting_stats.loc[filtered_batting_stats['batting_avg'].idxmax()]

        # Highest Individual Score
        highest_score = data.groupby(['match_id', 'striker'])['runs_off_bat'].sum().reset_index()
        max_score_player = highest_score.loc[highest_score['runs_off_bat'].idxmax()]
        # Filter the highest_score DataFrame based on the condition
        filtered_scores = highest_score[highest_score['runs_off_bat'] > 99]
        striker_counts = filtered_scores['striker'].value_counts()
        most_centuries_player = striker_counts.idxmax()

        # Find the count of the maximum appearances
        most_centuries_count = striker_counts.max()



        # Best Bowlers
        bowler_wickets = data[(data['wicket_type'].notna()) & (data['wicket_type'] != "run out")].groupby(['bowler'])['wicket_type'].count().reset_index()
        bowler_wickets.columns = ['Bowler', 'Wickets']
        max_wickets_bowler = bowler_wickets.loc[bowler_wickets['Wickets'].idxmax()]
        tournament_wickets = bowler_wickets['Wickets'].sum()

        # Most Sixes in a Single Match
        max_sixes_in_match = data.groupby(['match_id', 'striker']).agg({'runs_off_bat': lambda x: (x == 6).sum()}).reset_index()
        max_sixes_in_match_player = max_sixes_in_match.loc[max_sixes_in_match['runs_off_bat'].idxmax()]

        # Highest and Lowest Team Score in a Single Day
        team_scores = data.groupby(['start_date', 'batting_team', 'bowling_team'])[['runs_off_bat', 'extras']].sum().reset_index()
        highest_team_score = team_scores.loc[team_scores['runs_off_bat'].idxmax()]
        #lowest_team_score = team_scores.loc[team_scores['runs_off_bat'].idxmin()]
        st.subheader("🏆 Key Points (All-Time)")

        col1, col2, col3 = st.columns(3)

        with col3:
            #st.metric("Number of Matches", num_matches)
            st.metric("Highest SR (atleast 50 innings)", f"{max_sr_player['striker']}",f"{max_sr_player['total_runs'] / (max_sr_player['balls_faced'] - max_sr_player['wides_faced']) * 100:.2f}%")
            st.metric("Highest Batt AVG (atleast 50 innings)", max_batting_avg_player['striker'], f"{max_batting_avg_player['batting_avg']:.2f}")
            st.metric("Highest Team Score", highest_team_score['batting_team'], f"{highest_team_score['runs_off_bat'] + highest_team_score['extras']} runs (vs {highest_team_score['bowling_team']})")
            #st.metric("Lowest Team Score", lowest_team_score['batting_team'], f"{lowest_team_score['runs_off_bat'] + lowest_team_score['extras']} runs (vs {lowest_team_score['bowling_team']})")

        with col2:
            st.metric("Highest no. of Fours", max_fours_player['striker'], f"{max_fours_player['fours']}")
            st.metric("Highest no. of Sixes", max_sixes_player['striker'], f"{max_sixes_player['sixes']}")
            st.metric("Most Sixes in a Match", max_sixes_in_match_player['striker'], f"{max_sixes_in_match_player['runs_off_bat']}")

        with col1:
            st.metric("Highest Number Runs", max_runs_player['striker'], f"{max_runs_player['total_runs']} runs in {max_runs_player['num_matches']} matches")
            st.metric("Highest Individual Score", max_score_player['striker'], f"{max_score_player['runs_off_bat']} runs")
            st.metric("Most Centuries ", most_centuries_player, f"{most_centuries_count}")
            st.metric("most no. of Wickets By ", max_wickets_bowler['Bowler'], f"{max_wickets_bowler['Wickets']} wickets")
            #st.metric("Tournament Total Wickets", tournament_wickets)
            #st.metric("Most Centuries", most_centuries_player['striker'], f"{most_centuries_player['match_id']} centuries")

    display_key_stats(df)
