# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.base.exchange import Exchange

# -----------------------------------------------------------------------------

try:
    basestring  # Python 3
except NameError:
    basestring = str  # Python 2
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError

import time
import datetime
import dateutil

class quadrigacx (Exchange):

    def describe(self):
        return self.deep_extend(super(quadrigacx, self).describe(), {
            'id': 'quadrigacx',
            'name': 'QuadrigaCX',
            'countries': 'CA',
            'rateLimit': 10000,
            'version': 'v2',
            'has': {
                'fetchDepositAddress': True,
                'CORS': True,
                'withdraw': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766825-98a6d0de-5ee7-11e7-9fa4-38e11a2c6f52.jpg',
                'api': 'https://api.quadrigacx.com',
                'www': 'https://www.quadrigacx.com',
                'doc': 'https://www.quadrigacx.com/api_info',
            },
            'requiredCredentials': {
                'apiKey': True,
                'secret': True,
                'uid': True,
            },
            'api': {
                'public': {
                    'get': [
                        'order_book',
                        'ticker',
                        'transactions',
                    ],
                },
                'private': {
                    'post': [
                        'balance',
                        'bitcoin_deposit_address',
                        'bitcoin_withdrawal',
                        'bitcoincash_deposit_address',
                        'bitcoincash_withdrawal',
                        'bitcoingold_deposit_address',
                        'bitcoingold_withdrawal',
                        'buy',
                        'cancel_order',
                        'ether_deposit_address',
                        'ether_withdrawal',
                        'litecoin_deposit_address',
                        'litecoin_withdrawal',
                        'lookup_order',
                        'open_orders',
                        'sell',
                        'user_transactions',
                    ],
                },
            },
            'markets': {
                # TODO: Fix wrong limits of crypto/crypto markets
                'BTC/CAD': {'id': 'btc_cad', 'symbol': 'BTC/CAD', 'base': 'BTC', 'quote': 'CAD', 'maker': 0.005, 'taker': 0.005, 'limits':{ 'amount': {'min':0.000001}, 'cost': {'min': 1.0} }},
                'BTC/USD': {'id': 'btc_usd', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD', 'maker': 0.005, 'taker': 0.005, 'limits':{ 'amount': {'min':0.000001}, 'cost': {'min': 1.0} }},
                'ETH/BTC': {'id': 'eth_btc', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC', 'maker': 0.002, 'taker': 0.002, 'limits':{ 'amount': {'min':0.000001}, 'cost': {'min': 1.0} }},
                'ETH/CAD': {'id': 'eth_cad', 'symbol': 'ETH/CAD', 'base': 'ETH', 'quote': 'CAD', 'maker': 0.005, 'taker': 0.005, 'limits':{ 'amount': {'min':0.000001}, 'cost': {'min': 1.0} }},
                'LTC/CAD': {'id': 'ltc_cad', 'symbol': 'LTC/CAD', 'base': 'LTC', 'quote': 'CAD', 'maker': 0.005, 'taker': 0.005, 'limits':{ 'amount': {'min':0.000001}, 'cost': {'min': 1.0} }},
                'LTC/BTC': {'id': 'ltc_btc', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC', 'maker': 0.005, 'taker': 0.005, 'limits':{ 'amount': {'min':0.000001}, 'cost': {'min': 1.0} }},
                'BCH/CAD': {'id': 'bch_cad', 'symbol': 'BCH/CAD', 'base': 'BCH', 'quote': 'CAD', 'maker': 0.005, 'taker': 0.005, 'limits':{ 'amount': {'min':0.000001}, 'cost': {'min': 1.0} }},
                'BCH/BTC': {'id': 'bch_btc', 'symbol': 'BCH/BTC', 'base': 'BCH', 'quote': 'BTC', 'maker': 0.005, 'taker': 0.005, 'limits':{ 'amount': {'min':0.000001}, 'cost': {'min': 1.0} }},
                'BTG/CAD': {'id': 'btg_cad', 'symbol': 'BTG/CAD', 'base': 'BTG', 'quote': 'CAD', 'maker': 0.005, 'taker': 0.005, 'limits':{ 'amount': {'min':0.000001}, 'cost': {'min': 1.0} }},
                'BTG/BTC': {'id': 'btg_btc', 'symbol': 'BTG/BTC', 'base': 'BTG', 'quote': 'BTC', 'maker': 0.005, 'taker': 0.005, 'limits':{ 'amount': {'min':0.000001}, 'cost': {'min': 1.0} }},
            },
            'fees': {
                'trading': {
                    'maker': 0.5 / 100,
                    'taker': 0.5 / 100,
                }
            }
        })

    def to_mili_timestamp(self, date):
       return (time.mktime(dateutil.parser.parse(date).timetuple()) + dateutil.tz.tzlocal().utcoffset(datetime.datetime.now(dateutil.tz.tzlocal())).total_seconds() - 1 * 60 * 60 ) * 1000

    def fetch_balance(self, params={}):
        balances = self.privatePostBalance()
        result = {'info': balances}
        currencies = list(self.currencies.keys())
        for i in range(0, len(currencies)):
            currency = currencies[i]
            lowercase = currency.lower()
            account = {
                'free': float(balances[lowercase + '_available']),
                'used': float(balances[lowercase + '_reserved']),
                'total': float(balances[lowercase + '_balance']),
            }
            result[currency] = account
        return self.parse_balance(result)

    def fetch_order_book(self, symbol, limit=None, params={}):
        orderbook = self.publicGetOrderBook(self.extend({
            'book': self.market_id(symbol),
        }, params))
        timestamp = int(orderbook['timestamp']) * 1000
        return self.parse_order_book(orderbook, timestamp)

    def fetch_ticker(self, symbol, params={}):
        ticker = self.publicGetTicker(self.extend({
            'book': self.market_id(symbol),
        }, params))
        timestamp = int(ticker['timestamp']) * 1000
        vwap = float(ticker['vwap'])
        baseVolume = float(ticker['volume'])
        quoteVolume = baseVolume * vwap
        last = float(ticker['last'])
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': float(ticker['high']),
            'low': float(ticker['low']),
            'bid': float(ticker['bid']),
            'bidVolume': None,
            'ask': float(ticker['ask']),
            'askVolume': None,
            'vwap': vwap,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': baseVolume,
            'quoteVolume': quoteVolume,
            'info': ticker,
        }

    def parse_trade(self, trade, market):
        timestamp = int(trade['date']) * 1000
        return {
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': market['symbol'],
            'id': str(trade['tid']),
            'order': None,
            'type': None,
            'side': trade['side'],
            'price': float(trade['price']),
            'amount': float(trade['amount']),
        }

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        market = self.market(symbol)
        response = self.publicGetTransactions(self.extend({
            'book': market['id'],
            'time': 'hour',
        }, params))
        return self.parse_trades(response, market, since, limit)

    def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()

        # We gotta send symbol because the default is btc_cad
        market = self.market(symbol)
        open_orders = self.privatePostOpenOrders(self.extend({
            'book': market['id'],
        }, params))

        # No orders
        if open_orders == []:
            return open_orders

        # Parse orders
        parsed_orders = []
        for order in open_orders:
            timestamp = int(self.to_mili_timestamp(order['datetime']))
            parsed_order = {
                'info': order,
                'id': str(order['id']),
                'timestamp': timestamp,
                'datetime': str(order['datetime']),
                'symbol': symbol,
                'type': None,
                'side': 'buy' if order['type'] == 0 else 'sell',
                'price': float(order['price']),
                'average': None,
                'cost': None,
                'amount': float(order['amount']),
                'filled': None,
                'remaining': None,
                'status': 'open',
                'fee': None,
            }
            parsed_orders.append(parsed_order)

        return parsed_orders

    def fetch_my_trades(self, symbol=None, since=None, limit=10000, params={}):

        if not symbol:
            raise ExchangeError(self.id + ' fetch_my_trades requires a symbol parameter')

        # Load markets and prepare API request
        self.load_markets()
        request = {}
        method = 'privatePostUserTransactions'
        market = None

        # Add symbol to request
        if symbol:
            market = self.market(symbol)
            coin1 = market['id'].split('_')[0]
            coin2 = market['id'].split('_')[1]
            request['book'] = market['id']
            request['limit'] = 1000

        # Get user transactions from API and filter out deposits and withdrawals
        trades = getattr(self, method)(self.extend(request, params))
        trades = list(filter(lambda trade: trade['type'] == 2, trades))

        # Iterate returned data and parse it to the right format
        parsed_trades = []
        for trade in trades:

            # Check wether the trade is buy or sell
            if float(trade[coin2]) < 0:
                trade_side = 'buy'
            else:
                trade_side = 'sell'

            trade_amount = abs(float(trade[coin1]))
            timestamp = round(self.to_mili_timestamp(trade['datetime']))

            # Parsed trade
            parsed_trade = {
                'info': trade,
                'timestamp': timestamp,
                'datetime': self.iso8601(timestamp),
                'symbol': market['symbol'],
                'id': str(trade['id']),
                'order': None,
                'type': 'limit',
                'side': trade_side,
                'price': float(trade['rate']),
                'amount': float(trade_amount),
            }
            parsed_trades.append(parsed_trade)

        return parsed_trades

    def create_order(self, symbol, type, side, amount, price=None, params={}):

        # Create place order request
        method = 'privatePost' + self.capitalize(side)
        order = {
            'amount': amount,
            'book': self.market_id(symbol),
        }
        if type == 'limit':
            order['price'] = price

        # Request place order
        response = getattr(self, method)(self.extend(order, params))

        # Parse new order and return
        timestamp = int(self.to_mili_timestamp(response['datetime']))
        order = {
            'id': response['id'],
            'info': response,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': type,
            'side': side,
            'price': price,
            'average': price,
            'cost': 0,
            'amount': amount,
            'filled': 0,
            'remaining': amount,
            'status': 'open',
            'fee': None,
        }
        return order

    def cancel_order(self, id, symbol=None, params={}):
        return self.privatePostCancelOrder(self.extend({
            'id': id,
        }, params))

    def fetch_deposit_address(self, currency, params={}):
        method = 'privatePost' + self.get_currency_name(currency) + 'DepositAddress'
        response = getattr(self, method)(params)
        address = None
        status = None
        # [E|e]rror
        if response.find('rror') >= 0:
            status = 'error'
        else:
            address = response
            status = 'ok'
        self.check_address(address)
        return {
            'currency': currency,
            'address': address,
            'status': status,
            'info': self.last_http_response,
        }

    def get_currency_name(self, currency):
        currencies = {
            'ETH': 'Ether',
            'BTC': 'Bitcoin',
            'LTC': 'Litecoin',
            'BCH': 'Bitcoincash',
            'BTG': 'Bitcoingold',
        }
        return currencies[currency]

    def withdraw(self, currency, amount, address, tag=None, params={}):
        self.check_address(address)
        self.load_markets()
        request = {
            'amount': amount,
            'address': address,
        }
        method = 'privatePost' + self.get_currency_name(currency) + 'Withdrawal'
        response = getattr(self, method)(self.extend(request, params))
        return {
            'info': response,
            'id': None,
        }

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.version + '/' + path
        if api == 'public':
            url += '?' + self.urlencode(params)
        else:
            self.check_required_credentials()
            nonce = self.nonce()
            request = ''.join([str(nonce), self.uid, self.apiKey])
            signature = self.hmac(self.encode(request), self.encode(self.secret))
            query = self.extend({
                'key': self.apiKey,
                'nonce': nonce,
                'signature': signature,
            }, params)
            body = self.json(query)
            headers = {
                'Content-Type': 'application/json',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    def handle_errors(self, statusCode, statusText, url, method, headers, body):
        if not isinstance(body, basestring):
            return  # fallback to default error handler
        if len(body) < 2:
            return
        # Here is a sample QuadrigaCX response in case of authentication failure:
        # {"error":{"code":101,"message":"Invalid API Code or Invalid Signature"}}
        if statusCode == 200 and body.find('Invalid API Code or Invalid Signature') >= 0:
            raise AuthenticationError(self.id + ' ' + body)

    def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = self.fetch2(path, api, method, params, headers, body)
        if isinstance(response, basestring):
            return response
        if 'error' in response:
            raise ExchangeError(self.id + ' ' + self.json(response))
        return response
