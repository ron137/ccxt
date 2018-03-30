# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange
import hashlib
import time


class bit2c (Exchange):

    def describe(self):
        return self.deep_extend(super(bit2c, self).describe(), {
            'id': 'bit2c',
            'name': 'Bit2C',
            'countries': 'IL',  # Israel
            'rateLimit': 500,
            'has': {
                'CORS': False,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766119-3593220e-5ece-11e7-8b3a-5a041f6bcc3f.jpg',
                'api': 'https://bit2c.co.il',
                'www': 'https://bit2c.co.il',
                'doc': [
                    'https://bit2c.co.il/home/api',
                    'https://github.com/OferE/bit2c',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'Exchanges/{pair}/Ticker',
                        'Exchanges/{pair}/orderbook',
                        'Exchanges/{pair}/trades',
                    ],
                },
                'private': {
                    'post': [
                        'Account/Balance',
                        'Merchant/CreateCheckout',
                        'Order/AccountHistory',
                        'Order/AddCoinFundsRequest',
                        'Order/AddFund',
                        'Order/AddOrder',
                        'Order/AddOrderMarketPriceBuy',
                        'Order/AddOrderMarketPriceSell',
                        'Order/CancelOrder',
                        'Payment/GetMyId',
                        'Payment/Send',
                    ],
                    'get':[
                        'Account/Balance/v2',
                        'Order/MyOrders',
                        'Order/OrderHistory'
                    ],
                },
            },
            'markets': {
                'BTC/NIS': {'id': 'BtcNis', 'symbol': 'BTC/NIS', 'base': 'BTC', 'quote': 'NIS', 'precision': {'price': 2, 'amount': 8 }, 'limits':{ 'amount': {'min':0.00000001}, 'cost': {'min':10} }},
                'BCH/NIS': {'id': 'BchNis', 'symbol': 'BCH/NIS', 'base': 'BCH', 'quote': 'NIS', 'precision': {'price': 2, 'amount': 8 }, 'limits':{ 'amount': {'min':0.00000001}, 'cost': {'min':10} }},
                'LTC/NIS': {'id': 'LtcNis', 'symbol': 'LTC/NIS', 'base': 'LTC', 'quote': 'NIS', 'precision': {'price': 2, 'amount': 8 }, 'limits':{ 'amount': {'min':0.00000001}, 'cost': {'min':10} }},
                'BTG/NIS': {'id': 'BtgNis', 'symbol': 'BTG/NIS', 'base': 'BTG', 'quote': 'NIS', 'precision': {'price': 2, 'amount': 8 }, 'limits':{ 'amount': {'min':0.00000001}, 'cost': {'min':10} }},
            },
            'fees': {
                'trading': {
                    'maker': 0.5 / 100,
                    'taker': 0.5 / 100,
                },
            },
        })

    def fetch_balance(self, params={}):
        balance = self.privateGetAccountBalanceV2()
        result = {'info': balance}
        currencies = list(self.currencies.keys())
        for i in range(0, len(currencies)):
            currency = currencies[i]
            account = self.account()
            if currency in balance:
                available = 'AVAILABLE_' + currency
                account['free'] = balance[available]
                account['total'] = balance[currency]
                account['used'] = account['total'] - account['free']
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, limit=None, params={}):
        orderbook = self.publicGetExchangesPairOrderbook(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook)

    def fetch_ticker(self, symbol, params={}):
        ticker = self.publicGetExchangesPairTicker(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        timestamp = self.milliseconds()
        averagePrice = float(ticker['av'])
        baseVolume = float(ticker['a'])
        quoteVolume = baseVolume * averagePrice
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': float(ticker['h']),
            'ask': float(ticker['l']),
            'vwap': None,
            'open': None,
            'close': None,
            'first': None,
            'last': float(ticker['ll']),
            'change': None,
            'percentage': None,
            'average': averagePrice,
            'baseVolume': baseVolume,
            'quoteVolume': quoteVolume,
            'info': ticker,
        }

    def parse_order(self, order, market):
        info = order
        if 'NewOrder' in order:
            order = order['NewOrder']
        timestamp = int(order['created']) * 1000
        amount = float(order['amount'])
        remaining = amount
        filled = 0
        price = float(order['price'])
        average = price
        cost = 0
        result = {
            'info': info,
            'id': str(order['id']),
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'type': 'limit',
            'side': 'sell' if order['type'] == 1 else 'buy',
            'price': price,
            'average': average,
            'cost': 0,
            'amount': amount,
            'filled': 0,
            'remaining': remaining,
            'status': 'open',
            'fee': None,
        }
        return result

    def parse_trade(self, trade, market=None):
        timestamp = int(trade['date']) * 1000
        symbol = None
        if market:
            symbol = market['symbol']
        return {
            'id': str(trade['tid']),
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': None,
            'type': None,
            'side': None,
            'price': trade['price'],
            'amount': trade['amount'],
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        market = self.market(symbol)
        if since:
            params['date'] = since / 1000
        response = self.publicGetExchangesPairTrades(self.extend({
            'pair': market['id'],
        }, params))
        return self.parse_trades(response, market, since, limit)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' fetchOpenOrders requires a symbol parameter')
        self.load_markets()
        market = self.market(symbol)
        response = self.privateGetOrderMyOrders(self.extend({
            'pair': self.market_id(symbol)
            }, params))
        orders = []
        for side in response[self.market_id(symbol)]:
            side_orders = response[self.market_id(symbol)][side]
            if side_orders:
                orders += side_orders

        return self.parse_orders(orders, market, since, limit)

    def fetch_my_trades(self, symbol=None, since=None, limit=100, params={}):
        if not symbol:
            raise ExchangeError(self.id + ' fetchOpenOrders requires a symbol parameter')
        self.load_markets()
        market = self.market(symbol)
        response = self.privateGetOrderOrderHistory(self.extend({
            'pair': self.market_id(symbol),
            'take': limit
            },params))

        refined_trades = []
        for item in response:
            timestamp = int(item['ticks']) * 1000
            refined_trade = {
                'id': item['reference'],
                'info': response,
                'timestamp': timestamp,
                'datetime': self.iso8601(timestamp),
                'symbol': symbol,
                'type': None,
                'order': None,
                'price': float(item['price']),
                'side': 'sell' if item['action'] else 'buy',
                'amount': float(item['firstAmount']) * (-1) if item['action'] else float(item['firstAmount']),
            }
            refined_trades.append(refined_trade)

        return self.filter_by_since_limit(refined_trades, since, limit)


    def create_order(self, symbol, type, side, amount, price=None, params={}):
        method = 'privatePostOrderAddOrder'
        order = {
            'Amount': amount,
            'Pair': self.market_id(symbol),
        }
        if type == 'market':
            method += 'MarketPrice' + self.capitalize(side)
        else:
            order['Price'] = price
            order['Total'] = amount * price
            order['IsBid'] = (side == 'buy')
        result = getattr(self, method)(self.extend(order, params))
        return self.parse_order(result, self.market(symbol))

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostOrderCancelOrder({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        if api == 'public':
            url += '.json'
            url = self.url(url, params)
        else:
            self.check_required_credentials()
            nonce = int(time.time() * 10000000000)
            query = self.extend({'nonce': nonce}, params)
            body = self.urlencode(query)
            signature = self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512, 'base64')
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'key': self.apiKey,
                'sign': self.decode(signature),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}
