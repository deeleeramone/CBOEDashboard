"""CBOE Model"""

import pandas as pd
import numpy as np
import requests
from typing import Literal, Tuple
from pandas import DataFrame
from datetime import datetime
from requests.exceptions import HTTPError

__docformat__: Literal["numpy"] = "numpy"

symbol: str = ""
TICKER_EXCEPTIONS: list[str] = ["NDX", "RUT"]

#%%
def get_cboe_directory() -> DataFrame:
    """Gets the US Listings Directory for the CBOE

    Returns
    -------
    pd.DataFrame: CBOE_DIRECTORY
        DataFrame of the CBOE listings directory

    Example
    -------
    CBOE_DIRECTORY = get_cboe_directory()
    """

    CBOE_DIRECTORY: DataFrame = pd.read_csv(
        "https://www.cboe.com/us/options/symboldir/equity_index_options/?download=csv"
    )
    CBOE_DIRECTORY = CBOE_DIRECTORY.rename(
        columns = {
            ' Stock Symbol':'Symbol', 
            ' DPM Name':'DPM Name',
            ' Post/Station':'Post/Station',
        }
        ).set_index('Symbol')
    
    return CBOE_DIRECTORY

def get_cboe_index_directory() -> DataFrame:
    """Gets the US Listings Directory for the CBOE

    Returns
    -------
    pd.DataFrame: CBOE_INDEXES

    Example
    -------
    CBOE_INDEXES = get_cboe_index_directory(
    """

    CBOE_INDEXES: DataFrame = pd.read_json(
        "https://cdn.cboe.com/api/global/us_indices/definitions/all_indices.json"
    )

    CBOE_INDEXES = DataFrame(CBOE_INDEXES).rename(
        columns={
            "calc_end_time": "Close Time",
            "calc_start_time": "Open Time",
            "currency": "Currency",
            "description": "Description",
            "display": "Display",
            "featured": "Featured",
            "featured_order": "Featured Order",
            "index_symbol": "Ticker",
            "mkt_data_delay": "Data Delay",
            "name": "Name",
            "tick_days": "Tick Days",
            "tick_frequency": "Frequency",
            "tick_period": "Period",
            "time_zone": "Time Zone",
        },
    )

    indices_order: list[str] = [
        "Ticker",
        "Name",
        "Description",
        "Currency",
        "Tick Days",
        "Frequency",
        "Period",
        "Time Zone",
    ]

    CBOE_INDEXES = DataFrame(CBOE_INDEXES, columns=indices_order).set_index(
        "Ticker"
    )

    return CBOE_INDEXES

# %%

indexes = get_cboe_index_directory().index.tolist()
directory = get_cboe_directory()

# %%
    # Get Ticker Info and Expirations

