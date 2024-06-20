"""
This file contains functions for all statistic calculations.
Reference for functions: https://drive.google.com/drive/folders/1BfRhlvYniOr13KQWPN2iOUju_SghHHL5?usp=sharing
"""

import math
import statistics
import numpy as np
from Entities import Timeseries, Manager
OMEGA_ANNUALIZED_THRESHOLD = 0.005  # TODO: is there one threshold value or do we have different ones? ask Ranjan


def calc_omega_score(rors: list) -> float or None:
    """ Calculates Omega score for a given list of rors.

    :param rors: list of returns that will be used to calculate Omega score
    :return: Omega score, or None if calculation error
    """
    # turning compounded annualized threshold into monthly threshold
    monthly_threshold = math.pow((1 + OMEGA_ANNUALIZED_THRESHOLD), 1 / 12) - 1

    numerator = sum(rors) / len(rors) - monthly_threshold
    rors_below_threshold = [ror for ror in rors if ror < monthly_threshold]
    denominator = sum([monthly_threshold - ror for ror in rors_below_threshold]) / len(rors)

    if denominator != 0:
        return numerator / denominator + 1
    else:
        return None
def calc_annualized_return(rors: list) -> float:
    """ Calculates annualized return for a given list of rors.
    Annualized Return reference: https://www.investopedia.com/terms/a/annualized-total-return.asp

    :param rors: list of returns that will be used to calculate Annualized Return
    """
    cumulative_return = 1.0
    for ror in rors:
        cumulative_return = cumulative_return * (1 + ror)

    annualized_return = math.pow(cumulative_return, 12 / len(rors)) - 1
    return annualized_return


# TODO: risk free return rate for sharpe ratio?
def calc_sharpe_ratio(rors: list) -> float or None:
    """ Calculates (annualized) Sharpe Ratio for a given list of rors.

    :param rors: list of returns that will be used to calculate Sharpe Ratio
    :return: Sharpe ratio
    """
    if len(rors) < 2:
        return None

    return calc_annualized_return(rors) / (math.sqrt(statistics.variance(rors))) * math.sqrt(12)



#tuple[Timeseries, Timeseries]
def sync_returns(first_timeseries: Timeseries, second_timeseries: Timeseries) -> tuple:
    """ Given two timeseries, this function returns the overlapping 'slices' of each timeseries.

    :param first_timeseries: The first timeseries to sync
    :param second_timeseries: The second timeseries to sync
    :return: A tuple containing slices of the given timeseries
    """
    synced_first = Timeseries()
    synced_second = Timeseries()

    second_dates = second_timeseries.dates
    for i in range(len(first_timeseries.dates)):
        if first_timeseries.dates[i] in second_dates:
            synced_first.add_to_series(date=first_timeseries.dates[i], ror=first_timeseries.rors[i])

    synced_dates = synced_first.dates
    for i in range(len(second_timeseries.dates)):
        if second_timeseries.dates[i] in synced_dates:
            synced_second.add_to_series(date=second_timeseries.dates[i], ror=second_timeseries.rors[i])

    return synced_first, synced_second


def calc_pearson_correlation(first_timeseries: Timeseries, second_timeseries: Timeseries) -> float:
    """ Calculates Pearson Correlation of two timeseries.

    :param first_timeseries: The first timeseries for correlation
    :param second_timeseries: The second timeseries for correlation
    :return: correlation
    """
    synced_first_timeseries, synced_second_timeseries = sync_returns(first_timeseries, second_timeseries)
    synced_first_rors = synced_first_timeseries.rors
    synced_second_rors = synced_second_timeseries.rors

    return np.corrcoef(synced_first_rors, synced_second_rors)[0, 1]

def calc_drawdown_series(rors: list) -> list or None:
    """Calculate drawdown series for a given list of rors.
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


def calc_max_drawdown(rors: list) -> float:
    """ Calculate max. drawdown for a given list of rors.

    :param rors: list of returns used for calculation
    :return: max drawdown
    """
    return min(calc_drawdown_series(rors))


def calc_max_drawdown_length(rors: list) -> int:
    """ Calculate length (previous peak to trough) of max. drawdown for a given timeseries.

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

    return trough_index - peak_index  # months between trough and previous peak


def calc_max_drawdown_duration(rors: list) -> int:
    """ Calculate drawdown duration, or recovery time, of max. drawdown for a given timeseries.

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

    # what if the drawdown never recovers? currently, the drawdown length is returned. change this?
    for i in range(trough_index, len(dd_series)):
        if dd_series[i] == 0:
            drawdown_end = i
            break

    return drawdown_end - drawdown_start