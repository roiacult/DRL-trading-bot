from ta.volume import (
    MFIIndicator,
    AccDistIndexIndicator,
    OnBalanceVolumeIndicator,
    ChaikinMoneyFlowIndicator,
    ForceIndexIndicator,
    VolumePriceTrendIndicator,
    NegativeVolumeIndexIndicator,
    EaseOfMovementIndicator
)

from ta.momentum import (
    AwesomeOscillatorIndicator,
    RSIIndicator,
    TSIIndicator,
    UltimateOscillator,
)

from ta.trend import (
    MACD,
    AroonIndicator,
    CCIIndicator,
    DPOIndicator,
    KSTIndicator,
    MassIndex,
    VortexIndicator, TRIXIndicator,
)

from ta.volatility import (
    BollingerBands,
    KeltnerChannel,
)

from ta.others import (
    DailyReturnIndicator,
    DailyLogReturnIndicator
)


def add_volume_indicators(df, high: str, low: str, close: str, volume: str):
    # 'volume_mfi', 'volume_adi', 'volume_obv', 'volume_cmf', 'volume_fi', 'volume_em', 'volume_vpt', 'volume_nvi'

    # Money Flow Indicator
    df[f"volume_mfi"] = MFIIndicator(
        high=df[high],
        low=df[low],
        close=df[close],
        volume=df[volume],
        window=14,
    ).money_flow_index()

    # Accumulation Distribution Index
    df[f"volume_adi"] = AccDistIndexIndicator(
        high=df[high], low=df[low], close=df[close], volume=df[volume]
    ).acc_dist_index()

    # On Balance Volume
    df[f"volume_obv"] = OnBalanceVolumeIndicator(
        close=df[close], volume=df[volume]
    ).on_balance_volume()

    # Chaikin Money Flow
    df[f"volume_cmf"] = ChaikinMoneyFlowIndicator(
        high=df[high], low=df[low], close=df[close], volume=df[volume]
    ).chaikin_money_flow()

    # Force Index
    df[f"volume_fi"] = ForceIndexIndicator(
        close=df[close], volume=df[volume], window=13
    ).force_index()

    # Ease of Movement
    indicator_eom = EaseOfMovementIndicator(
        high=df[high], low=df[low], volume=df[volume], window=14
    )
    df[f"volume_em"] = indicator_eom.ease_of_movement()

    # Volume Price Trend
    df[f"volume_vpt"] = VolumePriceTrendIndicator(
        close=df[close], volume=df[volume]
    ).volume_price_trend()

    # Negative Volume Index
    df[f"volume_nvi"] = NegativeVolumeIndexIndicator(
        close=df[close], volume=df[volume]
    ).negative_volume_index()


def add_momentum_indicators(df, high: str, low: str, close: str):
    # 'momentum_rsi', 'momentum_tsi', 'momentum_uo', 'momentum_ao'

    # Relative Strength Index (RSI)
    df[f"momentum_rsi"] = RSIIndicator(
        close=df[close], window=14
    ).rsi()

    # TSI Indicator
    df[f"momentum_tsi"] = TSIIndicator(
        close=df[close], window_slow=25, window_fast=13
    ).tsi()

    # Ultimate Oscillator
    df[f"momentum_uo"] = UltimateOscillator(
        high=df[high],
        low=df[low],
        close=df[close],
        window1=7,
        window2=14,
        window3=28,
        weight1=4.0,
        weight2=2.0,
        weight3=1.0,
    ).ultimate_oscillator()

    # Awesome Oscillator
    df[f"momentum_ao"] = AwesomeOscillatorIndicator(
        high=df[high], low=df[low], window1=5, window2=34
    ).awesome_oscillator()