def get_ticker_info(symbol: str) -> Tuple[pd.DataFrame, list[str]]:
    """Gets basic info for the symbol and expiration dates

    Parameters
    ----------
    symbol: str
        The ticker to lookup

    Returns
    -------
    Tuple[pd.DataFrame, pd.Series]: ticker_details,ticker_expirations

    Examples
    --------
    ticker_details,ticker_expirations = get_ticker_info('AAPL')

    ticker_details,ticker_expirations = get_ticker_info('VIX')
    """

    # Variables for exception handling

    stock = "stock"
    index = "index"
    ticker: str = symbol
    new_ticker: str = ""
    ticker_details: DataFrame = pd.DataFrame()
    ticker_expirations: list = []
    
    try:
        # Checks ticker to determine if ticker is an index or an exception that requires modifying the request's URLs

        if ticker in TICKER_EXCEPTIONS:
            new_ticker = ("^" + ticker)
        else:
            if ticker not in indexes:
                new_ticker = ticker

            elif ticker in indexes:
                new_ticker = ("^" + ticker)

                # Gets the data to return, and if none returns empty Tuple #

        symbol_info_url = (
            "https://www.cboe.com/education/tools/trade-optimizer/symbol-info/?symbol="
            f"{new_ticker}"
        )

        symbol_info = requests.get(symbol_info_url)
        symbol_info_json = pd.Series(symbol_info.json())

        if symbol_info_json.success is False:
            ticker_details = pd.DataFrame()
            ticker_expirations = []
            print("No data found for the symbol: " f"{ticker}" "")
        else:
            symbol_details = pd.Series(symbol_info_json["details"])
            symbol_details = pd.DataFrame(symbol_details).transpose()
            symbol_details = symbol_details.reset_index()
            ticker_expirations = symbol_info_json["expirations"]

                # Cleans columns depending on if the security type is a stock or an index

            type = symbol_details.security_type

            if stock[0] in type[0]:
                stock_details = symbol_details
                ticker_details = pd.DataFrame(stock_details).rename(
                    columns={
                        "symbol": "Symbol",
                        "current_price": "Current Price",
                        "bid": "Bid",
                        "ask": "Ask",
                        "bid_size": "Bid Size",
                        "ask_size": "Ask Size",
                        "open": "Open",
                        "high": "High",
                        "low": "Low",
                        "close": "Close",
                        "volume": "Volume",
                        "iv30": "IV30",
                        "prev_day_close": "Previous Close",
                        "price_change": "Change",
                        "price_change_percent": "Change %",
                        "iv30_change": "IV30 Change",
                        "iv30_percent_change": "IV30 Change %",
                        "last_trade_time": "Last Trade Time",
                        "exchange_id": "Exchange ID",
                        "tick": "Tick",
                        "security_type": "Type",
                    }
                )
                details_columns = [
                    "Symbol",
                    "Type",
                    "Tick",
                    "Bid",
                    "Bid Size",
                    "Ask Size",
                    "Ask",
                    "Current Price",
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                    "Previous Close",
                    "Change",
                    "Change %",
                    "IV30",
                    "IV30 Change",
                    "IV30 Change %",
                    "Last Trade Time",
                ]
                ticker_details = (
                    pd.DataFrame(ticker_details, columns=details_columns)
                    .set_index(keys="Symbol")
                    .dropna(axis=1)
                    .transpose()
                )

            if index[0] in type[0]:
                index_details = symbol_details
                ticker_details = pd.DataFrame(index_details).rename(
                    columns={
                        "symbol": "Symbol",
                        "security_type": "Type",
                        "current_price": "Current Price",
                        "price_change": "Change",
                        "price_change_percent": "Change %",
                        "tick": "Tick",
                        "open": "Open",
                        "high": "High",
                        "low": "Low",
                        "close": "Close",
                        "prev_day_close": "Previous Close",
                        "iv30": "IV30",
                        "iv30_change": "IV30 Change",
                        "iv30_change_percent": "IV30 Change %",
                        "last_trade_time": "Last Trade Time",
                    }
                )

                index_columns = [
                    "Symbol",
                    "Type",
                    "Tick",
                    "Current Price",
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Previous Close",
                    "Change",
                    "Change %",
                    "IV30",
                    "IV30 Change",
                    "IV30 Change %",
                    "Last Trade Time",
                ]

                ticker_details = (
                    pd.DataFrame(ticker_details, columns=index_columns)
                    .set_index(keys="Symbol")
                    .dropna(axis=1)
                    .transpose()
                )

    except HTTPError:
        print("There was an error with the request'\n")
        ticker_details = pd.DataFrame()
        ticker_expirations = list()

    return ticker_details,ticker_expirations

# %%
    # Gets annualized high/low historical and implied volatility over 30/60/90 day windows.

