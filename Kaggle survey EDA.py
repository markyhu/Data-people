#!/usr/bin/env python
# coding: utf-8

#%%
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
pd.options.mode.chained_assignment = None


#%%


data = pd.read_csv('kaggle-survey-2021/kaggle_survey_2021_responses.csv',low_memory=False)
response = data[1:]
questions = list(survey_data.iloc[0])
N_response=response.shape[0]


#%%
response.rename(columns = {'Time from Start to Finish (seconds)':'Duration',
                            'Q1':'Age','Q2':'Gender','Q3':'Country',
                            'Q4':'Education','Q5':'Position','Q6':'Programming experience'}, 
                            inplace=True)
response['Duration'] = response['Duration'].astype(int)



# In[7]:




#Create dataframe of counts or percentage
def create_dataframe_of_counts(dataframe,column,rename_index,rename_column,return_percentages=False):
    '''
    A helper function to create a dataframe of either counts 
    or percentages, for a single multiple choice question.
    '''
    df = dataframe[column].value_counts().reset_index() 
    if return_percentages==True:
        df[column] = (df[column]*100)/(df[column].sum())
    df = pd.DataFrame(df) 
    df = df.rename({'index':rename_index, column:rename_column}, axis='columns')
    return df

def get_percent(df,col):
    '''
    return percent value given dataframe and column name
    '''
    counts = df[col].value_counts(dropna= False)
    percent = round(counts*100/df[col].count(),2)
    return percent

def plotly_bar_chart(response,title,y_axis_title,orientation):
    '''
    This function creates a bar chart.
    '''
    fig = px.bar(response,
             labels={"index": '',"value": y_axis_title},
             text=response.values,
             orientation=orientation,)
    fig.update_layout(showlegend=False,
                      title={'text': title+' in 2021',
                             'y':0.95,
                             'x':0.5,})
    fig.show()


# In[8]:


#Function to plot choropleth map 

def plotly_choropleth_map(df, column, title, max_value):
    '''
    This function creates a choropleth map.
    '''
    fig = px.choropleth(df, 
                    locations = 'country',  
                    color = column,
                    locationmode = 'country names', 
                    color_continuous_scale = 'viridis',
                    title = title,
                    range_color = [0, max_value])
    fig.update(layout=dict(title=dict(x=0.5)))
    fig.show()


# In[9]:


country_response_perc = create_dataframe_of_counts(survey_response,'Country','country','% of responses',return_percentages=True)


# In[10]:


country_response_perc


# ## Demographics
# ### Respondents distribution worldwide

# In[11]:


plotly_choropleth_map(country_response_perc,'% of responses', 
                      'Percentage of responses by countries in 2021', max_value=10)


# ### Age distribution

# In[12]:


age_percent = get_percent(survey_response,'Age').sort_index()
plotly_bar_chart(age_percent,'Age distribution on Kaggle','% of respondents', 'v')


# ## Skills in data science community
# ### Programming language

# In[13]:


Recom_language = get_percent(survey_response,'Q8')
plotly_bar_chart(Recom_language,'Most recommended language to learn by Kagglers', '% of responses','h')


# ### Business Intelligence tool

# In[14]:


BI_tool = get_percent(survey_response, 'Q35')


# In[15]:


plotly_bar_chart(BI_tool,'Most recommended business intelligence tool in 2011','% of respondents', 'h')


# ### Machine learning products

# In[16]:


ml_product_counts=[]
for i in range(1,10):
    ml_product_counts.append(survey_response[f'Q31_B_Part_{i}'].count())
ml_product_counts.append(survey_response['Q31_B_OTHER'].count())


ml_product_names=['Amazon SageMaker', 'Azure Machine Learning Studio', 'Google Cloud Vertex AI',
                  'DataRobot','Databricks','Dataiku','Alteryx', 'Rapidminer','None','Other']
ml_products =dict(zip(ml_product_names,ml_product_counts))

for key in ml_products:
    ml_products[key] = round(ml_products[key] * 100/N_response,2)

ml_products = pd.Series(ml_products).sort_values()
plotly_bar_chart(ml_products,'Most common ML products Kaggler want to learn', '% of respondents','h')


# ## Comparison between China and UK

# In[17]:


China_responses = survey_response[survey_response['Country']== 'China']
UK_responses = survey_response[survey_response['Country'] == 'United Kingdom of Great Britain and Northern Ireland']
China_positions = get_percent(China_responses,'Position')
plotly_bar_chart(China_positions,'Most common job titles for kagglers from China','% of respondents', 'h')

