import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

path = "./data/kaggle_survey_2021_responses.csv"


@st.cache
def load_data():
    data = pd.read_csv(path, low_memory=False)
    return data


def profile_plot(df, profile_metric, position):

    if profile_metric != "Country":

        grouped_df = df.groupby(["Position", profile_metric]).size().unstack().fillna(0)
        vals = grouped_df.loc[position].values

        fig = go.Figure(
            go.Pie(
                labels=grouped_df.columns,
                values=vals,
                hole=0.3,
                pull=(vals == max(vals)) * 0.2,
            )
        )
        fig.update_layout(width=600, height=500)
        if profile_metric == "Age":
            fig.update_layout(title=dict(text=f"Age distribution of {position}", x=0.5))
        if profile_metric == "Education":
            fig.update_layout(title=dict(text=f"Education level of {position}", x=0.5))
        if profile_metric == "Programming experience":
            fig.update_layout(
                title=dict(text=f"Programming experience of {position}", x=0.5)
            )
        st.plotly_chart(fig)
    else:
        grouped_df = (
            df[df["Position"] == position]["Country"].value_counts().reset_index()
        )
        grouped_df["Country"] = (grouped_df["Country"] * 100) / (
            grouped_df["Country"].sum()
        )
        grouped_df.rename(
            columns={"index": "country", "Country": "percentage"}, inplace=True
        )
        map = px.choropleth(
            grouped_df,
            locations=grouped_df.country,
            color=grouped_df.percentage,
            locationmode="country names",
            color_continuous_scale="viridis",
            title=f"Country residence of {position}",
            range_color=[0, 10],
        )
        map.update(layout=dict(title=dict(x=0.5)))
        st.plotly_chart(map)


def profile_desc(df, profile_metric, position):
    """
    Return some descriptions of the plot given a profile metric and the position title
    """

    data = df[df["Position"] == position][profile_metric].value_counts()
    if profile_metric == "Age":
        st.markdown(f"Most {position} aged **{data.idxmax()}**.")
    if profile_metric == "Country":
        st.markdown(f"Most {position} are from **{data.idxmax()}**.")
    if profile_metric == "Education":
        st.markdown(
            f"Most {position} have an education of or plan to attain an education of **{data.idxmax()}**."
        )
    if profile_metric == "Programming experience":
        st.markdown(
            f"Most {position} have programming experience of **{data.idxmax()}**."
        )


def job_bar_plot(df, position, industry):
    """
    Display bar plot to show the job responsibilities of given position title and industry
    """
    data = df.loc[position].sort_values()
    df = pd.DataFrame({"Job description": data.index, "Percentage": data.values * 100})
    fig = px.bar(
        df,
        x="Percentage",
        y="Job description",
        text=[str(round(val)) + "%" for val in df["Percentage"]],
        orientation="h",
        color="Percentage",
        width=650,
        height=450,
    )
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    fig.update_layout(
        title=dict(text=f"Job responsibilities of {position} in {str.lower(industry)}", x=0.5)
    )
    st.plotly_chart(fig)


def main():
    data = load_data()
    response = data[1:]
    questions = list(data.iloc[0])
    N_response = response.shape[0]
    N_questions = len(questions) - 1
    N_countries = len(response["Q3"].unique())
    job_title = [
        "Business Analyst",
        "Data Scientist",
        "Data Analyst",
        "Machine Learning Engineer",
        "DBA/Database Engineer",
        "Data Engineer",
        "Statistician",
        "Software Engineer",
        "Research Scientist",
    ]
    job_desc = [
        "Analyze data for business decisions",
        "Build data infrastructure",
        "Build ML Prototypes",
        "Build ML service for workflows",
        "Experiment/improve exisiting models",
        "Research to advance ML",
        "Other",
    ]
    metrics = ["Age", "Country", "Education", "Programming experience"]
    # Rename cols
    response.rename(
        columns={
            "Time from Start to Finish (seconds)": "Duration",
            "Q1": "Age",
            "Q2": "Gender",
            "Q3": "Country",
            "Q4": "Education",
            "Q5": "Position",
            "Q6": "Programming experience",
            "Q20": "Industry",
        },
        inplace=True,
    )
    # Remove outliers in duration (>1931 upper fence val)
    response["Duration"] = response["Duration"].astype(int)
    response = response[response["Duration"] <= 1931]

    # Replace the text to make it's clearer to display
    response.replace(
        "Some college/university study without earning a bachelor’s degree",
        "Some college study",
        inplace=True,
    )  # Replace the text to make it's clearer to display

    # Q24 asks people about their job duty
    Q24_question = [question for question in response.columns if "Q24" in question]
    Q24_question.remove("Q24_Part_7")  # remove none option in the answers
    job_activ = response.groupby("Position")[Q24_question].agg(
        lambda x: x.notnull().mean()
    )
    job_activ.columns = job_desc
    
    industries = [
        i for i in response.Industry.unique() if str(i) != "nan" and str(i) != "Other"
    ]
    industries.insert(0,"All industries")

    st.title("Data People Explorer")
    st.markdown(
        "Ever wondered about what the job titles are in data science and what the people working with data are like? \
        This dashboard takes answers from people working with data all over the world using the anual survey of Kaggle,\
        one of the largest data science community, and allows you to discover everything you are curious about data people."
    )
    st.header("Survey overview:")
    st.markdown(":clock1: Time window of the survey: 09/01/2021 - 10/04/2021")

    col1, spacer2, col2, spacer3, col3, spacer4 = st.columns([3.5, 1, 3.5, 1, 3.5, 1])
    with col1:
        st.markdown(":busts_in_silhouette: " + str(N_response) + " respondents")
    with col2:
        st.markdown(":question:" + "42 questions")
    with col3:
        st.markdown(":earth_americas: " + str(N_countries) + " countries/territories")
    with st.expander("Click here to view the raw data 👉"):
        st.dataframe(response)
    st.markdown("___")

    st.subheader("Select a job position you are interested to begin")
    spacer1, col1, col2, spacer2 = st.columns([0.2, 2.5, 4.4, 0.2])
    with col1:
        position = st.selectbox("I'm interested to know", job_title)

    spacer1, col1, col2, spacer2 = st.columns([0.2, 2.5, 4.4, 0.2])
    with col1:
        st.markdown(
            f"What do you want to know about {position}? Their age, educational level, country of residence or programming experience? Select below to find out!"
        )

        profile_metric = st.selectbox("Select a profile metric", metrics)

        st.text("")
        profile_desc(response, profile_metric, position)

    with col2:
        profile_plot(response, profile_metric, position)

    st.header("What do data people do?")

 
    spacer1, col1, spacer2, col2, spacer3 = st.columns((0.2, 2.5, 0.4, 4.4, 0.2))
    with col1:
        st.markdown(
            f"What do {position} do in their daily job? Select below to see their job responsibility in all industries or a certain industry."
        )

        industry = st.selectbox("", industries)

    with col2:

        if industry == "All industries":

            job_bar_plot(job_activ, position, industry)

        else:
            job_activ_indus = (
                response[response["Industry"] == industry]
                .groupby("Position")[Q24_question]
                .agg(lambda x: x.notnull().mean())
            )
            job_activ_indus.columns = job_desc
            job_bar_plot(job_activ_indus, position, industry)


if __name__ == "__main__":
    main()
