#!/usr/bin/env python
# coding: utf-8

# In[41]:


import numpy as np
import pandas as pd


# In[42]:


initial_info = pd.read_excel("/Users/alexrogers823/Documents/Student Loan Payment Schedule.xlsx", sheet_name="Initial Information")
balances_info = pd.read_excel("/Users/alexrogers823/Documents/Student Loan Payment Schedule.xlsx", sheet_name="Projected Balances")


# In[43]:


initial_index = initial_info["Student Loan Repayment: Game Plan"][2:]
initial_headers = initial_info.loc[1]


# In[44]:


initial_df = pd.DataFrame(initial_info)[2:]


# In[45]:


initial_df.rename(index=initial_index, columns=initial_headers, inplace=True)


# In[46]:


initial_df.drop(columns="Group", inplace=True)


# In[47]:


balances_df = pd.DataFrame(balances_info)[1:]


# In[48]:


balances_headers =  balances_info.loc[0]


# In[49]:


balances_df.rename(columns=balances_headers, inplace=True)


# In[50]:


t_period_one = [['1', '12', '2016', '122016', '29116.20']]
t_period_two = [['2', '1', '2017', '012017', '28108.40']]

trend_periods = balances_df["Pay Periods"]
trend_month = balances_df["Month"]
trend_year = balances_df["Month"]
trend_monthyear = balances_df["Month"]
trend_actuals = balances_df["Actual Balance (Manual)"]

align_row_index = lambda x: [trend_periods[x], trend_month[x].month, trend_year[x].year, trend_monthyear[x].strftime('%m%Y'), trend_actuals[x]]
other_periods = [align_row_index(x) for x in range(1, len(trend_periods))]
trendline_data = np.concatenate((t_period_one, t_period_two, other_periods))


# In[51]:


trendline_df = pd.DataFrame(data=trendline_data, index=range(0, len(trendline_data)), columns=["Period", "Month", "Year", "Month/Year", "Actual Balance"])


# In[52]:


trendline_condition = trendline_df["Actual Balance"] != 'nan'

filtered_trendline = trendline_df[trendline_condition]

# Grabbing last known actual balance
last_known_balance = filtered_trendline.tail(1)["Actual Balance"]


# In[53]:


start_balance = float(last_known_balance.to_numpy()[0])


# In[54]:


monthly_payoff = initial_df.loc["Total"][8]
arr_of_forecasts = []


# In[55]:


def forecast_balances(bal = start_balance):
    weighted_breakdown = initial_df["Weighted Balance"] * bal
    rec_pay = initial_df["Rec. Pay %"] * monthly_payoff
    interest = initial_df["Projected Interest %"] + 1

    proj_balance = (weighted_breakdown - rec_pay) *  interest
    next_balance = proj_balance.sum()
    if next_balance > 0:
        arr_of_forecasts.append(next_balance)
        forecast_balances(bal = arr_of_forecasts[-1])


# In[56]:


forecast_balances()
actuals = np.array(filtered_trendline["Actual Balance"])
full_trendline_raw = np.array([*actuals, *arr_of_forecasts])
months_forecasted = len(full_trendline_raw)
trend_length = len(trendline_data)

full_trendline = np.full((trend_length), 0.0)
full_trendline[:months_forecasted] = full_trendline_raw


# In[57]:


trendline_df.insert(5, "Full Trendline", full_trendline)


# In[58]:


a_f = np.where(trendline_condition, 'A', 'F')


# In[59]:


find_delta = lambda x: trendline_df["Full Trendline"][x-1] - trendline_df["Full Trendline"][x]
payment_delta_raw = np.array([find_delta(x) for x in range(1, len(trendline_df["Full Trendline"]))])
# payment_delta_raw.insert(0, 0.00)
payment_delta_raw = np.insert(payment_delta_raw, 0, 0.00)

payment_delta = np.where(payment_delta_raw > 0.1, payment_delta_raw, "N/A")


# In[60]:


trendline_df.insert(6, "Delta Between Last Payment", payment_delta)
trendline_df.insert(7, "Actual/Forecast", a_f)


# In[67]:


trendline_df.to_csv("/Users/alexrogers823/Documents/Python_Projects/Student_Loans/Dataframes/trendline.csv", index=False)
initial_df.to_csv("/Users/alexrogers823/Documents/Python_Projects/Student_Loans/Dataframes/groups.csv", index_label="Group")

