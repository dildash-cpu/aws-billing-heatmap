import streamlit as st
import boto3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Streamlit UI
st.title("AWS Cost Heatmap Visualization")

# User inputs AWS credentials
access_key = st.text_input("AWS Access Key", type="password")
secret_key = st.text_input("AWS Secret Key", type="password")
granularity = st.selectbox("Granularity : ", ['Monthly','Daily'])
# granularity = st.radio("Granularity : ", ['Monthly','Daily'])

# Select date range
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

# Function to fetch AWS cost data
# def get_aws_client():
#     return boto3.client(
#         'ce',
#         aws_access_key_id=access_key,
#         aws_secret_access_key=secret_key,
#         region_name='us-east-1'
#     )

def get_aws_client(access_key, secret_key, region='us-east-1'):
    """Creates an AWS client dynamically using provided credentials."""
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    return session.client('ce')  # AWS Cost Explorer client


def fetch_cost_data(client, granularity):
    response = client.get_cost_and_usage(
        TimePeriod={'Start': str(start_date), 'End': str(end_date)},
        Granularity=granularity.upper(),
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'},
                 {'Type': 'DIMENSION', 'Key': 'RECORD_TYPE'}]
    )
    return response

# Process and visualize data
if st.button("Generate Heatmap"):
    if access_key and secret_key:
        client = get_aws_client(access_key, secret_key)
        data = fetch_cost_data(client, granularity)

        # Process response into DataFrame
        # services = []
        costs = []
        for item in data['ResultsByTime']:
            period = item['TimePeriod']['Start']
            for group in item['Groups']:
                service = group['Keys'][0] # AWS Service Name 
                charge_type = group['Keys'][1] # Charge Type (Credit, Tax, Usage)
                cost = round(float(group['Metrics']['UnblendedCost']['Amount']),2)
                costs.append([period, service, charge_type, cost])
        
        df = pd.DataFrame(costs, columns=['Date', 'Service', 'Charge_Type','Cost'])
        df['Cost'] = df['Cost'].abs()
        df_tax = df[df['Charge_Type'] == 'Tax']
        df_usage = df[(df['Charge_Type'] == 'Usage')]
        df_usage_total = df_usage.groupby('Date')['Cost'].sum().reset_index()
        df_usage_total['Service'] = 'Total_Usage'
        df_usage_total['Charge_Type'] = 'Total_Usage'
        df_usage_total = df_usage_total[['Date','Service','Charge_Type','Cost']]
        final_df = pd.concat([df_usage, df_tax, df_usage_total], ignore_index = True)

        final_df['Date'] = pd.to_datetime(final_df['Date'])
        if granularity == 'Monthly':
            final_df['Date'] = final_df['Date'].dt.strftime('%Y-%m')
        elif granularity == 'Daily':
            final_df['Date'] = final_df['Date'].dt.strftime('%Y-%m-%d')

        # Create heatmap
        plt.figure(figsize=(14, 10))
        df_pivot = final_df.pivot_table(values="Cost", index="Service", columns='Date', aggfunc="sum")
        df_p = df_pivot.fillna(0).astype(float).round(2)
        sns.heatmap(df_p, annot=True, fmt=".2f", cmap="OrRd", linewidths=0.5)
        plt.xticks(rotation=45)
        plt.title('AWS Cost Heatmap by Service (Cost in $USD)')

        st.pyplot(plt)
    else:
        st.error("Please enter your AWS access key and secret key.")

