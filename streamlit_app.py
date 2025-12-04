import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data

# @st.cache

st.title("Global Tuberculosis Burden Dashboard, Our World in Data")
sidebar = st.sidebar.selectbox("Select Dashboard", ["Global Incidence of Tuberculosis",
                                                    "Age Distributions of Tuberculosis Related Deaths",
                                                    "Tuberculosis Diagnosis Gaps", 
                                                    "Drug-Resistant TB Treatment Success Rate",
                                                    "Associations Between Tuberculosis Burden and Key Risk Factors (HIV Prevalence)"])

if sidebar == "Global Incidence of Tuberculosis":
    def part1_load_data():
        df_incidence = pd.read_csv("data/1- incidence-of-tuberculosis-sdgs.csv")
        df_case_detection_rate = pd.read_csv("data/detection_rate.csv")

        df_incidence = df_incidence.rename(columns={
            "Entity": "Country",
            "Estimated incidence of all forms of tuberculosis": "Incidence"
        })

        df_case_detection_rate = df_case_detection_rate.rename(columns={
            "Entity": "Country",
            "Case detection rate (all forms)": "Case Detection Rate"
        })

        df_incidence_country = df_incidence[df_incidence["Code"].notna() & (df_incidence["Code"] != "")]
        df_case_detection_rate = df_case_detection_rate[df_case_detection_rate["Code"].notna() & (df_case_detection_rate["Code"] != "")]

        country_df = pd.read_csv(
            "https://raw.githubusercontent.com/hms-dbmi/bmi706-2022/main/cancer_data/country_codes.csv",
            dtype={"country-code": str}
        )
    
        df_incidence_country_id = df_incidence_country.merge(
            country_df[["alpha-3", "country-code"]],
            left_on = "Code",
            right_on = "alpha-3",
            how = "left"
        ).drop(columns = ["alpha-3"])

        df_case_detection_rate_id = df_case_detection_rate.merge(
            country_df[["alpha-3", "country-code"]],
            left_on = "Code",
            right_on = "alpha-3",
            how = "left"
        ).drop(columns = ["alpha-3"])

        return df_incidence_country_id, df_case_detection_rate_id

    part1_df_incidence, part1_df_case_detection = part1_load_data()

    year = st.slider("Year", min_value = int(part1_df_incidence["Year"].min()), max_value = int(part1_df_incidence["Year"].max()), value = 2012)

    subset = pd.merge(
        part1_df_incidence,
        part1_df_case_detection,
        on = ["Country", "Year", "Code", "country-code"],
        how = "inner"
    )

    subset = subset[subset["Year"] == year]

    source = alt.topo_feature(data.world_110m.url, "countries")

    width = 600
    height = 300
    project = "equirectangular"

    background = (
        alt.Chart(source)
        .mark_geoshape(fill = "#aaa", stroke = "white")
        .properties(width = width, height = height)
        .project(project)
    )

    selector = alt.selection_point(fields=["id"], empty="all")
    
    chart_base = (
        alt.Chart(source)
        .properties(width = width, height = height)
        .project(project)
        .transform_lookup(
            lookup = "id",
            from_ = alt.LookupData(
                subset,
                "country-code",
                ["Country", "Code", "Incidence", "Case Detection Rate"]
            )
        )
        .add_params(selector)
    )

    incidence_scale = alt.Scale(domain = [part1_df_incidence["Incidence"].min(), part1_df_incidence["Incidence"].max()], scheme = "yellowgreenblue")

    chart_incidence = chart_base.mark_geoshape().encode(
        color = alt.Color("Incidence:Q", scale=incidence_scale),
        tooltip = ["Country:N", "Incidence:Q"]
    ).transform_filter(selector).properties(
        title=alt.TitleParams(
            text = f"Estimated rate of new tuberculosis cases per 100,000 people, {year}",
            fontSize = 16,
            subtitle = "Includes both new and latent reactivated infections",
            subtitleColor = "white",
            subtitleFontSize = 12,
            subtitleFontWeight = "normal"
        )
    )

    rate_scale = alt.Scale(domain = [part1_df_case_detection["Case Detection Rate"].min(), part1_df_case_detection["Case Detection Rate"].max()], scheme = "oranges")

    chart_case_detection_rate = chart_base.mark_geoshape().encode(
        color = alt.Color("Case Detection Rate:Q", scale=rate_scale),
        tooltip = ["Country:N", "Case Detection Rate:Q"]
    ).transform_filter(selector).properties(
        title = alt.TitleParams(
            text = f"Estimated tuberculosis case detection rate, {year}",
            fontSize = 16,
            subtitle = "Represents tuberculosis cases that were detected and treated in national tuberculosis control programs",
            subtitleColor = "white",
            subtitleFontSize = 12,
            subtitleFontWeight = "normal"
        )
    )

    part1_chart = alt.vconcat(
        background + chart_incidence,
        background + chart_case_detection_rate
    ).resolve_scale(color="independent")

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
    

