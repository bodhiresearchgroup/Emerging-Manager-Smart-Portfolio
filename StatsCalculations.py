"""
This file contains functions for all statistic calculations.
Reference for functions: https://drive.google.com/drive/folders/1BfRhlvYniOr13KQWPN2iOUju_SghHHL5?usp=sharing
"""

import math
import numpy as np
from Entities import Timeseries


def calc_omega_score(rors: np.array, threshold: float) -> float:
    """ 
    Calculates Omega score for a given list of rors.

    :param rors: list of returns that will be used to calculate Omega score
    :param threshold: annualized omega threshold (as a decimal)
    :return: Omega score, or None if calculation error
    """
    # turning compounded annualized threshold into monthly threshold
    monthly_threshold = math.pow((1 + threshold), 1 / 12) - 1

    differences = rors - monthly_threshold
    numerator = np.sum(differences[differences > 0])
    denominator = np.sum(abs(differences[differences < 0]))

    if denominator == 0:
        return np.inf
    else:
        return numerator / denominator 
    

def calc_cumulative_returns(rors: np.array) -> float:
    """ 
    Calculates cumulative returns for a given list of rors.

    :param rors: list of returns 
    :return: cumulative returns
    """
    cumulative_returns = (1 + rors).cumprod() - 1
    return cumulative_returns
    

def calc_ann_return(rors: np.array) -> float:
    """ 
    Calculates annualized return for a given list of rors.
    Annualized Return reference: https://www.investopedia.com/terms/a/annualized-total-return.asp

    :param rors: list of returns 
    :return: annualized return
    """
    total_return = calc_cumulative_returns(rors)[-1]

    annualized_return = math.pow(total_return + 1, 12 / len(rors)) - 1
    return annualized_return


# TODO: risk free return rate for sharpe ratio?
def calc_sharpe_ratio(rors: np.array) -> float:
    """ Calculates (annualized) Sharpe Ratio for a given list of rors.

    :param rors: list of returns that will be used to calculate Sharpe Ratio
    :return: Sharpe ratio, or None if calculation error
    """
    if len(rors) < 2:
        return None

    return calc_ann_return(rors) / (rors.std() * np.sqrt(12))


def sync_returns(first_timeseries: Timeseries, second_timeseries: Timeseries) -> tuple:
    """ 
    Given two timeseries, this function returns the overlapping 'slices' of each timeseries.

    :param first_timeseries: The first timeseries to sync
    :param second_timeseries: The second timeseries to sync
    :return: A tuple containing slices of the given timeseries, or None if the timeseries don't intersect

    TODO: Decide a threshold for min intersection between two timeseries
    """
    first_data, second_data = first_timeseries.data.align(second_timeseries.data, join='inner')
    
    if len(first_data) < 2: # Not enough meaningful data
        return None, None

    first_synced = Timeseries(data=first_data)
    second_synced = Timeseries(data=second_data)

    return first_synced, second_synced


def calc_pearson_correlation(first_timeseries: Timeseries, second_timeseries: Timeseries) -> float:
    """ 
    Calculates Pearson Correlation of two timeseries.

    :param first_timeseries: The first timeseries for correlation
    :param second_timeseries: The second timeseries for correlation
    :return: correlation
    """
    synced_first_timeseries, synced_second_timeseries = sync_returns(first_timeseries, second_timeseries)
    if synced_first_timeseries is None:
        return 0
    synced_first_rors = synced_first_timeseries.get_rors()
    synced_second_rors = synced_second_timeseries.get_rors()

    return np.corrcoef(synced_first_rors, synced_second_rors)[0, 1]


def calc_drawdown_series(rors: np.array) -> list:
    """
    Calculate drawdown series for a given list of rors.
    VAMI Reference: https://corporatefinanceinstitute.com/resources/wealth-management/value-added-monthly-index-vami/

    :param: rors: list of returns that will be used for calculations
    :return: list[float] of drawdowns
    """
    if len(rors) < 2:
        return None
    
    vami = [1.0]
    for ror in rors:
        vami.append(vami[-1] * (1.0 + ror))
    dd_series = []
    curr_peak = vami[0]
    for i in range(1, len(vami)):
        curr_peak = max(curr_peak, vami[i])
        dd_series.append(vami[i] / curr_peak - 1)  # Calculates drawdown relative to each peak
    return dd_series


def calc_max_drawdown(rors: np.array) -> float:
    """ 
    Calculate max. drawdown for a given list of rors.

    :param rors: list of returns used for calculation
    :return: max drawdown
    """
    return min(calc_drawdown_series(rors))


def calc_max_drawdown_length(rors: np.array) -> int:
    """ 
    Calculate length (previous peak to trough) of max. drawdown for a given timeseries.

    :param rors: list of returns used for calculation
    :return: length (in months) of max. drawdown
    """
    dd_series = calc_drawdown_series(rors)
    trough = min(dd_series)
    trough_index = dd_series.index(trough)

    peak = dd_series[0]
    peak_index = 0
    for (index, dd) in enumerate(dd_series[1:trough_index]):
        if dd >= peak:
            peak = dd
            peak_index = index + 1

    return trough_index - peak_index 


