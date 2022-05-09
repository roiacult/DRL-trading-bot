from trader.env.benchmarks.base_benchmark import BaseBenchmark, SIGNALS


class BuyAndHold(BaseBenchmark):
    def get_label(self) -> str:
        return 'Buy and Hold (BH)'

    def signal(self, i) -> SIGNALS:
        return SIGNALS.BUY