elif sidebar == "Tuberculosis Diagnosis Gaps":
    def part3_load_data():
        # Load datasets
        df_detect = pd.read_csv("data/detection_rate.csv")
        df_deaths = pd.read_csv("data/death_by_age.csv")

        # Rename columns
        df_detect = df_detect.rename(columns={
            "Entity": "Country",
            "Case detection rate (all forms)": "DetectionRate"
        })
        df_deaths = df_deaths.rename(columns={"Entity": "Country"})

        # Death columns by age group
        death_cols = [
            "Deaths - Tuberculosis - Sex: Both - Age: 70+ years (Number)",
            "Deaths - Tuberculosis - Sex: Both - Age: 50-69 years (Number)",
            "Deaths - Tuberculosis - Sex: Both - Age: 15-49 years (Number)",
            "Deaths - Tuberculosis - Sex: Both - Age: 5-14 years (Number)",
            "Deaths - Tuberculosis - Sex: Both - Age: Under 5 (Number)"
        ]

        # Compute total deaths
        df_deaths["Death"] = df_deaths[death_cols].sum(axis=1)

        # Merge datasets
        df_merged = pd.merge(
            df_detect[["Country", "Year", "DetectionRate"]],
            df_deaths[["Country", "Year", "Death"]],
            on=["Country", "Year"],
            how="inner"
        )

        # Compute diagnosed cases
        df_merged["Diagnosed"] = df_merged["Death"] * df_merged["DetectionRate"]

        # Compute difference
        df_merged["Difference"] = df_merged["Diagnosed"] - df_merged["Death"]

        # Final dataframe
        df_final = df_merged[["Country", "Year", "Death", "Diagnosed", "Difference"]]
        return df_final

    df = part3_load_data()

    # Select country
    countries = sorted(df["Country"].unique())
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

    # Merge back for tooltip
    df_melt = df_melt.merge(
        df_country[["Year", "Death", "Diagnosed", "Difference"]],
        on="Year",
        how="left"
    )

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

elif sidebar == "Drug-Resistant TB Treatment Success Rate":
    def part4_load_data():
        df_xdr_mdr = pd.read_csv("data/4- tuberculosis-treatment-success-rate-by-type.csv")

        df_xdr_mdr = df_xdr_mdr.rename(columns={
            "Entity": "Country",
            "Indicator:Treatment success rate: new TB cases": "New TB Cases Treatment Success Rate",
            "Indicator:Treatment success rate for patients treated for MDR-TB (%)": "MDR-TB Cases Treatment Success Rate", 
            "Indicator:Treatment success rate: XDR-TB cases": "XDR-TB Cases Treatment Success Rate", 
        })

        return df_xdr_mdr
    
    part4_df_xdr_mdr = part4_load_data()

    default_countries = [
        "South Africa",
        "India",
        "Spain",
        "Hungary",
        "France"
    ]

    countries = st.multiselect(
        "Countries",
        part4_df_xdr_mdr["Country"].unique(),
        default = default_countries
    )

    country_filtered_df_xdr_mdr = part4_df_xdr_mdr[
        part4_df_xdr_mdr["Country"].isin(countries)
    ]

    country_filtered_df_xdr_mdr_melt = country_filtered_df_xdr_mdr.melt(
        id_vars=["Country", "Year"],
        value_vars = ["New TB Cases Treatment Success Rate", "MDR-TB Cases Treatment Success Rate", "XDR-TB Cases Treatment Success Rate"],
        var_name = "Tuberculosis Type",
        value_name = "Treatment Success Rate"
    )

    chart_list = []

    for country in countries:
        single_country_df = country_filtered_df_xdr_mdr_melt[country_filtered_df_xdr_mdr_melt["Country"] == country]

        chart = alt.Chart(single_country_df).mark_line(
            point=True
        ).encode(
            x = alt.X("Year:O", title="Year"),
            y = alt.Y("Treatment Success Rate:Q", title = "Treatment Success Rate (%)", scale = alt.Scale(domain = [0, 100])),
            color = alt.Color("Tuberculosis Type:N", title = "Tuberculosis Case Type"),
            tooltip = ["Country", "Year", "Tuberculosis Type", "Treatment Success Rate"]
        ).properties(
            width = 700,
            height = 300,
            title = country
        )

        chart_list.append(chart)

    # Source: https://github.com/vega/altair/issues/1281
    final_chart = alt.vconcat(*chart_list)
    st.altair_chart(final_chart, use_container_width=True)