import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data

# @st.cache

st.write("## Global Tuberculosis Burden, Our World in Data")

def part1_load_data():
    df_incidence = pd.read_csv('data/1- incidence-of-tuberculosis-sdgs.csv')

    df_incidence = df_incidence.rename(columns={
        "Entity": "Country",
        "Estimated incidence of all forms of tuberculosis": "Incidence"
    })

    df_incidence_country = df_incidence[df_incidence["Code"].notna() & (df_incidence["Code"] != "")]

    country_df = pd.read_csv('https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv', dtype = {'conuntry-code': str})
    df_incidence_country_id = df_incidence_country.merge(country_df[["Country", "country-code"]], on = "Country", how = "left")

    return df_incidence_country_id

part1_df = part1_load_data()

year = st.slider("Year", min_value = part1_df["Year"].min(), max_value = part1_df["Year"].max(), value = 2012)
subset = part1_df[part1_df["Year"] == year]

source = alt.topo_feature(data.world_110m.url, 'countries')

width = 600
height  = 300
project = 'equirectangular'

background = alt.Chart(source
).mark_geoshape(
    fill = '#aaa',
    stroke = 'white'
).properties(
    width = width,
    height = height
).project(project)

chart_base = alt.Chart(source).properties(
        width = width, 
        height = height
    ).project(project
    ).transform_lookup(
        lookup= "id",
        from_= alt.LookupData(
            subset,
            "country-code",
            ["Country", "Code", "Incidence"]
        )
    )

rate_scale = alt.Scale(domain=[part1_df['Incidence'].min(), part1_df['Incidence'].max()], scheme = 'oranges')
rate_color = alt.Color(field = "Incidence", type = "quantitative", scale = rate_scale)

chart_incidence = chart_base.mark_geoshape().encode(
    color = alt.Color("Incidence:Q", scale = rate_scale),
    tooltip = ["Incidence:Q", "Country:N"],
    ).properties(
      title=f'Tuberculosis Incidence Rate By Country, {year}'
)

part1_chart = alt.vconcat(background + chart_incidence).resolve_scale(color = 'independent')

st.altair_chart(part1_chart, use_container_width=True)