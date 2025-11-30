import altair as alt
import pandas as pd
import streamlit as st

# @st.cache

st.write("## Global Tuberculosis Burden, Our World in Data")


# 3. Death vs Diagnosis

def part3_load_data():

    df_detect = pd.read_csv("data/detection_rate.csv")
    df_deaths = pd.read_csv("data/death_by_age.csv")

    df_detect = df_detect.rename(columns={
        "Entity": "Country",
        "Case detection rate (all forms)": "DetectionRate"
    })

    df_deaths = df_deaths.rename(columns={"Entity": "Country"})

    death_cols = [
        "Deaths - Tuberculosis - Sex: Both - Age: 70+ years (Number)",
        "Deaths - Tuberculosis - Sex: Both - Age: 50-69 years (Number)",
        "Deaths - Tuberculosis - Sex: Both - Age: 15-49 years (Number)",
        "Deaths - Tuberculosis - Sex: Both - Age: 5-14 years (Number)",
        "Deaths - Tuberculosis - Sex: Both - Age: Under 5 (Number)"
    ]

    # Compute total deaths
    df_deaths["Death"] = df_deaths[death_cols].sum(axis=1)

    # Merge datasets by Country and Year
    df_merged = pd.merge(
        df_detect[["Country", "Year", "DetectionRate"]],
        df_deaths[["Country", "Year", "Death"]],
        on=["Country", "Year"],
        how="inner"
    )

    # Compute "Diagnosed" = Death * CaseDetectionRate
    df_merged["Diagnosed"] = df_merged["Death"] * df_merged["DetectionRate"]

    df_final = df_merged[["Country", "Year", "Diagnosed", "Death"]]

    return df_final


df = part3_load_data()


st.write("## Deaths vs Diagnosed")

# Select country
countries = sorted(df["Country"].unique())

# Default to Afghanistan
default_index = countries.index("Afghanistan") if "Afghanistan" in countries else 0

selected_country = st.selectbox(
    "Select a Country",
    countries,
    index=default_index
)

df_country = df[df["Country"] == selected_country].copy()

# Melt for plotting
df_melt = df_country.melt(
    id_vars=["Country", "Year"],
    value_vars=["Death", "Diagnosed"],
    var_name="Measure",
    value_name="Value"
)

# Compute difference
df_country["Difference"] = df_country["Diagnosed"] - df_country["Death"]

# Points
points = (
    alt.Chart(df_melt)
    .mark_circle(size=80)
    .encode(
        x=alt.X("Value:Q", title="Number of Cases"),
        y=alt.Y("Year:O", sort="ascending"),
        color=alt.Color("Measure:N", scale=alt.Scale(scheme="tableau10")),
        tooltip=[
            alt.Tooltip("Year:O"),
            alt.Tooltip("Death:Q"),
            alt.Tooltip("Diagnosed:Q"),
            alt.Tooltip("Difference:Q")
        ]
    )
)

# Lines connecting points per year
lines = (
    alt.Chart(df_country)
    .mark_rule()
    .encode(
        y=alt.Y("Year:O", sort="ascending"),
        x=alt.X("Death:Q"),
        x2="Diagnosed:Q",
        tooltip=[
            alt.Tooltip("Year:O"),
            alt.Tooltip("Death:Q"),
            alt.Tooltip("Diagnosed:Q"),
            alt.Tooltip("Difference:Q")
        ]
    )
)

chart = (lines + points).properties(
    title=f"Number of Deaths vs Diagnosed Cases {selected_country}",
    height=500
)

st.altair_chart(chart, use_container_width=True)
