import requests
import pandas as pd
from datetime import datetime, timedelta

def get_comm_prices(symbol, start, end):
  # print(symbol, start, end)
  durl = "https://www.mcxindia.com/backpage.aspx/GetDateWiseBhavCopy"
  dheaders = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.mcxindia.com/market-data/bhavcopy",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"}
      
  start = datetime.strptime(start, '%Y-%m-%d')
  end = datetime.strptime(end, '%Y-%m-%d')
  new_df = pd.DataFrame()
  while(start<=end):
    try:
      date = str(start.year)+('0'+str(start.month) if start.month<10 else str(start.month))+('0'+str(start.day) if start.day<10 else str(start.day))
      # print(date)
      dpayload = {'Date': date,'InstrumentName':'FUTCOM'}

      data = requests.post(url = durl, headers = dheaders, json = dpayload).json()
      data = pd.DataFrame(data['d']['Data'])
    except:
      pass
    try:
      data = data.drop(['__type', 'PreviousClose', 'Value', 'OpenInterest', 'InstrumentName', 'StrikePrice', 'OptionType'], axis=1)
      data['Symbol'] = data['Symbol'].str.strip()
      new = data.loc[data['Symbol'] == symbol]
      new_df = pd.concat([new_df, new], ignore_index=True) 
    except:
      pass
    start += timedelta(days=1)
  # print(new_df)

  # find nearest expiry dates
  final_df = pd.DataFrame()
  data = new_df
  try:
    data["Date"] = pd.to_datetime(data["Date"])
    data["ExpiryDate"] = pd.to_datetime(data["ExpiryDate"])
  except:
    pass

  sorted_unique_dates = sorted(set(data["Date"]))

  for i in sorted_unique_dates:
      temp_df = data[data["Date"] == i]
      # print(temp_df)
      min_exp_deets = temp_df[
          (
              temp_df["ExpiryDate"]
              == (i + min(abs(temp_df["ExpiryDate"] - temp_df["Date"])))
          )
          & (temp_df["Date"] == i)
      ]
      final_df = pd.concat([final_df, min_exp_deets], ignore_index=True)

  # final_df = final_df.drop_duplicates(subset=["Date"], ignore_index=True)
  return final_df.set_index("Date")

def get_comm_list():
  durl = "https://www.mcxindia.com/backpage.aspx/GetDateWiseBhavCopy"
  dheaders = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.mcxindia.com/market-data/bhavcopy",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"}
  date = (datetime.today() - timedelta(days=5))
  date = date.strftime('%Y-%m-%d')
  
  # print(date)
  date = datetime.strptime(date, '%Y-%m-%d')
  date = str(date.year)+('0'+str(date.month) if date.month<10 else str(date.month))+('0'+str(date.day) if date.day<10 else str(date.day))
  dpayload = {'Date': date,'InstrumentName':'FUTCOM'}
  data = requests.post(url = durl, headers = dheaders, json = dpayload).json()
  data = [i.strip()+" FUTCOM" for i in pd.DataFrame(data['d']['Data'])['Symbol'].unique()]
  return data

# print(get_comm_list())
# data = get_comm_prices('ALUMINI', '2023-03-01', '2023-04-15')
# print(data)
# data