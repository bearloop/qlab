import pandas as _pd
import requests as _requests
from bs4 import BeautifulSoup as _bs

# ---------------------------------------------------------------------------------------------------
# Constants
_summary_columns = ['ISIN','AUM','ExpRatio','Currency','Domicile','Launch']

_sectors = ['Technology','Financial Services','Healthcare','Consumer Cyclical','Industrials',
              'Communication Services','Consumer Defensive','Basic Materials','Energy']

_non_equities = ['Non-equities']

_unidentified = ['UnidentifiedSectors','UnidentifiedSecurities']

_top_10 = ['Top-10']

# ---------------------------------------------------------------------------------------------------
def ft_aggregate(etfs_list, how_securities=_top_10[0]):
    """ """
    cols = _summary_columns+_sectors+_non_equities+_unidentified+_top_10
    
    df = _pd.DataFrame(index = cols)
    
    ln = len(etfs_list)
    
    for count, etf in enumerate(etfs_list):
        
        try:
            x1 = ft_summary(etf).fillna('-')
            x2 = ft_sectors(etf).fillna(0).astype(float).round(3).astype(str)
            x3 = ft_securities(etf).fillna(0).astype(float).round(3).astype(str)

            if how_securities == _top_10[0]:
                x3 = x3[_top_10+[_unidentified[1]]]

            sup = _pd.concat([x1,x2,x3],axis=1).T
            df = _pd.concat([df,sup],axis=1)

            print(str(count+1) + ' out of ' + str(ln) + ' done', end = "\r")
         
        except Exception as e:
            print(etf + ': ' + e.args)
        
    return df.fillna('-1')


# ---------------------------------------------------------------------------------------------------
def ft_summary(etf):
    """ """
    
    try:
        res = _requests.get("https://markets.ft.com/data/etfs/tearsheet/summary?s={}".format(etf))
        table = _bs(res.content, 'html.parser').find_all('tr')

        # Assign data
        ft_data = _pd.DataFrame(index=[etf],
                           columns=_summary_columns)
        
        ft_data.loc[etf]['ISIN'] = _parse_table(table,'ISIN')
        ft_data.loc[etf]['AUM'] = _parse_table(table,'Fund size')
        
        try:
            ft_data.loc[etf]['ExpRatio'] = _transform_exp(_parse_table(table,'Ongoing charge'))
        except:
            ft_data.loc[etf]['ExpRatio'] = _transform_exp(_parse_table(table,'Net expense ratio'))
            
        ft_data.loc[etf]['Currency'] = _parse_table(table,'Price currency')
        ft_data.loc[etf]['Domicile'] = _parse_table(table,'Domicile')
        ft_data.loc[etf]['Launch'] = _parse_table(table,'Launch date')
        
        return ft_data

    except Exception as e:
        print(e.args)

# ---------------------------------------------------------------------------------------------------
def ft_sectors(etf):
    """ """
    
    try:
        res = _requests.get('https://markets.ft.com/data/etfs/tearsheet/holdings?s={}'.format(etf))
        soup = _bs(res.content, 'html.parser').find_all('tr')

        sup_df = _pd.DataFrame([[weight.text for weight in item.find_all('td')] for item in soup]
                             ).dropna(how='all').set_index([0])

        return _transform_sectors(sup_df, col_name = etf).T
    
    except Exception as e:
        print(e.args)

# ---------------------------------------------------------------------------------------------------
def ft_securities(etf):
    """ """
    
    try:
        res = _requests.get('https://markets.ft.com/data/etfs/tearsheet/holdings?s={}'.format(etf))
        soup = _bs(res.content, 'html.parser').find_all('tr')

        sup_df = _pd.DataFrame([[weight.text for weight in item.find_all('td')] for item in soup]
                             ).dropna(how='all').set_index([0])
        
        dt = _transform_securities(sup_df, col_name=etf)
        
        # Calc top-10 sum
        dt.loc[_top_10[0]] = dt.drop([_unidentified[1]]).sum()
        
        return dt.T
    
    except Exception as e:
        print(e.args)

# ---------------------------------------------------------------------------------------------------
def _parse_table(table, filtered_value):
    """ """
    
    try:
        
        result = list(filter(lambda x: list(filter(lambda t: t.text.strip() == filtered_value, 
                                                       x.find_all('th'))),table))

        if filtered_value in ['Fund size']:    
            aum_size = result[0].find_all('td')[0].text.split(" ")[0]
            curr = result[0].find_all('td')[0].text.split(" ")[1][:3]
            result = curr+' '+_transform_aum(aum_size)

        elif filtered_value in ['ISIN','Price currency','Domicile','Ongoing charge','Net expense ratio']:
            result = result[0].find_all('td')[0].text.split(" ")[0]

        elif filtered_value in ['Launch date']:
            result = result[0].find_all('td')[0].text

        else:
            print(filtered_value + ' -- not found.')
            result = '-1'
        return result

    except Exception as e:
        print(e.args)

# ---------------------------------------------------------------------------------------------------
def _transform_aum(string_val):
    """ """
    aum = "<0.05bn"
    if string_val[-1:] == "m":
        num = float(string_val[:-1])/1000
        if num >=  0.05:
            aum = str(round(num,2))+"bn"
    else: 
        aum = string_val
    return aum

# ---------------------------------------------------------------------------------------------------
def _transform_exp(string_val):
    """ """
    return float(string_val.split("%")[0])

# ---------------------------------------------------------------------------------------------------
def _transform_sectors(df, col_name):
    """ """
    
    sectors = _sectors
    
    try:
        # Filter df index for sectors
        sec = list(filter(lambda x: x in list(df.index), sectors))
        
        if not sec:
            raise('No sectors found.')
            
        # Transform sectors from string to float and add "Unidentified"
        weights_list = [float(i.split('%')[0]) for i in df.loc[sec][1]]

        if  sum(weights_list) <=100:
            weights_list.append(round(100-sum(weights_list),3))
            sec.append(_unidentified[0])

        return _pd.DataFrame(index = sec, data = weights_list, columns = [col_name])
    
    except:
        return _pd.DataFrame(index=_non_equities, data = [100], columns = [col_name])

# ---------------------------------------------------------------------------------------------------
def _transform_securities(df, col_name='Weights'):
    """ """
    
    df = df.loc['--':,:][2].dropna().drop('--')
    sec = list(df.index)
    
    # Transform securities from string to float and add "Unidentified"
    weights_list = [float(i.split('%')[0]) for i in df]
    if  sum(weights_list) <=100:
        weights_list.append(round(100-sum(weights_list),3))
        sec.append(_unidentified[1])
    
    return _pd.DataFrame(index = sec, data = weights_list, columns = [col_name])

# ---------------------------------------------------------------------------------------------------


