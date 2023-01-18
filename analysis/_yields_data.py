import pandas as _pd
import pandas_datareader as _pdr
import requests as _req
from bs4 import BeautifulSoup as _BeautifulSoup


    
def update_us_treasuries(start_date='2020-01-01', update_last_n_days=20):
    '''
    Fetch bond yields for US Treasuries from Fred service
    '''
    df = _pdr.fred.FredReader(['DTB3','DGS2','DGS5','DGS10','DGS30'],
                                start=start_date).read().ffill()
     

    df.columns = ['US_3M','US_2Y','US_5Y','US_10Y','US_30Y']
    df.index.name = ''


    if update_last_n_days is None:
        return df
    else:
        return df.tail(update_last_n_days)

    
def update_us_recession():
    '''
    Fetch NBER's US recession flags (daily)
    '''
    usrec = _pdr.fred.FredReader(['USRECD'], start='1954-01-04').read()
    
    usrec.columns = ['US_REC']
    usrec.index.name = ''

    return usrec


def update_german_bunds(start_date='2020-01-01', update_last_n_days=20):
    '''
    Fetch bond yields for German Federal securities from Bundesbank
    '''
    ge_dict = {
      "GE_2Y":"WT0202",
      "GE_5Y":"WT0505",
      "GE_10Y":"WT1010",
      "GE_30Y":"WT3030"
    }
    
    df = _pd.DataFrame()
    
    for i in ge_dict:
        url = "https://api.statistiken.bundesbank.de/rest/data/BBK01/{tsid}?".format(tsid=ge_dict[i])
        params = "detail=dataonly&startPeriod="+start_date
        
        response = _req.get(url+params)
        
        items = _BeautifulSoup(response.text,'lxml-xml').find_all('Obs')
        
        ts = []
        for el in items:
            try:
                ts.append( (
                           el.find('ObsDimension').get('value'),
                           eval(el.find('ObsValue').get('value')) 
                           )
                         )
            except:
                pass
        
        dt = _pd.DataFrame(ts,columns=['Dates', i]).set_index('Dates')
        dt.index = _pd.to_datetime(dt.index)

        df = _pd.concat([df,dt],axis=1)
        
    if update_last_n_days is None:
        return df
    else:
        return df.tail(update_last_n_days)



def update_euro_area_yields(update_last_n_days=None):
    '''
    Fetch euro area (changing composition) govt bond yields from the ECB
    '''

    dct = {  "EA_3M":  "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_3M", # Government bond, nominal, all issuers whose rating is triple A
             "EA_2Y":  "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y", # triple A
             "EA_5Y":  "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_5Y", # triple A
             "EA_10Y": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y", # triple A
             "EA_30Y": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_30Y" # triple A
        }
    
    df = _pd.DataFrame()
    
    
    def convert_to_pd(resp):

        # Do some weird extraction
        k = [i for i in resp['dataSets'][0]['series'].keys()][0]

        vals = resp['dataSets'][0]['series'][k]['observations']
        dates = resp['structure']['dimensions']['observation'][0]['values']

        dates = list(map(lambda x: x['id'] , dates)) # extract the value from the id key
        vals = list(map(lambda x: x[0] ,vals.values())) # extract the first element from the list

        dt = _pd.DataFrame(list(zip(dates,vals)),columns=['Date','Yield']).set_index('Date')
        dt.index = _pd.to_datetime(dt.index)

        return dt

    
    for i in dct:
        url = "https://sdw-wsrest.ecb.europa.eu/service/data/YC/{bid}?format=jsondata".format(bid=dct[i])
        response = _req.get(url).json()
        
        dt = convert_to_pd(response)
        dt.columns = [i]
        df = _pd.concat([df,dt],axis=1)
    
    if update_last_n_days is None:
        return df
    else:
        return df.tail(update_last_n_days)



def update_govt_yields(start_date='2020-01-01', update_last_n_days=20):

    # Update period
    df_us = update_us_treasuries(start_date, update_last_n_days)
    df_ge = update_german_bunds(start_date, update_last_n_days)

    # Update all
    df_ea = update_euro_area_yields()
    df_us_rec = update_us_recession()

    rates = _pd.concat([df_us,
                        df_ge,
                        df_ea,
                        df_us_rec],
                        axis=1)

    return rates