def get_ticker_iv(symbol: str) -> pd.DataFrame:
    """Gets annualized high/low historical and implied volatility over 30/60/90 day windows.

    Parameters
    ----------
    symbol: str
        The loaded ticker

    Returns
    -------
    pd.DataFrame: ticker_iv

    Examples
    --------
    ticker_iv = get_ticker_iv('AAPL')

    ticker_iv = get_ticker_iv('NDX')
    """

    ticker = symbol

    # Checks ticker to determine if ticker is an index or an exception that requires modifying the request's URLs
    try:
        if ticker in TICKER_EXCEPTIONS:
            quotes_iv_url = (
                "https://cdn.cboe.com/api/global/delayed_quotes/historical_data/_"
                f"{ticker}"
                ".json"
            )
        else:
            if ticker not in indexes:
                quotes_iv_url = (
                    "https://cdn.cboe.com/api/global/delayed_quotes/historical_data/"
                    f"{ticker}"
                    ".json"
                )

            elif ticker in indexes:
                quotes_iv_url = (
                    "https://cdn.cboe.com/api/global/delayed_quotes/historical_data/_"
                    f"{ticker}"
                    ".json"
                )

                # Gets annualized high/low historical and implied volatility over 30/60/90 day windows.

        h_iv = requests.get(quotes_iv_url)

        if h_iv.status_code != 200:
            print("No data found for the symbol: " f"{ticker}" "")
            return pd.DataFrame()

        else:
            h_iv_json = pd.DataFrame(h_iv.json())
            h_columns = [
                "annual_high",
                "annual_low",
                "hv30_annual_high",
                "hv30_annual_low",
                "hv60_annual_high",
                "hv60_annual_low",
                "hv90_annual_high",
                "hv90_annual_low",
                "iv30_annual_high",
                "iv30_annual_low",
                "iv60_annual_high",
                "iv60_annual_low",
                "iv90_annual_high",
                "iv90_annual_low",
                "symbol",
            ]
            h_data = h_iv_json[1:]
            h_data = pd.DataFrame(h_iv_json).transpose()
            h_data = h_data[1:2]
            quotes_iv_df = pd.DataFrame(data=h_data, columns=h_columns).reset_index()

            quotes_iv_df = pd.DataFrame(quotes_iv_df).rename(
                columns={
                    "annual_high": "1Y High",
                    "annual_low": "1Y Low",
                    "hv30_annual_high": "HV30 1Y High",
                    "hv30_annual_low": "HV30 1Y Low",
                    "hv60_annual_high": "HV60 1Y High",
                    "hv60_annual_low": "HV60 1Y Low",
                    "hv90_annual_high": "HV90 1Y High",
                    "hv90_annual_low": "HV90 1Y Low",
                    "iv30_annual_high": "IV30 1Y High",
                    "iv30_annual_low": "IV30 1Y Low",
                    "iv60_annual_high": "IV60 1Y High",
                    "iv60_annual_low": "IV60 1Y Low",
                    "iv90_annual_high": "IV90 1Y High",
                    "iv90_annual_low": "IV90 1Y Low",
                    "symbol": "Symbol",
                },
            )

            quotes_iv_df = quotes_iv_df.set_index(keys="Symbol")

            iv_order = [
                "IV30 1Y High",
                "HV30 1Y High",
                "IV30 1Y Low",
                "HV30 1Y Low",
                "IV60 1Y High",
                "HV60 1Y High",
                "IV60 1Y Low",
                "HV60 1Y low",
                "IV90 1Y High",
                "HV90 1Y High",
                "IV90 1Y Low",
                "HV 90 1Y Low",
            ]

            ticker_iv = (
                pd.DataFrame(quotes_iv_df, columns=iv_order)
                .fillna(value="N/A")
                .transpose()
            )
    except HTTPError:
        print("There was an error with the request'\n")

    return ticker_iv

    # Gets quotes and greeks data and returns a dataframe: options_quotes


