# BMI 706: Tuberculosis Dashboard Final Project 

Authors: Claire Qu, Sidhant Puntambekar, Beatrice Chen, Christine Song

Team Name: The Last Altairbenders

# Dataset Overview

Our dataset is from Kaggle (1), originally sourced from Our World in Data (2), a UK-based nonprofit
that publishes data on various world issues. We will be working with a dataset consisting of a
collection of six tuberculosis (TB) tables that include information about tuberculosis incidence,
deaths by age, case detection rate, treatment success rate by tuberculosis resistance type
(multidrug resistant TB vs. extensively drug resistant TB), HIV incidence, and deaths under age
five categorized from the Institute of Health Metrics and Evaluation.

# Variables

* Categorical data: 3 unique types of treatment (TB vs. MDR-TB vs. XDR-TB)
* Ordinal data: age group (>5, 5-14, 15-49, 50-69, 70+)
* Quantitative data
    * Estimated incidence of tuberculosis
    * Number of deaths by tuberculosis
    * Case detection rate
    * Treatment success rate
    * HIV incidence rates among tuberculosis patients
* Temporal data: Year (2000-2022 for incidence of tuberculosis and HIV; 1999-2019 for deaths; 1995-2019 for treatment success rate)
* Geospatial data: 228 unique countries globally

# Target Audience
Our main goal for the tuberculosis visualization tool is to describe the prevalence of TB cases globally, identify key risk factors such as HIV comorbidities, as well as emphasize current challenges to TB medical care (such as antibiotic resistance and diagnosis gaps). The visualization tool will be designed for the general public to easily explore global trends, understand the drivers of tuberculosis burden, and recognize the persistent gaps in treatment. 

# Visualization Tasks 

1. Describe trends in global and regional tuberculosis incidence and mortality over time. 
2. Categorize age distributions of tuberculosis related deaths to highlight the differences in adult vs. child mortality. 
3. Comparison of estimated tuberculosis deaths vs. number of diagnosed cases to visualize diagnosis gaps. 
4. Geographical distribution and prevalence of treatment success rate for antibiotic-resistant tuberculosis (MDR, XDR) cases. 
5. Relationships between tuberculosis burden and major risk factors (from orthogonal datasets) such as HIV prevalence. 

# References

References

1. Momeni, M. (2023). Tuberculosis [Dataset]. Kaggle. Retrieved November 3, 2025, from:
https://www.kaggle.com/datasets/imtkaggleteam/tuberculosis

2. Dattani, S., Spooner, F., Ritchie, H., & Roser, M. (2023). Tuberculosis. Our World in Data.
https://ourworldindata.org/tuberculosis