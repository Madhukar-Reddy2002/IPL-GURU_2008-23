import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

def display_player_dashboard(df):
    selected_player = st.sidebar.selectbox("Select a Player", sorted(df['striker'].unique()), key="player_selection")
    """Display the player-wise dashboard"""
    st.title(f"🏏 {selected_player}'s IPL Dashboard")

    # Filter data for selected player
    batting_data = df[(df['striker'] == selected_player)].copy()
    num_matches = len(batting_data["match_id"].unique())
    runs_scored = sum(batting_data["runs_off_bat"])
    balls_faced = len(batting_data)
    num_times_out = df[df["player_dismissed"] == selected_player].shape[0]
    batting_avg = runs_scored / num_times_out if num_times_out > 0 else "Not available"
    strike_rate = round((runs_scored / balls_faced) * 100, 2) if balls_faced > 0 else "Not Available"
    max_runs_single_day = batting_data.groupby(["start_date"])["runs_off_bat"].sum().max()  # Maximum runs scored in a single start_day

    # Key Metrics
    st.header("Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Number of Matches Played", num_matches)
        st.metric("Balls Faced", balls_faced)
        st.metric("Number of Times Out", num_times_out)

    with col2:
        st.metric("Runs Scored", runs_scored)
        st.metric("Strike Rate", strike_rate)

    with col3:
        st.metric("Batting Average", round(batting_avg, 2))
        st.metric("Max Runs in Single Day", max_runs_single_day)

    # Top 10 Scores
    st.header("Top 10 Scores")
    st.write(batting_data.groupby(["start_date", "venue", "date", "batting_team", "bowling_team"])
             ["runs_off_bat"].sum().nlargest(10).reset_index())

    # Total Runs per Year
    st.header("Total Runs per Year")
    sm = batting_data.groupby([batting_data["start_date"].dt.year, "batting_team"])["runs_off_bat"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    for team in sm['batting_team'].unique():
        team_data = sm[sm['batting_team'] == team]
        ax.bar(team_data['start_date'], team_data['runs_off_bat'], label=team)
    ax.set_xlabel('Year')
    ax.set_ylabel('Total Runs')
    ax.set_title(f"Total Runs per Year for {selected_player}")
    ax.legend()
    st.pyplot(fig)

    # Line graph for strike rate year-wise
    st.header("Average Strike Rate per Year")
    strike_rate_data = batting_data.groupby(batting_data["start_date"].dt.year).apply(
        lambda x: (x["runs_off_bat"].sum() / x.shape[0]) * 100).reset_index(name="strike_rate")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(strike_rate_data["start_date"], strike_rate_data["strike_rate"], marker='o')
    ax.set_title(f"Average Strike Rate per Year for {selected_player}")
    ax.set_xlabel("Year")
    ax.set_ylabel("Strike Rate")
    st.pyplot(fig)

    # Line graph for batting average year-wise
    st.header("Average Batting Average per Year")
    batting_avg_data = batting_data.groupby(batting_data["start_date"].dt.year).apply(
        lambda x: x["runs_off_bat"].sum() / len(x["player_dismissed"].unique())).reset_index(name="batting_avg")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(batting_avg_data["start_date"], batting_avg_data["batting_avg"], marker='o')
    ax.set_title(f"Average Batting Average per Year for {selected_player}")
    ax.set_xlabel("Year")
    ax.set_ylabel("Batting Average")
    st.pyplot(fig)