# %%
def get_ticker_chains(symbol: str) -> pd.DataFrame:
    """Gets the complete options chains for a ticker

    Parameters
    ----------
    symbol: str
        The ticker get options data for

    Returns
    -------
    ticker_options: pd.DataFrame
        DataFrame of all options chains for the ticker

    Examples
    --------
    ticker_options = get_ticker_chains('SPX')

    ticker_options = get_ticker_chains('SPX').filter(like = '2027-12-17', axis = 0)

    ticker_calls = get_ticker_chains('AAPL').filter(like = 'Call', axis = 0)

    vix_20C = (
        get_ticker_chains('VIX')
        .filter(like = 'Call', axis = 0)
        .reset_index(['Expiration', 'Type'])
        .query('20.0')
    )
    """

    ticker: str = symbol

    # Checks ticker to determine if ticker is an index or an exception that requires modifying the request's URLs

    try:

        ticker_info, _ = get_ticker_info(ticker)
        if not ticker_info.empty:
            last_price = float(ticker_info.loc["Current Price"])
        else:
            return pd.DataFrame()

        if ticker in TICKER_EXCEPTIONS:
            quotes_url = (
                "https://cdn.cboe.com/api/global/delayed_quotes/options/_"
                f"{ticker}"
                ".json"
            )
        else:
            if ticker not in indexes:
                quotes_url = (
                    "https://cdn.cboe.com/api/global/delayed_quotes/options/"
                    f"{ticker}"
                    ".json"
                )
            if ticker in indexes:
                quotes_url = (
                    "https://cdn.cboe.com/api/global/delayed_quotes/options/_"
                    f"{ticker}"
                    ".json"
                )

        r = requests.get(quotes_url)
        if r.status_code != 200:
            print("No data found for the symbol: " f"{ticker}" "")
            return pd.DataFrame()
        else:
            r_json = r.json()
            data = pd.DataFrame(r_json["data"])
            options = pd.Series(data.options, index=data.index)
            options_columns = list(options[0])
            options_data = list(options[:])
            options_df = pd.DataFrame(options_data, columns=options_columns)
            options_df = pd.DataFrame(options_df).rename(
                columns={
                    "option": "Option Symbol",
                    "bid": "Bid",
                    "bid_size": "Bid Size",
                    "ask": "Ask",
                    "ask_size": "Ask Size",
                    "iv": "IV",
                    "open_interest": "OI",
                    "volume": "Vol",
                    "delta": "Delta",
                    "gamma": "Gamma",
                    "theta": "Theta",
                    "rho": "Rho",
                    "vega": "Vega",
                    "theo": "Theoretical",
                    "change": "Change",
                    "open": "Open",
                    "high": "High",
                    "low": "Low",
                    "tick": "Tick",
                    "last_trade_price": "Last Price",
                    "last_trade_time": "Timestamp",
                    "percent_change": "% Change",
                    "prev_day_close": "Prev Close",
                }
            )

            options_df_order: list[str] = [
                "Option Symbol",
                "Tick",
                "Theoretical",
                "Last Price",
                "Prev Close",
                "% Change",
                "Open",
                "High",
                "Low",
                "Bid Size",
                "Bid",
                "Ask",
                "Ask Size",
                "Vol",
                "OI",
                "IV",
                "Theta",
                "Delta",
                "Gamma",
                "Vega",
                "Rho",
                "Timestamp",
            ]

            options_df: DataFrame = DataFrame(
                options_df, columns=options_df_order
            ).set_index(keys=["Option Symbol"])

            option_df_index = pd.Series(options_df.index).str.extractall(
                r"^(?P<Ticker>\D*)(?P<Expiration>\d*)(?P<Type>\D*)(?P<Strike>\d*)"
            )

            option_df_index: DataFrame = option_df_index.reset_index().drop(
                columns=["match", "level_0"]
            )

            option_df_index.Expiration = pd.DatetimeIndex(
                option_df_index.Expiration, yearfirst=True
            )

            option_df_index.Type = option_df_index.Type.str.replace(
                "C", "Call"
            ).str.replace("P", "Put")

            option_df_index.Strike = [ele.lstrip("0") for ele in option_df_index.Strike]
            option_df_index.Strike = option_df_index.Strike.astype(float)
            option_df_index.Strike = option_df_index.Strike * (1 / 1000)
            option_df_index = option_df_index.drop(columns=["Ticker"])
            ticker_chains = option_df_index.join(options_df.reset_index())

            ticker_chains = ticker_chains.drop(columns=["Option Symbol"]).set_index(
                keys=["Expiration", "Strike", "Type"]
            )

            ticker_chains["Theoretical"] = round(
                ticker_chains["Theoretical"], ndigits=2
            )
            ticker_chains["Prev Close"] = round(ticker_chains["Prev Close"], ndigits=2)
            ticker_chains["% Change"] = round(ticker_chains["% Change"], ndigits=4)

            ticker_chains.Tick = (
                ticker_chains["Tick"]
                .str.capitalize()
                .str.replace(pat="No_change", repl="No Change")
            )

            ticker_chains.OI = ticker_chains["OI"].astype(int)
            ticker_chains.Vol = ticker_chains["Vol"].astype(int)
            ticker_chains["Bid Size"] = ticker_chains["Bid Size"].astype(int)
            ticker_chains["Ask Size"] = ticker_chains["Ask Size"].astype(int)
            ticker_chains: DataFrame = ticker_chains.sort_index()
            ticker_calls: DataFrame = ticker_chains.filter(like="Call", axis=0).copy()
            ticker_puts: DataFrame = ticker_chains.filter(like="Put", axis=0).copy()
            ticker_calls = ticker_calls.reset_index()

            ticker_calls.loc[:, ("$ to Spot")] = round(
                (ticker_calls.loc[:, ("Strike")])
                + (ticker_calls.loc[:, ("Ask")])
                - (last_price),
                ndigits=2,
            )

            ticker_calls.loc[:, ("% to Spot")] = round(
                (ticker_calls.loc[:, ("$ to Spot")] / last_price) * 100, ndigits=4
            )

            ticker_calls.loc[:, ("Breakeven")] = (
                ticker_calls.loc[:, ("Strike")] + ticker_calls.loc[:, ("Ask")]
            )

            ticker_calls.loc[:, ("Delta $")] = (
                (ticker_calls.loc[:, ("Delta")] * 100)
                * (ticker_calls.loc[:, ("OI")])
                * last_price
            )

            ticker_calls.loc[:, ("GEX")] = (
                ticker_calls.loc[:, ("Gamma")]
                * 100
                * ticker_calls.loc[:, ("OI")]
                * (last_price * last_price)
                * 0.01
            )

            ticker_calls.GEX = ticker_calls.GEX.astype(int)
            ticker_calls["Delta $"] = ticker_calls["Delta $"].astype(int)
            ticker_calls = ticker_calls.set_index(keys=["Expiration", "Strike", "Type"])

            ticker_puts = ticker_puts.reset_index()

            ticker_puts.loc[:, ("$ to Spot")] = round(
                (ticker_puts.loc[:, ("Strike")])
                - (ticker_puts.loc[:, ("Ask")])
                - (last_price),
                ndigits=2,
            )

            ticker_puts.loc[:, ("% to Spot")] = round(
                (ticker_puts.loc[:, ("$ to Spot")] / last_price) * 100, ndigits=4
            )

            ticker_puts.loc[:, ("Breakeven")] = (
                ticker_puts.loc[:, ("Strike")] - ticker_puts.loc[:, ("Ask")]
            )

            ticker_puts.loc[:, ("Delta $")] = (
                (ticker_puts.loc[:, ("Delta")] * 100)
                * (ticker_puts.loc[:, ("OI")])
                * last_price
                * (-1)
            )

            ticker_puts.loc[:, ("GEX")] = (
                ticker_puts.loc[:, ("Gamma")]
                * 100
                * ticker_puts.loc[:, ("OI")]
                * (last_price * last_price)
                * 0.01
            )

            ticker_puts.GEX = ticker_puts.GEX.astype(int)
            ticker_puts["Delta $"] = ticker_puts["Delta $"].astype(int)
            ticker_puts.set_index(keys=["Expiration", "Strike", "Type"], inplace=True)

            ticker_chains = pd.concat([ticker_puts, ticker_calls]).sort_index()

            temp = ticker_chains.reset_index().get(["Expiration"])
            temp.Expiration = pd.DatetimeIndex(data=temp.Expiration)
            temp_ = temp.Expiration - datetime.now()
            temp_ = temp_.astype(str)
            temp_ = temp_.str.extractall(r"^(?P<DTE>\d*)")
            temp_ = temp_.droplevel("match")
            temp_.DTE = temp_.DTE.fillna("-1")
            temp_.DTE = temp_.DTE.astype(int)
            temp_.DTE = temp_.DTE + 1
            ticker_chains = temp_.join(ticker_chains.reset_index()).set_index(
                ["Expiration", "Strike", "Type"]
            )

            ticker_chains["Expected Move"] = round(
                (ticker_chains["Last Price"] * ticker_chains["IV"])
                * (np.sqrt(ticker_chains["DTE"] / 252)),
                ndigits=2,
            )

            ticker_chains_cols: list[str] = [
                "DTE",
                "Tick",
                "Last Price",
                "Expected Move",
                "% Change",
                "Theoretical",
                "$ to Spot",
                "% to Spot",
                "Breakeven",
                "Vol",
                "OI",
                "Delta $",
                "GEX",
                "IV",
                "Theta",
                "Delta",
                "Gamma",
                "Vega",
                "Rho",
                "Open",
                "High",
                "Low",
                "Prev Close",
                "Bid Size",
                "Bid",
                "Ask",
                "Ask Size",
                "Timestamp",
            ]

            ticker_chains = DataFrame(data=ticker_chains, columns=ticker_chains_cols)

    except HTTPError:
        print("There was an error with the request'\n")

    return ticker_chains


