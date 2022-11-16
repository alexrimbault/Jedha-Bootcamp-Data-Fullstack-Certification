import streamlit as st

import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# IMPORT DATASET
@st.cache(allow_output_mutation=True)
def delay():
  dataset = pd.read_excel("get_around_delay_analysis.xlsx")
  return dataset

dataset = delay()

# IMPORT VARIABLES

# Show number of unique cars
cars = len(dataset['car_id'].unique())
# Show number of rentals
rentals = len(dataset['rental_id'].unique())
# Show global mean delay at checkout in minutes
global_delay_mean = dataset.delay_at_checkout_in_minutes.mean()
# Show mean delay at checkout for mobile checkin type
data_mobile_type = dataset[dataset.checkin_type =='mobile']
delay_mobile_type = data_mobile_type.delay_at_checkout_in_minutes.mean()
# Show mean delay at checkout for connect checkin type
data_connect_type = dataset[dataset.checkin_type =='connect']
delay_connect_type = data_connect_type.delay_at_checkout_in_minutes.mean()
# Create a new dataframe with a delay at checkout between 12 hours
data_without_outliers = dataset[(dataset.delay_at_checkout_in_minutes > -720) & (dataset.delay_at_checkout_in_minutes < 720)]
# Create dataframe with ratio checkin type
data_ratio_chekin_type = (dataset['checkin_type'].value_counts(normalize=True)*100).rename_axis('state').reset_index(name='counts')
# Create new column to show if a car is late or not
dataset['late'] = dataset['delay_at_checkout_in_minutes'].apply(lambda x: 'late' if x > 0 else 'in time')
# Delete Nan values
data_clean = dataset[dataset["delay_at_checkout_in_minutes"].isna() == False]
# Show numbers of effective rentals in the dataset
effective_rentals = data_clean.shape[0]
# Create a dataframe with a ratio of late or in time rentals
data_late_ratio = (data_clean['late'].value_counts(normalize=True)*100).rename_axis('late').reset_index(name='counts')
# Create a dataframe with a ratio of canceled and ended rentals
data_ratio_state = (dataset['state'].value_counts(normalize=True)*100).rename_axis('state').reset_index(name='counts')
# Create datafreme with only canceled 
data_canceled = dataset[dataset["state"] == "canceled"]
# Create column with nan = > 720 minutes
data_canceled['delta'] = data_canceled.time_delta_with_previous_rental_in_minutes.isna().apply(lambda x: x if x == False else '> 720 minutes')
# Create a dataframe with a ratio delta for canceled rentals
data_ratio_delta_canceled_all = (data_canceled.delta.value_counts(normalize=True)*100).rename_axis('delta').reset_index(name='counts')
# Create a dataframe with a ratio delta for canceled rentals with only < 12h delta time
data_ratio_delta_canceled = (data_canceled.time_delta_with_previous_rental_in_minutes.value_counts(normalize=True)*100).rename_axis('delta').reset_index(name='counts')
# Create dataframe with only rentals with time delta with previous < 12 hours
data_canceled_clean = data_canceled[~data_canceled.previous_ended_rental_id.isnull()]
# Create a list of the column time delta
previous_rental = data_canceled_clean["previous_ended_rental_id"]
# Create dataframe with previous rentals in this list
data_previous_rental = dataset[dataset["rental_id"].isin(previous_rental)]
### Create a merged dataframe with the previous and next rental
merged_data = data_previous_rental.merge(dataset, how='inner', left_on='rental_id', right_on='previous_ended_rental_id')
# Drop useless columns
merged_data.drop(['state_x', 'previous_ended_rental_id_x','previous_ended_rental_id_y', 'time_delta_with_previous_rental_in_minutes_x', 'car_id_y', 'delay_at_checkout_in_minutes_y'], axis=1, inplace=True)
# Ratio of checkin type for cancelation
data_canceled_ratio_chekin = (merged_data['checkin_type_x'].value_counts(normalize=True)*100).rename_axis('checkin').reset_index(name='counts')
# Ratio of lateness for cancelation
data_canceled_ratio_lateness = (merged_data['late_x'].value_counts(normalize=True)*100).rename_axis('lateness').reset_index(name='counts')
# Only late cars
data_canceled_late = merged_data[merged_data.delay_at_checkout_in_minutes_x > 0]
# Create treshold
threshold_delay = data_canceled_late.delay_at_checkout_in_minutes_x.quantile(0.75)
# Create dataframe with only previous rental
data_previous_rental = dataset[dataset.previous_ended_rental_id.isnull()]
# Make a list of the column
previous_rental = data_previous_rental["previous_ended_rental_id"]
# Create dataframe with previous rental found 
data_previous_rental = dataset[dataset["rental_id"].isin(previous_rental)]
# Create a merged dataframe with the previous and next rental & drop useless columns
merged_data = data_previous_rental.merge(dataset, how='inner', left_on='rental_id', right_on='previous_ended_rental_id')
merged_data.drop(['state_x', 'previous_ended_rental_id_x','previous_ended_rental_id_y', 'time_delta_with_previous_rental_in_minutes_x', 'car_id_y', 'delay_at_checkout_in_minutes_y'], axis=1, inplace=True)
# Create a copy of the dataframe with only ended
data_merged_ended = merged_data[merged_data["state_y"] == "ended"].copy()
# Select rentals > to the treshold
data_ended_treshold = data_merged_ended[data_merged_ended["time_delta_with_previous_rental_in_minutes_y"] >= threshold_delay]
# Define how many rentals are affected by treshold
rentals_affected = len(data_merged_ended)-len(data_ended_treshold)



