"""CBOE Options Dashboard"""
__docformat__ = "numpy"

import pandas as pd
import numpy as np
import streamlit as st
from pandas import DataFrame
from st_aggrid import AgGrid,ColumnsAutoSizeMode
from data import cboe_model as cboe


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 0)
pd.set_option('display.colheader_justify', 'left')

CBOE_DIRECTORY: DataFrame = cboe.get_cboe_directory()
CBOE_INDEXES: DataFrame = cboe.get_cboe_index_directory()

    # Start of Dashboard Section
st.set_page_config(
    page_title = 'Options Analysis Dashboard',
    layout = 'wide',
    menu_items={
        "Get help":"https://discord.com/invite/Y4HDyB6Ypu",
        },
    )
st.title('CBOE Options Dashboard')

col_1,col_2,col_3,col_4,col_5,col_6,col_7,col_8,col_9,col_10 = st.columns([0.20,0.33,0.20,0.20,0.20,0.20,0.20,0.20,0.20,1])
with col_1:
    symbol = st.text_input(label = 'Ticker', value = '', key = 'symbol')
if symbol == '':
    st.write('Please enter a symbol')

else:
    @st.cache_data
    def get_ticker(symbol) -> object:
        ticker: object = cboe.ticker.get_ticker(symbol)
        
        return ticker
    ticker = get_ticker(symbol)
    
    if ticker:
        try:
            ticker.by_expiration.index = ticker.by_expiration.index.astype(str)
            ticker.skew.index = ticker.skew.index.astype(str)
            ticker.chains = ticker.chains.reset_index()
            ticker.chains.Expiration = ticker.chains.Expiration.astype(str)
            ticker.chains = ticker.chains.set_index('Expiration')
        
            with col_2:
                st.write('\n')
                st.write('\n')
                st.write(ticker.name)

            with col_3:
                st.metric(label = 'Current Price', value = ticker.details['Current Price'], delta = ticker.details['Change %'])
                st.write('% Change')
            
            with col_4:
                st.metric(label = "IV 30", value = ticker.details['IV30'], delta = ticker.details['IV30 Change'])
                st.write('IV 30 Change')
            
            with col_5:
                iv_diff: float = round((ticker.details['IV30'] - ticker.iv['IV30 1Y High']), ndigits = 4)
                st.metric(label = 'IV 30 1 Year High', value = round(ticker.iv['IV30 1Y High'], ndigits = 4), delta = iv_diff)
                st.write('IV 30 - 1 Year High')
                
            with col_6:
                iv_low_diff: float = round((ticker.details['IV30'] - ticker.iv['IV30 1Y Low']), ndigits = 4)
                st.metric(label = 'IV 30 1 Year Low', value = round(ticker.iv['IV30 1Y Low'], ndigits = 4), delta = iv_low_diff)
                st.write('IV 30 - 1 Year Low')
            
            with col_7:
                net_pcr: int = ((int(ticker.by_expiration['Put OI'].sum())) - (int(ticker.by_expiration['Call OI'].sum()))) 
                st.metric(label = 'Put/Call OI Ratio', value = round(ticker.details['Put-Call Ratio'], ndigits = 4), delta = net_pcr)
                st.write('Net Put - Call OI')
            
            with col_8:
                net_volume: int = ((int(ticker.by_expiration['Put Vol'].sum())) - (int(ticker.by_expiration['Call Vol'].sum())))
                vol_ratio: float = ((ticker.by_expiration['Put Vol'].sum()) / (ticker.by_expiration['Call Vol'].sum()))
                st.metric(label = 'Put/Call Vol Ratio', value = round(vol_ratio, ndigits = 4), delta = net_volume)
                st.write('Net Put - Call Vol')
                
            with col_9:
                turnover_ratio: float = round(
                    ((ticker.by_expiration['Put Vol'].sum()) + (ticker.by_expiration['Call Vol'].sum()))
                    /((ticker.by_expiration['Put OI'].sum()) + (ticker.by_expiration['Call OI'].sum()))
                ,ndigits = 4)
                
                turnover = (
                    ((ticker.by_expiration['Put Vol'].sum()) + (ticker.by_expiration['Call Vol'].sum()))
                    - ((ticker.by_expiration['Put OI'].sum()) + (ticker.by_expiration['Call OI'].sum()))
                )
                
                st.metric(label = 'Turnover Ratio', value = turnover_ratio, delta = int(turnover))
                st.write('Net Volume - OI')
            
            with col_10:
                put_gex: float = ((ticker.by_expiration['Put GEX'].sum()) * (-1))
                call_gex: float = (ticker.by_expiration['Call GEX'].sum())
                net_gex = put_gex + call_gex
                st.metric(label = 'Net Gamma Exposure', value = int(net_gex), delta = int(call_gex - put_gex))
                st.write('Net Call - Put GEX')

            tab1,tab2,tab3 = st.tabs(["Summary", "Chains", "Charts"])

            with tab1:
                tab5,tab6 = st.tabs(['By Expiration', 'By Strike'])
                with tab5:
                    AgGrid(
                        ticker.by_expiration.reset_index(),
                        update_mode="value_changed",
                        fit_columns_on_grid_load = True,
                    )
                with tab6:
                    AgGrid(
                        ticker.by_strike.reset_index(), 
                        update_mode="Value_changed",
                        fit_columns_on_grid_load = True,
                    )

            with tab2:
                    st.write('\n')
                    AgGrid(
                        ticker.chains.reset_index(),
                        height = 600,
                        update_mode="value_changed",
                        columns_auto_size_mode = ColumnsAutoSizeMode.FIT_CONTENTS,
                    )

            with tab3:
                st.write('\n')  
                tab4,tab5,tab6 = st.tabs(["Open Interest", "Gamma", "Volatility"])
                with tab4:
                    st.write('\n')
                    tab7,tab8,tab11 = st.tabs(["By Strike", "By Expiration", "Ratios"])
                    with tab7:
                        st.header(f"{ticker.symbol}"' Open Interest by Strike')
                        chart1_data = pd.DataFrame(columns = ['Puts', 'Calls'])
                        chart1_data.Puts = ticker.by_strike['Put OI']*(-1)
                        chart1_data.Calls = ticker.by_strike['Call OI']
                        st.bar_chart(
                            chart1_data,
                            y=['Puts', 'Calls'],
                            width=0,
                            height=600,
                            use_container_width = True,
                        )        
                    with tab8:
                        st.write('\n')
                        st.header(f"{ticker.symbol}"' Open Interest by Expiration')
                        chart2_data = pd.DataFrame(columns = ['Puts', 'Calls'])
                        chart2_data.Puts = ticker.by_expiration['Put OI']*(-1)
                        chart2_data.Calls = ticker.by_expiration['Call OI']
                        chart2_data.fillna(axis = 1, value = 0, inplace = True)
                        st.bar_chart(
                            chart2_data,
                            y=['Puts', 'Calls'],
                            width=0,
                            height=600,
                            use_container_width=True,
                        )
                    with tab11:
                        st.write('\n')
                        st.header('Open Interest and Volume Ratios by Expiration for 'f"{ticker.symbol}")
                        
                        chart7_data = pd.DataFrame(columns = ['OI Ratio', 'Vol Ratio', 'Vol-OI Ratio'])
                        chart7_data['OI Ratio'] = ticker.by_expiration['OI Ratio']
                        chart7_data['Vol Ratio'] = ticker.by_expiration['Vol Ratio']
                        chart7_data['Vol-OI Ratio'] = ticker.by_expiration['Vol-OI Ratio']
                        chart7_data.replace([np.inf, -np.inf], np.nan, inplace=True)
                        chart7_data.fillna(value = 0.0000, inplace = True)
                        
                        st.line_chart(
                            data = chart7_data,
                            use_container_width = True,
                            height = 450,
                            y = ['OI Ratio', 'Vol Ratio', 'Vol-OI Ratio'],
                        )
                        
                with tab5:
                    st.write('\n')
                    tab7,tab8 = st.tabs(["By Strike", "By Expiration"])
                    with tab7:
                        st.header('Nominal Gamma Exposure Per 1% Change in 'f"{ticker.symbol}")
                        chart3_data = pd.DataFrame(columns = ['Puts', 'Calls'])
                        chart3_data.Puts = ticker.by_strike['Put GEX']
                        chart3_data.Calls = ticker.by_strike['Call GEX']
                        chart3_data.fillna(axis = 1, value = 0, inplace = True)
                        st.bar_chart(
                            chart3_data,
                            y= ['Puts','Calls'],
                            use_container_width = True,
                            width=0,
                            height=600
                        )
                    with tab8:
                        st.header('Nominal Gamma Exposure per 1% Change in 'f"{ticker.symbol}")
                        chart4_data = pd.DataFrame(columns = ['Calls', 'Puts'])
                        chart4_data.Puts = ticker.by_expiration['Put GEX']
                        chart4_data.Calls = ticker.by_expiration['Call GEX']
                        chart4_data.fillna(axis = 1, value = 0, inplace = True)
                        st.bar_chart(
                            chart4_data,
                            y=['Puts', 'Calls'],
                            use_container_width = True,
                            width=0,
                            height=600
                        )
                with tab6:
                    st.write('\n')
                    tab9,tab10,tab11 = st.tabs(["Skew", "Smile", "Surface"])
                    with tab9:
                        st.subheader('Implied Volatility Skew of 'f"{ticker.symbol}")
                        chart5_data = ticker.skew
                        chart5_data = (
                            chart5_data.rename(columns = {
                                'Call IV': 'ATM Call IV',
                                'Put IV': '5% OTM Put IV'
                            })
                        )
                        chart5_data.index = chart5_data.index.astype(str)
                        st._arrow_area_chart(
                            chart5_data,
                            y = ['IV Skew'],
                            use_container_width = True,
                            width = 0,
                            height = 450,
                        )
                        AgGrid(
                            ticker.skew.reset_index(),
                            update_mode="value_changed",
                            columns_auto_size_mode = ColumnsAutoSizeMode.FIT_CONTENTS,
                        )

                    with tab10:
                        def get_chart6_data(choice) -> pd.DataFrame:
                            chart6_data = pd.DataFrame(columns = ['Call IV', 'Put IV'])
                            chart6_data['Call IV'] = ticker.calls.loc[choice]['IV'].reset_index(['Type'])['IV']
                            chart6_data['Put IV'] = ticker.puts.loc[choice]['IV'].reset_index(['Type'])['IV']
                            chart6_data = chart6_data.query("0 < `Call IV` and 0 < `Put IV`")
                            return chart6_data

                        choice = st.selectbox(label = "Expiration Date", options = ticker.expirations)

                        chart6_data = get_chart6_data(choice)

                        st.subheader("Volatility Smile of "f"{ticker.symbol}")                
                        st.line_chart(
                            chart6_data,
                            y = ['Call IV', 'Put IV'],
                            height = 450,
                            width = 0,
                            use_container_width = True,
                        )
                    with tab11:
                        st.write("Coming soon!")

        except Exception:
            st.write('Sorry, no data found')
    else:
        pass