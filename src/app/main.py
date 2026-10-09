import tfl.database_client

from datetime import datetime as dt, timezone, timedelta

import plotly.express as px
import polars as pl
import streamlit as st

"""
# Aldgate East Station
"""
def show_data(slider: int) -> tuple:
    db = tfl.database_client.database()

    data_crowding, data_disruptions, data_arrivals = (
        db
        .read_db()
    )
    
    data_crowding = (
        data_crowding
        .filter(
            pl.col("data_available") == 1
        )
        .with_columns(
            pl.col("time_local").str.to_datetime(time_zone = "Europe/London"),
            pl.col("time_utc").str.to_datetime(time_zone = "UTC"),
            
        )
        .filter(
            pl.col("time_utc") >= dt.now(timezone.utc).date() - timedelta(st.session_state.slider)
        )
        .select(
            pl.col("id"),
            (pl.col("percentage_baseline") * 100).round(2),
            pl.col("time_local")
        )
        .sort("id")
    )

    data_disruptions = (
        data_disruptions
        .with_columns(
            pl.col("time_utc").str.to_datetime(time_zone = "UTC"),
        )
        .filter(
            dt.now(timezone.utc) - pl.col("time_utc") < timedelta(minutes = 5)
        )
        .sort("id")
        .group_by("line")
        .last()
        .sort("line")
        .select(
            pl.col("line"),
            pl.col("description"),
            pl.col("time_local")
        )
    )

    data_arrivals = (
        data_arrivals
        .with_columns(
            pl.col("time_utc").cast(pl.String).str.to_datetime(time_zone="UTC"),
            pl.col("expected_arrival").cast(pl.String).str.to_datetime(time_zone="UTC"),
            pl.col("destination").cast(pl.String).str.replace(
                " Underground Station", ""
            )
        )
        .with_columns(
            time_remaining = pl.col("expected_arrival") - pl.col("time_utc")
        )
        .select(
            pl.col("line"),
            pl.col("platform"),
            pl.col("destination"),
            pl.col("time_remaining")
        )
        .sort("time_remaining")
        .group_by(["line", "platform"])
        .first()
    )

    return data_crowding, data_disruptions, data_arrivals

if "slider" not in st.session_state:
    st.session_state["slider"] = 7

data_crowding, data_disruptions, data_arrivals = show_data(st.session_state.slider)
last_crowd = data_crowding.select(pl.col("percentage_baseline").last()).item()
last_time = data_crowding.select(pl.col("time_local").last()).item()

"""
## Arrivals
"""
col_1, col_2 = st.columns(2)

with col_1:
    data_col_1 = (
        data_arrivals
        .filter(pl.col("platform") == "Westbound - Platform 1")
        .select(
            # pl.col("line"),
            pl.col("destination"),
            pl.col("time_remaining")
        )
    )
    st.subheader("Westbound - Platform 1")
    st.dataframe(data_col_1, column_config = {
        "destination": "Destination",
        "time_remaining": "Arrival Time"
    })

with col_2:
    data_col_2 = (
        data_arrivals
        .filter(pl.col("platform") == "Eastbound - Platform 2")
        .select(
            # pl.col("line"),
            pl.col("destination"),
            pl.col("time_remaining")
        )
    )
    st.subheader("Eastbound - Platform 2")
    st.dataframe(data_col_2, column_config = {
        "destination": "Destination",
        "time_remaining": "Arrival Time"
    })
# st.table(data_arrivals)

"""
## Disruptions
"""
st.table(data_disruptions, hide_header = True)

"""
## Crowding
"""
st.write(f"Crowd at {last_crowd}% of baseline at {last_time}.")

fig = px.line(
    data_crowding,
    x = "time_local",
    y = "percentage_baseline",
    labels = {
        "time_local": "Time",
        "percentage_baseline": "Crowd (% of Baseline)"
    }
)

st.plotly_chart(fig, use_container_width = True)

add_slider = st.slider(
    'How many historical days to include in plot?',
    min_value = 0, 
    max_value = 30, 
    value = 7,
    key = "slider" 
)

st.write(f"Showing today and past {st.session_state.slider} days.")