def main():
    pages = {
        'EDA': EDA,
        }

    if "page" not in st.session_state:
        st.session_state.update({
        # Default page
        'page': 'EDA'
        })

    with st.sidebar:
        page = st.selectbox("", tuple(pages.keys()))

    pages[page]()

def EDA():
    st.header('GETAROUND EDA')

    # Dataset basic figures
    st.subheader('Quick figures')
    # Show number of cars
    st.write(f'There are {cars} cars in the dataset')
    # Show number of rentals
    st.write(f'There are {rentals} rentals in the dataset')
    # Show mean global delay at checkout
    st.write(f'The average delay at checkout is {round(global_delay_mean)} minutes')


    # Display delay at checkout in minutes distribution within 12 hours range
    fig = px.histogram(data_without_outliers, x="delay_at_checkout_in_minutes",
                      title = 'Rentals distribution for a delay at checkout in minutes within 12 hours range',
                      color = 'checkin_type',
                      barmode ='group',
                      width= 1000,
                      height = 600
                      ) 
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      xaxis_title = '',
                      yaxis_title = '',
                      template = 'plotly_dark'
                      )
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                      'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
                      )       
    st.plotly_chart(fig)
    st.markdown('The majority of the delay within checkout distribution is between -200 and 200 minutes')

    # Show delay at checkout mean for mobile checkin 
    st.write(f'The average delay at checkout for mobile checkin type is {round(delay_mobile_type)} minutes')
    # Show delay at checkout mean for connect checkin
    st.write(f'The average delay at checkout for connect checkin type is {round(delay_connect_type)} minutes')
    st.markdown('The connect checkin tend to be earlier, we can suppose that the connect type is full digital and create less frictions in the process')

    # Display ratio of checkin type rentals
    fig = px.pie(data_ratio_chekin_type,
                values='counts',
                names='state', 
                width= 1000,
                title='Proportion by type of checkin'
                )
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark'
                      )    
    st.plotly_chart(fig)
    st.markdown('The connect type of checkin represents 20% of the rentals, we can suppose that the reason behind is correlated to trust as it is a full digital type of checkin and therefore there is less cars on the market with this type of checkin available')

    st.subheader('Analysis regarding only the rentals in range with an acceptable delay')
    st.write(f'There are {effective_rentals} effective rentals in the dataset')

    # Piechart for late or in time cars for effective rentals
    fig = px.pie(data_late_ratio,
                values='counts',
                names='late', 
                color ='late',
                title='Proportion of late or in time cars for the checkout',
                width= 1000,
                color_discrete_map={'late':'orange',
                                    'in time':'green'}
                )
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      template = 'plotly_dark' )                
    st.plotly_chart(fig)

    # Histogram for delay at checkout by checkin type
    fig = px.histogram(data_clean, x="late",
                      title = 'Proportion of late or in time cars for the checkout between checkin type',
                      color = 'checkin_type',
                      histnorm= 'percent',
                      barmode ='group',
                      width= 1000,
                      height = 600,
                      text_auto = True
                      )
    fig.update_traces(textposition = 'outside', textfont_size = 15)
    fig.update_layout(title_x = 0.5,
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      yaxis = {'visible': False}, 
                      xaxis = {'visible': True}, 
                      xaxis_title = '',
                      template = 'plotly_dark',
                      )
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                      'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
                      )                                  
    st.plotly_chart(fig)
    st.write(' The difference can probably be explained by the fact that there is a need for physical interaction in the case of a mobile checkin type.')

    # Piechart proporion for state of the cars
    fig = px.pie(data_ratio_state,
                values='counts',
                names='state',
                color = 'state',
                width= 1000,
                title='Proportion of ended vs canceled rentals',
                color_discrete_map={'ended':'green',
                                    'canceled':'orange'}
                )
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark'
                      )    
    st.plotly_chart(fig)

    # Histogram for delay at checkout by checkin type
    fig = px.histogram(dataset, x = "state",
                      title = 'Proportion of canceled or ended rentals between checkin type',
                      color = 'checkin_type',
                      barmode ='group',
                      histnorm = 'percent',
                      width= 1000,
                      height = 600,
                      text_auto = True
                      )       
    fig.update_traces(textposition = 'outside', textfont_size = 15)
    fig.update_layout(title_x = 0.5,
                      margin=dict(l=50,r=50,b=50,t=50,pad=4),
                      yaxis = {'visible': False}, 
                      xaxis = {'visible': True}, 
                      xaxis_title = '',
                      template = 'plotly_dark'
                      )
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                      'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
                      )                    
    fig.update_xaxes(tickfont_size=15)                     
    st.plotly_chart(fig)

    st.subheader('Analysis about only the canceled rentals')

    st.write(f'There are {len(data_canceled)} canceled rentals')

    # Piechart proporion for delta ratio canceled cars
    fig = px.pie(data_ratio_delta_canceled_all,
                values='counts',
                names='delta',
                color = 'delta',
                color_discrete_map={'> 720 minutes':'green','false':'yellow'},
                width= 1000,
                title='Proportion of canceled rentals superior to 12 hours time delta with previous rental',
                )
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark'
                      )    
    st.plotly_chart(fig)

    # Piechart proportion for canceled rentals with only time delta under 12 hours rentals
    fig = px.pie(data_ratio_delta_canceled,
                values='counts',
                names='delta',
                color = 'delta',
                width= 1000,
                title='Proportion of canceled rentals with time delta under 12 hours',
                color_discrete_sequence=px.colors.sequential.RdBu
                )
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark',
                      legend=dict(yanchor= "bottom",y = -0.5, xanchor="right", x=0.5, orientation = "h")
                      )    
    st.plotly_chart(fig)
    st.write('Only 7% of canceled rentals are under 12 hours of time delta with previous rentals')
    st.write('50% of under 12 hours canceled rentals are for 0, 60, 600, 120 and 210 minutes time delta with previous rental')

    # Piechart proportion for checkin type influence on cancelation
    fig = px.pie(data_canceled_ratio_chekin,
                values='counts',
                names='checkin', 
                width= 1000,
                title='Proportion of cancelations by rentals checkin type'
                )
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark'
                      )    
    st.plotly_chart(fig)
    st.write('60% of cancelation is for connect cars, easier to cancel with a full digital process')

    # Piechart proporion for lateness influence on cancelation
    fig = px.pie(data_canceled_ratio_lateness,
                values='counts',
                names='lateness', 
                width= 1000,
                title='Proportion of in time and late previous rentals for canceled rentals',
                color_discrete_map={'late':'orange',
                                    'in time':'green'}
                )
    fig.update_traces(textposition = 'outside', textfont_size = 15)             
    fig.update_layout(title_x = 0.5, 
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark'
                      )    
    st.plotly_chart(fig)
    st.write('The lateness seems to have no influence in cancelation')

    st.subheader('Threshold setting')

    # Display delay at checkout in minutes distribution
    fig = px.histogram(data_canceled_late, x="delay_at_checkout_in_minutes_x",
                      title = 'Number of late rentals resulting in cancelation',
                      nbins= 250
                      ) 
    fig.update_layout(title_x = 0.5,
                      width = 1000,
                      margin=dict(l=50,r=50,b=50,t=50,pad=4), 
                      template = 'plotly_dark',
                      yaxis_title = '',
                      xaxis_title = 'Delay at checkout'
                      )  
    fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                      'paper_bgcolor': 'rgba(0, 0, 0, 0)'}
                      )                       
    fig.add_vline(x = threshold_delay,
                  line_color = 'blue',
                  annotation_text= 'Threshold'
                  )              
    st.plotly_chart(fig)
    st.write(f'The chosen threshold is {threshold_delay} minutes. It stops 75% of cancelation by lateness')
    
    st.subheader('Conclusion')
    
    st.subheader('Regarding the scope')
    st.write('The connect type represents almost a quarter of the total bookings which is not negligible and therefore we need to take this type of checkin in consideration. Charts show that both checkin type are likely the same regarding cancelations and delays, therefore threshold should concern both types.')
    
    st.subheader('About the threshold')
    st.write('We can see on the graph showing the numbers of cancelations that are due to late rentals that with a threshold set at 142 minutes we will be able to cover 75% of the regular delays. We should keep in mind too that the higher the threshold is the more restrictive it is for the owners to chain rents and reduce therefore the chance for users to rent those vehicles.')
    

if __name__ == "__main__":
    main()