import streamlit as st
import pandas as pd
import requests

# --- 1. CONFIGURATION (Same as before) ---
CLIENT_ID = st.secrets["ZOHO_CLIENT_ID"]
CLIENT_SECRET = st.secrets["ZOHO_CLIENT_SECRET"]
ORG_ID = st.secrets["ZOHO_ORG_ID"]
DATACENTER_URL = 'https://accounts.zoho.in' 
API_BASE_URL = 'https://www.zohoapis.in/crm/v8'

# --- 2. THE LOGIC (The "Engine") ---
def get_access_token():
    url = f"{DATACENTER_URL}/oauth/v2/token"
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials',
        'scope': 'ZohoCRM.modules.ALL',
        'soid': f'ZohoCRM.{ORG_ID}'
    }
    response = requests.post(url, params=params)
    return response.json().get('access_token')

def fetch_deals(token):
    url = f"{API_BASE_URL}/Deals"
    headers = {'Authorization': f'Zoho-oauthtoken {token}'}
    params = {'fields': 'Deal_Name,Amount,Stage,Closing_Date'}
    response = requests.get(url, headers=headers, params=params)
    print("DEBUG RAW RESPONSE:", response.json())
    return response.json().get('data', [])

# --- 3. THE DASHBOARD (The "Visuals") ---
st.set_page_config(page_title="Zoho CRM Dashboard", page_icon="📈")
st.title("🚀 Zoho CRM Live Sales Tracker")

if st.button('🔄 Refresh Live Data'):
    try:
        token = get_access_token()
        data = fetch_deals(token)
        
        if data:
            df = pd.DataFrame(data)
            # Fill empty amounts with 0 so the math works
            df['Amount'] = df['Amount'].fillna(0)

            # --- METRICS ---
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Deals", len(df))
            col2.metric("Pipeline Value", f"${df['Amount'].sum():,.2f}")
            col3.metric("Avg Deal Size", f"${df['Amount'].mean():,.2f}")

            # --- CHARTS ---
            st.subheader("Sales Pipeline by Stage")
            chart_data = df.groupby('Stage')['Amount'].sum().reset_index()
            st.bar_chart(data=chart_data, x='Stage', y='Amount')

            # --- DATA TABLE ---
            st.subheader("Detailed Deal List")
            st.dataframe(df[['Deal_Name', 'Amount', 'Stage', 'Closing_Date']], use_container_width=True)
            
        else:
            st.warning("Connected to Zoho, but no deals were found!")
            
    except Exception as e:
        st.error(f"Connection Error: {e}")