def add_trend_indicators(df, high: str, low: str, close: str):
    # 'trend_macd', 'trend_vortex_ind_pos', 'trend_vortex_ind_neg', 'trend_vortex_ind_diff', 'trend_trix',
    # 'trend_mass_index', 'trend_cci', 'trend_dpo', 'trend_kst', 'trend_kst_sig', 'trend_kst_diff', 'trend_aroon_up',
    # 'trend_aroon_down', 'trend_aroon_ind',

    # MACD
    indicator_macd = MACD(
        close=df[close], window_slow=26, window_fast=12, window_sign=9
    )
    df[f"trend_macd"] = indicator_macd.macd()

    # Vortex Indicator
    indicator_vortex = VortexIndicator(
        high=df[high], low=df[low], close=df[close], window=14
    )
    df[f"trend_vortex_ind_pos"] = indicator_vortex.vortex_indicator_pos()
    df[f"trend_vortex_ind_neg"] = indicator_vortex.vortex_indicator_neg()
    df[f"trend_vortex_ind_diff"] = indicator_vortex.vortex_indicator_diff()

    # TRIX Indicator
    df[f"trend_trix"] = TRIXIndicator(
        close=df[close], window=15
    ).trix()

    # Mass Index
    df[f"trend_mass_index"] = MassIndex(
        high=df[high], low=df[low], window_fast=9, window_slow=25
    ).mass_index()

    # CCI Indicator
    df[f"trend_cci"] = CCIIndicator(
        high=df[high],
        low=df[low],
        close=df[close],
        window=20,
        constant=0.015,
    ).cci()

    # DPO Indicator
    df[f"trend_dpo"] = DPOIndicator(
        close=df[close], window=20
    ).dpo()

    # KST Indicator
    indicator_kst = KSTIndicator(
        close=df[close],
        roc1=10,
        roc2=15,
        roc3=20,
        roc4=30,
        window1=10,
        window2=10,
        window3=10,
        window4=15,
        nsig=9,
    )
    df[f"trend_kst"] = indicator_kst.kst()
    df[f"trend_kst_sig"] = indicator_kst.kst_sig()
    df[f"trend_kst_diff"] = indicator_kst.kst_diff()

    # Aroon Indicator
    indicator_aroon = AroonIndicator(close=df[close], window=25)
    df[f"trend_aroon_up"] = indicator_aroon.aroon_up()
    df[f"trend_aroon_down"] = indicator_aroon.aroon_down()
    df[f"trend_aroon_ind"] = indicator_aroon.aroon_indicator()


def add_volatility_indicator(df, high: str, low: str, close: str):
    # 'volatility_bbh', 'volatility_bbhi', 'volatility_bbli', 'volatility_bbm', 'volatility_bbl', 'volatility_kchi',
    # 'volatility_kcli',

    # Bollinger Bands
    indicator_bb = BollingerBands(
        close=df[close], window=20, window_dev=2,
    )
    df[f"volatility_bbh"] = indicator_bb.bollinger_hband()
    df[f"volatility_bbhi"] = indicator_bb.bollinger_hband_indicator()
    df[f"volatility_bbli"] = indicator_bb.bollinger_lband_indicator()
    df[f"volatility_bbm"] = indicator_bb.bollinger_mavg()
    df[f"volatility_bbl"] = indicator_bb.bollinger_lband()

    # Keltner Channel
    indicator_kc = KeltnerChannel(
        close=df[close], high=df[high], low=df[low], window=10,
    )
    df[f"volatility_kchi"] = indicator_kc.keltner_channel_hband_indicator()
    df[f"volatility_kcli"] = indicator_kc.keltner_channel_lband_indicator()


def add_other_indicators(df, close: str):
    # 'others_dr', 'others_dlr'

    # Daily Return
    df[f"others_dr"] = DailyReturnIndicator(close=df[close]).daily_return()

    # Daily Log Return
    df[f"others_dlr"] = DailyLogReturnIndicator(close=df[close]).daily_log_return()


def add_all_indicators(df, high: str, low: str, close: str, volume: str):
    add_volume_indicators(df, high, low, close, volume)
    add_momentum_indicators(df, high, low, close)
    add_trend_indicators(df, high, low, close)
    add_volatility_indicator(df, high, low, close)
    add_other_indicators(df, close)

    return df