# %%
def separate_chains(chains_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Helper function to separate Options Chains into Call and Put Chains.
    Parameters
    ----------
    chains_df : pd.DataFrame
        DataFrame of options chains data.

    Returns
    -------
    Tuple: [pd.DataFrame, pd.DataFrame]
        Tuple of options DataFrames separated by calls and puts.

    Example
    -------
    calls,puts = separate_chains(chains_df)
    """

    if not chains_df.empty and chains_df is not None:
        calls: pd.DataFrame = chains_df.filter(like="Call", axis=0).copy()
        puts: pd.DataFrame = chains_df.filter(like="Put", axis=0).copy()

        return calls, puts

    else:
        print(
            "There was an error with the input data, or the DataFrame passed was empty."
            "\n"
        )
        calls = pd.DataFrame()
        puts = pd.DataFrame()
        return calls, puts


# %%
def calc_chains_by_expiration(chains_df: pd.DataFrame) -> pd.DataFrame:
    """Calculates stats for options chains by expiration.
    Parameters
    ----------
    chains_df: pd.DataFrame
        DataFrame of options chains to use.

    Returns
    -------
    pd.DataFrame
        DataFrame with stats by expiration date.

    Example
    -------
    chains_by_expiration = calc_chains_by_expiration(chains_df)
    """

    if not chains_df.empty and chains_df is not None:

        calls, puts = separate_chains(chains_df)

        calls_by_expiration = (
            calls.reset_index()
            .groupby("Expiration")
            .sum(numeric_only=True)[["OI", "Vol", "Delta $", "GEX"]]
        )

        calls_by_expiration = calls_by_expiration.rename(
            columns={
                "OI": "Call OI",
                "Vol": "Call Vol",
                "Delta $": "Call Delta $",
                "GEX": "Call GEX",
            }
        )

        puts_by_expiration = (
            puts.reset_index()
            .groupby("Expiration")
            .sum(numeric_only=True)[["OI", "Vol", "Delta $", "GEX"]]
        )

        puts_by_expiration["Delta $"] = puts_by_expiration["Delta $"] * (-1)
        puts_by_expiration["GEX"] = puts_by_expiration["GEX"] * (-1)

        puts_by_expiration = puts_by_expiration.rename(
            columns={
                "OI": "Put OI",
                "Vol": "Put Vol",
                "Delta $": "Put Delta $",
                "GEX": "Put GEX",
            }
        )

        chains_by_expiration = calls_by_expiration.join(puts_by_expiration)

        chains_by_expiration["OI Ratio"] = round(
            chains_by_expiration["Put OI"] / chains_by_expiration["Call OI"], ndigits=4
        )

        chains_by_expiration["Net OI"] = (
            chains_by_expiration["Call OI"] + chains_by_expiration["Put OI"]
        )

        chains_by_expiration["Vol Ratio"] = round(
            chains_by_expiration["Put Vol"] / chains_by_expiration["Call Vol"],
            ndigits=4,
        )

        chains_by_expiration["Net Vol"] = (
            chains_by_expiration["Call Vol"] + chains_by_expiration["Put Vol"]
        )

        chains_by_expiration["Vol-OI Ratio"] = round(
            chains_by_expiration["Net Vol"] / chains_by_expiration["Net OI"], ndigits=4
        )

        chains_by_expiration["Net Delta $"] = (
            chains_by_expiration["Call Delta $"] + chains_by_expiration["Put Delta $"]
        )

        chains_by_expiration["Net GEX"] = (
            chains_by_expiration["Call GEX"] + chains_by_expiration["Put GEX"]
        )

        cols_order = [
            "Call OI",
            "Put OI",
            "Net OI",
            "OI Ratio",
            "Call Vol",
            "Put Vol",
            "Net Vol",
            "Vol Ratio",
            "Vol-OI Ratio",
            "Call Delta $",
            "Put Delta $",
            "Net Delta $",
            "Call GEX",
            "Put GEX",
            "Net GEX",
        ]

        chains_by_expiration = pd.DataFrame(chains_by_expiration, columns=cols_order)

        return chains_by_expiration

    else:
        print(
            "There was an error with the input data, or the DataFrame passed was empty."
            "\n"
        )
        chains_by_expiration = pd.DataFrame()
        return chains_by_expiration


# %%
def calc_chains_by_strike(chains_df: pd.DataFrame) -> pd.DataFrame:
    """
    Parameters
    ----------
    chains_df: pd.DataFrame
        Dataframe of the chains by expiration

    Returns
    -------
    pd.DataFrame:
        Dataframe of the chains by strike

    Example
    -------
    chains_by_strike = calc_chains_by_strike(chains_df)
    """

    if not chains_df.empty and chains_df is not None:

        calls, puts = separate_chains(chains_df)

        calls_by_strike = (
            calls.reset_index()
            .groupby("Strike")
            .sum(numeric_only=True)[["OI", "Vol", "Delta $", "GEX"]]
        )

        calls_by_strike = calls_by_strike.rename(
            columns={
                "OI": "Call OI",
                "Vol": "Call Vol",
                "Delta $": "Call Delta $",
                "GEX": "Call GEX",
            }
        )

        puts_by_strike = (
            puts.reset_index()
            .groupby("Strike")
            .sum(numeric_only=True)[["OI", "Vol", "Delta $", "GEX"]]
        )

        puts_by_strike["Delta $"] = puts_by_strike["Delta $"] * (-1)
        puts_by_strike["GEX"] = puts_by_strike["GEX"] * (-1)

        puts_by_strike = puts_by_strike.rename(
            columns={
                "OI": "Put OI",
                "Vol": "Put Vol",
                "Delta $": "Put Delta $",
                "GEX": "Put GEX",
            }
        )
        chains_by_strike = calls_by_strike.join(puts_by_strike)

        chains_by_strike["Net OI"] = (
            chains_by_strike["Call OI"] + chains_by_strike["Put OI"]
        )
        chains_by_strike["Net Vol"] = (
            chains_by_strike["Call Vol"] + chains_by_strike["Put Vol"]
        )
        chains_by_strike["Net Delta $"] = (
            chains_by_strike["Call Delta $"] + chains_by_strike["Put Delta $"]
        )
        chains_by_strike["Net GEX"] = (
            chains_by_strike["Call GEX"] + chains_by_strike["Put GEX"]
        )

        cols_order = [
            "Call OI",
            "Put OI",
            "Net OI",
            "Call Vol",
            "Put Vol",
            "Net Vol",
            "Call Delta $",
            "Put Delta $",
            "Net Delta $",
            "Call GEX",
            "Put GEX",
            "Net GEX",
        ]

        chains_by_strike = pd.DataFrame(data=chains_by_strike, columns=cols_order)

        return chains_by_strike

    else:
        print(
            "There was an error with the input data, or the DataFrame passed was empty."
            "\n"
        )
        chains_by_strike = pd.DataFrame()
        return chains_by_strike

# %%

class Ticker(object):
    """Class object for a single ticker"""

    def __init__(self) -> None:
        return None
    self = __init__

    def get_ticker(self, symbol:str) -> object:
        """Gets all data from the CBOE for a given ticker and returns an object

        Parameters
        ----------
        symbol: str
            The ticker symbol to get data for.

        Returns
        -------
        object: An object containing all the options data for the ticker.
            ticker.symbol
            ticker.details
            ticker.expirations
            ticker.iv
            ticker.chains
            ticker.calls
            ticker.puts
            ticker.by_expiration
            ticker.by_strike
            ticker.skew

        Examples
        --------
        spx = get_ticker('SPX')

        chains = get_ticker('spx').chains

        """
        try:
            self.symbol = symbol.upper()
            self.details, self.expirations = get_ticker_info(self.symbol)
            symbol_ = self.details.columns[0]
            self.details = self.details[symbol_]
            stock_price = self.details["Current Price"]
            self.stock_price = stock_price
            self.iv = get_ticker_iv(self.symbol)
            self.iv = self.iv[symbol_]
            self.chains = get_ticker_chains(self.symbol)
            self.calls, self.puts = separate_chains(self.chains)
            self.by_expiration = calc_chains_by_expiration(self.chains)
            self.by_strike = calc_chains_by_strike(self.chains)
            self.details["Put-Call Ratio"] = (
                self.by_expiration.sum()["Put OI"] / self.by_expiration.sum()["Call OI"]
            )
            self.name = str(directory.query("`Symbol` ==  @ticker.symbol")['Company Name'][0])

            # Calculate IV Skew by Expiration

            atm_calls: DataFrame = self.calls.reset_index()[
                ["Expiration", "Strike", "IV"]
            ]
            atm_calls = atm_calls.query(
                "@self.stock_price*0.995 <= Strike <= @self.stock_price*1.05"
            )
            atm_calls = atm_calls.groupby("Expiration")[["Strike", "IV"]]
            atm_calls = atm_calls.apply(lambda x: x.loc[x["Strike"].idxmin()])
            atm_calls = atm_calls.rename(columns={"Strike": "Call Strike", "IV": "Call IV"})
            otm_puts: DataFrame = self.puts.reset_index()[["Expiration", "Strike", "IV"]]
            otm_puts = otm_puts.query(
                "@self.stock_price*0.94 <= Strike <= @self.stock_price"
            )
            otm_puts = otm_puts.groupby("Expiration")[["Strike", "IV"]]
            otm_puts = otm_puts.apply(lambda x: x.loc[x["Strike"].idxmin()])
            otm_puts = otm_puts.rename(columns={"Strike": "Put Strike", "IV": "Put IV"})
            iv_skew: DataFrame = atm_calls.join(otm_puts)
            iv_skew["IV Skew"] = iv_skew["Put IV"] - iv_skew["Call IV"]
            self.skew = iv_skew
            self.by_expiration["IV Skew"] = iv_skew["IV Skew"]

        except Exception:
            print("\n")

        return ticker

ticker: Ticker = Ticker()