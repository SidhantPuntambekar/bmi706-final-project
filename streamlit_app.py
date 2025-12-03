import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data

# @st.cache

st.title("Global Tuberculosis Burden, Our World in Data")
sidebar = st.sidebar.selectbox("Select Dashboard", ["Global Incidence of Tuberculosis",
                                                    "Age Distributions of Tuberculosis Related Deaths",
                                                    "Tuberculosis Diagnosis Gaps", 
                                                    "Geographic Patterns in Drug-Resistant TB Treatment Success",
                                                    "Associations Between Tuberculosis Burden and Key Risk Factors (HIV Prevalence)"])

if sidebar == "Global Incidence of Tuberculosis":
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
        tooltip = ["Country:N", "Incidence:Q"],
        ).properties(
        title=f'Tuberculosis Incidence Rate By Country, {year}'
    )

    part1_chart = alt.vconcat(background + chart_incidence).resolve_scale(color = 'independent')

    st.altair_chart(part1_chart, use_container_width=True)

elif sidebar == "Age Distributions of Tuberculosis Related Deaths":

    part2_df = pd.read_csv("data/2- tuberculosis-deaths-by-age.csv")

    death_cols = [
        "Deaths - Tuberculosis - Sex: Both - Age: 70+ years (Number)",
        "Deaths - Tuberculosis - Sex: Both - Age: 50-69 years (Number)",
        "Deaths - Tuberculosis - Sex: Both - Age: 15-49 years (Number)",
        "Deaths - Tuberculosis - Sex: Both - Age: 5-14 years (Number)",
        "Deaths - Tuberculosis - Sex: Both - Age: Under 5 (Number)"
    ]

    # Sum deaths across all countries for each year
    df_yearly = part2_df.groupby("Year")[death_cols].sum().reset_index()

    df_melted = df_yearly.melt(
        id_vars="Year",
        value_vars=death_cols,
        var_name="Age Group",
        value_name="Deaths"
    )

    df_melted["Age Group"] = df_melted["Age Group"].str.extract(r"Age: (.*) \(")
    # st.write(df_melted)

    # Year range slider
    min_year = int(df_melted["Year"].min())
    max_year = int(df_melted["Year"].max())

    year_range = st.slider(
        "Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

    # Filter by chosen year range
    subset = df_melted[
        (df_melted["Year"] >= year_range[0]) &
        (df_melted["Year"] <= year_range[1])
    ]

    age_order = ["Under 5", "5-14 years", "15-49 years", "50-69 years", "70+ years"]

    chart = alt.Chart(subset).mark_bar().encode(
        x=alt.X("Year:O"),
        xOffset=alt.XOffset("Age Group:N", sort = age_order),
        y=alt.Y("Deaths:Q", title="Tuberculosis Deaths"),
        color=alt.Color("Age Group:N", title="Age Group", sort = age_order),
        tooltip=["Year", "Age Group", "Deaths"]
    ).properties(
        width=600,
        height=400,
        title=f"Global Tuberculosis Deaths by Age Group ({year_range[0]}-{year_range[1]})"
    )

    st.altair_chart(chart, use_container_width=True)
