""" Information Ratio """
import numpy as np
from collections import deque
from pedlar.agent import Agent
import time as tm



class IRAgent(Agent):
    name = "IR"
    def __init__(self, verbose=False, **kwargs):
        self.verbose=verbose
        self.slow = deque(maxlen=128)
        self.fast = deque(maxlen=32)
        self.last_order = None
        self.price_list=[]
        self.std=0
        self.total_profit_list=[]
        self.total_profit=0
        self.order_in_progress=False
        super().__init__(**kwargs)


    """ Print order. Resets price_list, and updates last_order with current order.id """
    def on_order(self, order):
        """On order handler."""
        if self.verbose:
            print(f"Order: {order}")
        self.order_in_progress=True
        self.last_order=order.id
        self.price_list=[]

    """ print the profit after the order is closed """
    def on_order_close(self, order, profit):
        """On order close handler."""
        if self.verbose:
            print(f"PROFIT: {profit}")
        self.order_in_progress=False
        self.total_profit+=profit
        self.total_profit_list.append(self.total_profit)



    def on_tick(self, bid, ask, time=None):
        """On tick handler."""
        if self.verbose:
            print(f"Tick: {bid} {ask}")
        if not (self.orders):
            self.slow.append(bid)
            self.fast.append(bid)
            fast_std = np.std(self.fast)
            slow_std = np.std(self.slow)
            if fast_std == 0 or slow_std == 0:
                return
            fast_avg = sum(self.fast)/len(self.fast)
            slow_avg = sum(self.slow)/len(self.slow)
            fast_ir = fast_avg / fast_std   # use std to measure volatility
            slow_ir = slow_avg / slow_std
            if fast_avg != slow_avg:
                if self.verbose:
                    print('-------start making trades-------')
                if fast_avg > slow_avg:
                    self.buy()
                else:
                    self.sell()
                return


        # when the information ratio for current value > 1, close the order
        if self.orders:
            o = self.orders[self.last_order]
            if self.verbose:
                print(f"with order: {o.id}")
            if o.type=='buy':
                self.price_list.append(bid)
                self.std=np.std(self.price_list)
                ir = (bid - o.price )/self.std
            elif o.type == "sell":
                self.price_list.append(ask)
                self.std=np.std(self.price_list)
                ir=(o.price - ask ) / self.std

            if self.verbose:
                print('IR:',ir)

            if (ir > 1):
                if self.verbose:
                    print("Order close")
                    print(f"IR: {ir}")
                self.close()
            return

if __name__ == "__main__":
    backtest=False
    if not backtest:
        agent = IRAgent(username="algosoc", password="1234",
                            ticker="tcp://icats.doc.ic.ac.uk:7000",
                            endpoint="http://icats.doc.ic.ac.uk")
    else:
        agent = IRAgent(backtest="backtest_GBPUSD.csv")
  # OR agent = IRAgent.from_args() # python3 IR.py -b backtest_GBPUSD.csv
    agent.run()
