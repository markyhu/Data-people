from multiprocessing.sharedctypes import Value
import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title='Data people explorer',layout='wide')

path = './data/kaggle_survey_2021_responses.csv'

@st.cache
def load_data():
    data = pd.read_csv(path,low_memory=False)
    return data
    
def get_percent(df,col):
    '''
    return percent value given dataframe and column name
    '''
    counts = df[col].value_counts(dropna= False)
    percent = round(counts*100/df[col].count(),2)
    return percent

def profile_plot(df,profile_metric,position):
    '''
    Plot pie chart or map according to profile metric
    '''
    if profile_metric != 'Country':

        grouped_df=df.groupby(['Position',profile_metric]).size().unstack().fillna(0)
        vals = grouped_df.loc[position].values
        
        fig = go.Figure(go.Pie(labels=grouped_df.columns, values=vals, 
                                 hole=.3,pull= (vals == max(vals))*0.2))
        fig.update_layout(width =600,height =500)
        if profile_metric == 'Age':
            fig.update_layout(title = dict(text=f'Age distribution of {position}',x=.5))
        if profile_metric == 'Education':
            fig.update_layout(title = dict(text=f'Education level of {position}',x=.5))
        if profile_metric =='Programming experience':
            fig.update_layout(title = dict(text=f'Programming experience of {position}',x=.5))
        st.plotly_chart(fig)
    else:
        grouped_df = df[df['Position'] == position]['Country'].value_counts().reset_index()
        grouped_df['Country'] = (grouped_df['Country']*100)/(grouped_df['Country'].sum())
        grouped_df.rename(columns = {'index':'country','Country':'percentage'},inplace = True)
        map = px.choropleth(grouped_df, 
                    locations = grouped_df.country,  
                    color = grouped_df.percentage,
                    locationmode = 'country names', 
                    color_continuous_scale = 'viridis',
                    title = f'Country residence of {position}',
                    range_color = [0, 10])
        map.update(layout=dict(title=dict(x=0.5)))
        st.plotly_chart(map)


def profile_desc(df,profile_metric,position):
    
    data = df[df['Position'] == position][profile_metric].value_counts()
    if profile_metric =='Age':
        st.markdown(f'Most {position} aged **{data.idxmax()}**.' )
    if profile_metric =='Country':
        st.markdown(f'Most {position} are from **{data.idxmax()}**.' )
    if profile_metric =='Education':
        st.markdown(f'Most {position} have an education of or plan to attain an education of **{data.idxmax()}**.')
    if profile_metric =='Programming experience':
        st.markdown(f'Most {position} have programming experience of **{data.idxmax()}**.')


def job_bar_plot(df,position,industry,all_industry):
    data = df.loc[position].sort_values()
    df = pd.DataFrame({'Job description':data.index,'Percentage':data.values*100})
    fig =px.bar(df,x='Percentage',y= 'Job description',
                text = [str(round(val))+'%' for val in df['Percentage']],
                orientation='h',color = 'Percentage',width=650,height=450)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    #fig.update_yaxes(tickfont_family="Arial Black")
    if all_industry == True:
        fig.update_layout(title = dict(text=f'Job responsibilities of {position}',x=.5))
    else:
        fig.update_layout(title = dict(text=f'Job responsibilities of {position} in {industry}',x=.5))

    # fig = go.Figure(data=[go.Bar(x=data.values*100,y= data.index,
    #                         text =['{:.0%}'.format(val) for val in data.values],
    #                         orientation=orientation)],layout=go.Layout(plot_bgcolor='rgba(0,0,0,0)',color = data.values*100))

    st.plotly_chart(fig)


def main():
    data = load_data()
    response = data[1:]
    questions = list(data.iloc[0])

#Rename cols
    response.rename(columns = {'Time from Start to Finish (seconds)':'Duration',
                            'Q1':'Age','Q2':'Gender','Q3':'Country',
                            'Q4':'Education','Q5':'Position','Q6':'Programming experience','Q20':'Industry'}, 
                           inplace=True)
#Remove outliers in duration (>1931 upper fence val)
    response['Duration'] = response['Duration'].astype(int)
    response = response[response['Duration'] <=1931]
    response.replace('Some college/university study without earning a bachelor’s degree',
                    'Some college study',inplace=True) #Rename to make it's clearer to display
    N_response=response.shape[0]
    N_questions = len(questions)-1
    N_countries = len(response['Country'].unique())
    
    st.title('Data People Explorer')

    st.header('Survey overview:')
    st.markdown(':clock1: Time window of the survey: 09/01/2021 - 10/04/2021')
    col1,col2,col3 = st.columns(3)
    with col1:
        st.markdown(':busts_in_silhouette: ' + str(N_response)+' respondents')
    with col2:
        st.markdown(':question:' + '42 questions')
    with col3:
        st.markdown(':earth_americas: ' + str(N_countries) + ' countries/territories')
    with st.expander('Click here to view the raw data 👉'):
        st.dataframe(response)

    st.markdown('___')
    metrics = ['Age','Country','Education','Programming experience']
    Q24_question = [question for question in response.columns if 'Q24' in question]
    Q24_question.remove('Q24_Part_7') #remove none option
    job_activ = response.groupby('Position')[Q24_question].agg(lambda x : x.notnull().mean())
    job_desc =  ["Analyze data for business decisions", 
                    "Build data infrastructure", 
                    "Build ML Prototypes",
                    "Build ML service for workflows",
                    "Experiment/improve exisiting models",
                    "Research to advance ML",
                    "Other"]
    job_activ.columns = job_desc

    job_title=['Business Analyst','Data Scientist', 'Data Analyst', 'Machine Learning Engineer',
            'DBA/Database Engineer','Data Engineer','Statistician',
            'Software Engineer','Research Scientist']


    st.sidebar.text('')
    st.sidebar.text('')
    st.sidebar.text('')
    st.sidebar.markdown('**Select a job position you are interested to begin**')
    position = st.sidebar.selectbox("Choose a job title",job_title)

    st.header('Data people profile')
    
    spacer1,col1, col2,spacer2 = st.columns([.2,2.5,4.4,.2])
    with col1:
        st.markdown(f'What do you want to know about {position}? Their age, educational level, country of residence or programming experience? Select below to find out!')
        
        profile_metric = st.selectbox('Select a profile metric',metrics)
        
        st.text('')
        profile_desc(response,profile_metric,position)
    
    with col2:
        profile_plot(response,profile_metric,position)


    
    st.header('What do data people do?')

    industries = [i for i in response.Industry.unique() if str(i) != 'nan' and str(i) != 'Other']
    spacer1, col1, spacer2, col2, spacer3  = st.columns((.2, 2.5,.4,  4.4, .2))
    with col1:
        st.markdown(f'What do {position} do in their daily job? Select below to see their job responsibility in all industries or a certain industry.')
        all_industry = st.checkbox(f'View in all industries',value=True)
        industry = st.selectbox('Or pick an industry 👇', industries)
    with col2:

        if all_industry:
        
            job_bar_plot(job_activ,position,industry,all_industry = all_industry)
        
    
        else:
            job_activ_indus=response[response['Industry']==industry]\
                .groupby('Position')[Q24_question].agg(lambda x : x.notnull().mean())
            job_activ_indus.columns = job_desc
            job_bar_plot(job_activ_indus,position,industry,all_industry= all_industry)


if __name__ == '__main__':
    main()