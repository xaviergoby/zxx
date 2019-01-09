import pandas as pd
import numpy as np


class RSI():

    def __init__(self, data, time_period=14, overbought_level=70, oversold_level=30):
        self.data = data
        self.dates = data.Dates.tolist()
        # self.wk_days = data.WeekDays
        self.close = self.data.Close
        self.T = time_period
        self.overbought_level = overbought_level
        self.oversold_level = oversold_level
        self.signal_values_df = self.get_num_signal_df()
        self.num_sig_np_array = self.get_num_signal_np_array()
        self.cat_sig_list = self.get_cat_sig_labels()

    def get_num_signal_df(self):
        samples_num = len(self.data)
        num_sig_np_array = self.get_num_signal_np_array().values
        num_sig_dict = {"Dates":self.dates, "Close":self.close.values, "SignalValues":num_sig_np_array}
        num_sig_df = pd.DataFrame(num_sig_dict, index=range(samples_num))
        return num_sig_df

    def get_num_signal_np_array(self):
        """Relative Strength Index (RSI) is a momentum oscillator that measures the speed and change of price movements.
        RSI oscillates between zero and 100. Traditionally, and according to Wilder, RSI is considered overbought when above 70 and oversold when below 30.
        Signals can also be generated by looking for divergences, failure swings and centerline crossovers.
        RSI can also be used to identify the general trend."""

        ## get the price diff
        # delta = self.close.diff()[1:]
        delta = self.close.diff()

        ## positive gains (up) and negative gains (down) Series
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        # EMAs of ups and downs
        _gain = up.ewm(span=self.T, min_periods=self.T - 1).mean()
        _loss = down.abs().ewm(span=self.T, min_periods=self.T - 1).mean()

        RS = _gain / _loss
        result = pd.Series(100. - (100. / (1. + RS)), name="RSI")
        # num_sig_np_array = np.asarray(result)
        # return num_sig_np_array
        return result

    def get_cat_sig_labels(self):
        signal = self.get_num_signal_np_array()
        cat_sig_list_labels = []
        for s in signal:
            if s < self.oversold_level:
                cat_sig_list_labels.append("Buy")
            elif s > self.overbought_level:
                cat_sig_list_labels.append("Sell")
            else:
                cat_sig_list_labels.append("Hold")
        return cat_sig_list_labels




class SMA_CrossOver():

    def __init__(self, data, short_trend_period = 42, long_trend_period = 252, threshold = 5):
        self.data = data
        self.np_dates_array = data.index.values
        self.dt_dates_list = data.index.date.tolist()
        self.business_wk_days = data.Dates
        self.close = self.data.Close
        self.sttT = short_trend_period
        self.lttT = long_trend_period
        self.threshold = threshold
        self.stt = self.get_stt_and_ltt()[0]
        self.ltt = self.get_stt_and_ltt()[1]
        self.short_term_trend_period = str(self.sttT) + "d"
        self.long_term_trend_period = str(self.lttT) + "d"
        self.sma_crossover_signal_info = "-".join([self.short_term_trend_period, self.long_term_trend_period])
        self.signal_values_df = self.get_num_signal_df()
        self.signal_labels_df = self.get_cat_signal_df()
        self.signals_df = self.get_num_cat_signal_df()

    def get_stt_and_ltt(self):
        sst = np.round(self.close.rolling(window=self.sttT).mean(), 4)
        ltt = np.round(self.close.rolling(window=self.lttT).mean(), 4)
        return sst, ltt

    def get_num_signal_df(self):
        samples_num = len(self.data)
        sst = np.round(self.close.rolling(window=self.sttT).mean(), 4)
        ltt = np.round(self.close.rolling(window=self.lttT).mean(), 4)
        signal_values = sst - ltt
        num_sig_dict = {"Dates":self.dt_dates_list, "Close":self.close.values,
                         "SignalValues": signal_values.values}
        num_sig_df = pd.DataFrame(num_sig_dict, index=range(samples_num))
        return num_sig_df

    def get_num_signal_np_array(self):
        """
        :return: 1d numpy array row vector (len(samples_num),) and with element types:numpy.float64
        """
        num_sig = self.signal_values_df["SignalValues"].values
        return num_sig

    def get_cat_signal_df(self):
        samples_num = len(self.data)
        stt_minus_ltt_signal = self.signal_values_df.SignalValues
        signal = np.where(stt_minus_ltt_signal > self.threshold, "buy", "hold")
        signal = np.where(stt_minus_ltt_signal < self.threshold, "sell", signal)
        sig_pos_dict = {"Dates": self.dt_dates_list, "Close": self.close.values,
                         "SignalPosition": signal}
        sig_pos_df = pd.DataFrame(sig_pos_dict, index=range(samples_num))
        return sig_pos_df

    def get_cat_signal_list(self):
        """
        :return: list with length=len(samples_num) and with element types:str
        """
        cat_sig = self.signal_labels_df["SignalPosition"].tolist()
        return cat_sig

    def get_num_cat_signal_df(self):
        stt_minus_ltt_signal_values = self.get_num_signal_df().SignalValues.values
        signal_buy_sell_hold_position = self.get_cat_signal_df().SignalPosition.values
        samples_num = len(self.data)
        data_dict = {"Dates": self.dt_dates_list, "Close": self.close.values,
                     "SignalValues": stt_minus_ltt_signal_values,
                     "SignalPosition": signal_buy_sell_hold_position}
        datadf = pd.DataFrame(data_dict, index=range(samples_num))
        return datadf