def calc_max_drawdown_duration(rors: np.array) -> int:
    """ 
    Calculate drawdown duration, or recovery time, of max. drawdown for a given timeseries.

    :param rors: list of returns used for calculation
    :return: drawdown duration (in months) of max. drawdown
    """
    dd_series = calc_drawdown_series(rors)
    trough = min(dd_series)
    trough_index = dd_series.index(trough)

    drawdown_start = trough_index
    drawdown_end = trough_index
    for i in range(trough_index, 0, -1):
        if dd_series[i] == 0:
            drawdown_start = i
            break

    # Prev: what if the drawdown never recovers? Currently, the drawdown length is returned. Change this?
    for i in range(trough_index, len(dd_series)):
        if dd_series[i] == 0:
            drawdown_end = i
            break

    return drawdown_end - drawdown_start


def calc_max_drawdown_length_index(rors: np.array):
    """ 
    Calculate the indices corresponding to the previous peak and trough of the maximum drawdown for a given timeseries.

    :param rors: list of returns used for calculation
    :return: start and end indices of the length of drawdown
    """
    dd_series = calc_drawdown_series(rors)
    trough = min(dd_series)
    trough_index = dd_series.index(trough)

    peak = dd_series[0]
    peak_index = 0
    for (index, dd) in enumerate(dd_series[1:trough_index]):
        if dd >= peak:
            peak = dd
            peak_index = index + 1

    return peak_index, trough_index


def calc_max_drawdown_duration_index(rors: np.array):
    """ 
    Calculate the indices corresponding to the previous peak and trough of the maximum drawdown for a given timeseries.

    :param rors: list of returns used for calculation
    :return:the start and end indices of the duration of drawdown
    """
    dd_series = calc_drawdown_series(rors)
    trough = min(dd_series)
    trough_index = dd_series.index(trough)

    drawdown_start = trough_index
    drawdown_end = trough_index
    for i in range(trough_index, 0, -1):
        if dd_series[i] == 0:
            drawdown_start = i
            break

    for i in range(trough_index, len(dd_series)):
        if dd_series[i] == 0:
            drawdown_end = i
            break

    if drawdown_end == trough_index:
        drawdown_end = len(dd_series)

    return drawdown_start, drawdown_end


def calc_weighted_drawdown_area(rors: np.array, whole: True, duration: False, base: float = math.e) -> float:
    """
    Calculate the weighted area under the drawdown curve for a given list of rors within a specified period.
    
    :param rors: list of returns used for calculation
    :param start: start index of the period
    :param end: end index of the period (inclusive)
    :return: weighted area under the drawdown curve
    """

    ## Get index for calculating the area under the whole drawdown curve
    start = 0
    end = len(rors)

    if whole is False:
        ## Get index for calculating the area under the drawdown curve between drawdown duration
        if duration is True:
            start, end = calc_max_drawdown_duration_index(rors)
        ## Get index for calculating the area under the drawdown curve between drawdown duration
        else: 
            start, end = calc_max_drawdown_length_index(rors)
        
    # Calculate drawdown series within the specified period
    dd_series = calc_drawdown_series(rors[start:end])
    if dd_series is None:
        return 0
    
    # Calculate the sum of the exponential weights
    weight_sum = sum(base ** (i + 1) for i in range(len(dd_series)))

    # Calculate the weighted drawdown area
    weighted_area = 0
    for i, dd in enumerate(dd_series):
        # weight: normalized exponential weight
        weight = (base ** (i + 1)) / weight_sum
        weighted_area += abs(dd) * weight
    
    return weighted_area


def calc_pop_to_drop(rors:np.array, p: float, q: float) -> float:
    """
    Calculate pop2drop ratio of timeseries
    param rors: list of returns used for calculation
             p: upper percentile
             q: lower percentile
    return: ratio of average gain to average loss
    """
    # Calculate the percentiles
    pth_percentile = np.percentile(rors, p)
    qth_percentile = np.percentile(rors, q)
    
    # Calculate the average of values at or above the pth percentile (gains)
    avg_gain = np.mean(rors[rors >= pth_percentile])
    
    # Calculate the average of values at or below the qth percentile (losses)
    avg_loss = np.mean(rors[rors <= qth_percentile])
    
    # Calculate the ratio of the average gain to the average loss
    pop2drop_ratio = abs(avg_gain / avg_loss)
    
    return pop2drop_ratio


def calc_gain_to_pain(rors: Timeseries, s_and_p: Timeseries) -> float:
    """
    Calculate Gain to Pain ratio of timeseries during months when S&P500 is down
    param rors: list of returns used for calculation
                s_and_p: S&P 500 returns
        
    return: gain to pain ratio
    """
    rors, s_and_p = sync_returns(rors, s_and_p)
    
    rors = rors.get_rors()
    s_and_p = s_and_p.get_rors()

    # Filter for months when the S&P 500 is down (negative returns)
    relative_returns = rors[s_and_p < 0]
    total_gain = np.sum(relative_returns[relative_returns > 0])
    #Calculate sum of negative returns
    total_pain = np.sum(np.abs(relative_returns[relative_returns < 0]))
    #Gain to pain ratio calculation
    if total_pain == 0:
        return np.inf #no pain
    else:
        return total_gain / total_pain