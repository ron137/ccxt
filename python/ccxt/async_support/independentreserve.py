# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange


class independentreserve(Exchange):

    def describe(self):
        return self.deep_extend(super(independentreserve, self).describe(), {
            'id': 'independentreserve',
            'name': 'Independent Reserve',
            'countries': ['AU', 'NZ'],  # Australia, New Zealand
            'rateLimit': 1000,
            'has': {
                'CORS': False,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/30521662-cf3f477c-9bcb-11e7-89bc-d1ac85012eda.jpg',
                'api': {
                    'public': 'https://api.independentreserve.com/Public',
                    'private': 'https://api.independentreserve.com/Private',
                },
                'www': 'https://www.independentreserve.com',
                'doc': 'https://www.independentreserve.com/API',
            },
            'api': {
                'public': {
                    'get': [
                        'GetValidPrimaryCurrencyCodes',
                        'GetValidSecondaryCurrencyCodes',
                        'GetValidLimitOrderTypes',
                        'GetValidMarketOrderTypes',
                        'GetValidOrderTypes',
                        'GetValidTransactionTypes',
                        'GetMarketSummary',
                        'GetOrderBook',
                        'GetAllOrders',
                        'GetTradeHistorySummary',
                        'GetRecentTrades',
                        'GetFxRates',
                    ],
                },
                'private': {
                    'post': [
                        'PlaceLimitOrder',
                        'PlaceMarketOrder',
                        'CancelOrder',
                        'GetOpenOrders',
                        'GetClosedOrders',
                        'GetClosedFilledOrders',
                        'GetOrderDetails',
                        'GetAccounts',
                        'GetTransactions',
                        'GetDigitalCurrencyDepositAddress',
                        'GetDigitalCurrencyDepositAddresses',
                        'SynchDigitalCurrencyDepositAddressWithBlockchain',
                        'WithdrawDigitalCurrency',
                        'RequestFiatWithdrawal',
                        'GetTrades',
                        'GetBrokerageFees',
                    ],
                },
            },
            'fees': {
                'trading': {
                    'taker': 0.5 / 100,
                    'maker': 0.5 / 100,
                    'percentage': True,
                    'tierBased': False,
                },
            },
            'commonCurrencies': {
                'PLA': 'PlayChip',
            },
        })

    async def fetch_markets(self, params={}):
        baseCurrencies = await self.publicGetGetValidPrimaryCurrencyCodes(params)
        quoteCurrencies = await self.publicGetGetValidSecondaryCurrencyCodes(params)
        result = []
        for i in range(0, len(baseCurrencies)):
            baseId = baseCurrencies[i]
            base = self.safe_currency_code(baseId)
            for j in range(0, len(quoteCurrencies)):
                quoteId = quoteCurrencies[j]
                quote = self.safe_currency_code(quoteId)
                id = baseId + '/' + quoteId
                symbol = base + '/' + quote
                result.append({
                    'id': id,
                    'symbol': symbol,
                    'base': base,
                    'quote': quote,
                    'baseId': baseId,
                    'quoteId': quoteId,
                    'info': id,
                    'active': None,
                    'precision': self.precision,
                    'limits': self.limits,
                })
        return result

    async def fetch_balance(self, params={}):
        await self.load_markets()
        balances = await self.privatePostGetAccounts(params)
        result = {'info': balances}
        for i in range(0, len(balances)):
            balance = balances[i]
            currencyId = self.safe_string(balance, 'CurrencyCode')
            code = self.safe_currency_code(currencyId)
            account = self.account()
            account['free'] = self.safe_float(balance, 'AvailableBalance')
            account['total'] = self.safe_float(balance, 'TotalBalance')
            result[code] = account
        return self.parse_balance(result)

    async def fetch_order_book(self, symbol, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'primaryCurrencyCode': market['baseId'],
            'secondaryCurrencyCode': market['quoteId'],
        }
        response = await self.publicGetGetOrderBook(self.extend(request, params))
        timestamp = self.parse8601(self.safe_string(response, 'CreatedTimestampUtc'))
        return self.parse_order_book(response, timestamp, 'BuyOrders', 'SellOrders', 'Price', 'Volume')

    def parse_ticker(self, ticker, market=None):
        timestamp = self.parse8601(self.safe_string(ticker, 'CreatedTimestampUtc'))
        symbol = None
        if market:
            symbol = market['symbol']
        last = self.safe_float(ticker, 'LastPrice')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_float(ticker, 'DayHighestPrice'),
            'low': self.safe_float(ticker, 'DayLowestPrice'),
            'bid': self.safe_float(ticker, 'CurrentHighestBidPrice'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'CurrentLowestOfferPrice'),
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': self.safe_float(ticker, 'DayAvgPrice'),
            'baseVolume': self.safe_float(ticker, 'DayVolumeXbtInSecondaryCurrrency'),
            'quoteVolume': None,
            'info': ticker,
        }

    async def fetch_ticker(self, symbol, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'primaryCurrencyCode': market['baseId'],
            'secondaryCurrencyCode': market['quoteId'],
        }
        response = await self.publicGetGetMarketSummary(self.extend(request, params))
        return self.parse_ticker(response, market)

    def parse_order(self, order, market=None):
        #
        #     {
        #         "OrderGuid": "c7347e4c-b865-4c94-8f74-d934d4b0b177",
        #         "CreatedTimestampUtc": "2014-09-23T12:39:34.3817763Z",
        #         "Type": "MarketBid",
        #         "VolumeOrdered": 5.0,
        #         "VolumeFilled": 5.0,
        #         "Price": null,
        #         "AvgPrice": 100.0,
        #         "ReservedAmount": 0.0,
        #         "Status": "Filled",
        #         "PrimaryCurrencyCode": "Xbt",
        #         "SecondaryCurrencyCode": "Usd"
        #     }
        #
        symbol = None
        baseId = self.safe_string(order, 'PrimaryCurrencyCode')
        quoteId = self.safe_string(order, 'PrimaryCurrencyCode')
        base = None
        quote = None
        if (baseId is not None) and (quoteId is not None):
            base = self.safe_currency_code(baseId)
            quote = self.safe_currency_code(quoteId)
            symbol = base + '/' + quote
        elif market is not None:
            symbol = market['symbol']
            base = market['base']
            quote = market['quote']
        orderType = self.safe_value(order, 'Type')
        if orderType.find('Market') >= 0:
            orderType = 'market'
        elif orderType.find('Limit') >= 0:
            orderType = 'limit'
        side = None
        if orderType.find('Bid') >= 0:
            side = 'buy'
        elif orderType.find('Offer') >= 0:
            side = 'sell'
        timestamp = self.parse8601(self.safe_string(order, 'CreatedTimestampUtc'))
        amount = self.safe_float(order, 'VolumeOrdered')
        if amount is None:
            amount = self.safe_float(order, 'Volume')
        filled = self.safe_float(order, 'VolumeFilled')
        remaining = None
        feeRate = self.safe_float(order, 'FeePercent')
        feeCost = None
        if amount is not None:
            if filled is not None:
                remaining = amount - filled
                if feeRate is not None:
                    feeCost = feeRate * filled
        fee = {
            'rate': feeRate,
            'cost': feeCost,
            'currency': base,
        }
        id = self.safe_string(order, 'OrderGuid')
        status = self.parse_order_status(self.safe_string(order, 'Status'))
        cost = self.safe_float(order, 'Value')
        average = self.safe_float(order, 'AvgPrice')
        price = self.safe_float(order, 'Price', average)
        return {
            'info': order,
            'id': id,
            'clientOrderId': None,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'type': orderType,
            'side': side,
            'price': price,
            'cost': cost,
            'average': average,
            'amount': amount,
            'filled': filled,
            'remaining': remaining,
            'status': status,
            'fee': fee,
            'trades': None,
        }

    def parse_order_status(self, status):
        statuses = {
            'Open': 'open',
            'PartiallyFilled': 'open',
            'Filled': 'closed',
            'PartiallyFilledAndCancelled': 'canceled',
            'Cancelled': 'canceled',
            'PartiallyFilledAndExpired': 'canceled',
            'Expired': 'canceled',
        }
        return self.safe_string(statuses, status, status)

    async def fetch_order(self, id, symbol=None, params={}):
        await self.load_markets()
        response = await self.privatePostGetOrderDetails(self.extend({
            'orderGuid': id,
        }, params))
        market = None
        if symbol is not None:
            market = self.market(symbol)
        return self.parse_order(response, market)

    async def fetch_my_trades(self, symbol=None, since=None, limit=50, params={}):
        await self.load_markets()
        pageIndex = self.safe_integer(params, 'pageIndex', 1)
        if limit is None:
            limit = 50
        request = self.ordered({
            'pageIndex': pageIndex,
            'pageSize': limit,
        })
        response = await self.privatePostGetTrades(self.extend(request, params))
        market = None
        if symbol is not None:
            market = self.market(symbol)
        return self.parse_trades(response['Data'], market, since, limit)

    def parse_trade(self, trade, market=None):
        timestamp = self.parse8601(trade['TradeTimestampUtc'])
        id = self.safe_string(trade, 'TradeGuid')
        orderId = self.safe_string(trade, 'OrderGuid')
        price = self.safe_float_2(trade, 'Price', 'SecondaryCurrencyTradePrice')
        amount = self.safe_float_2(trade, 'VolumeTraded', 'PrimaryCurrencyAmount')
        cost = None
        if price is not None:
            if amount is not None:
                cost = price * amount
        symbol = None
        if market is not None:
            symbol = market['symbol']
        side = self.safe_string(trade, 'OrderType')
        if side is not None:
            if side.find('Bid') >= 0:
                side = 'buy'
            elif side.find('Offer') >= 0:
                side = 'sell'
        return {
            'id': id,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': orderId,
            'type': None,
            'side': side,
            'takerOrMaker': None,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': None,
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'primaryCurrencyCode': market['baseId'],
            'secondaryCurrencyCode': market['quoteId'],
            'numberOfRecentTradesToRetrieve': 50,  # max = 50
        }
        response = await self.publicGetGetRecentTrades(self.extend(request, params))
        return self.parse_trades(response['Trades'], market, since, limit)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        await self.load_markets()
        market = self.market(symbol)
        capitalizedOrderType = self.capitalize(type)
        method = 'privatePostPlace' + capitalizedOrderType + 'Order'
        orderType = capitalizedOrderType
        orderType += 'Offer' if (side == 'sell') else 'Bid'
        request = self.ordered({
            'primaryCurrencyCode': market['baseId'],
            'secondaryCurrencyCode': market['quoteId'],
            'orderType': orderType,
        })
        if type == 'limit':
            request['price'] = price
        request['volume'] = amount
        response = await getattr(self, method)(self.extend(request, params))
        return {
            'info': response,
            'id': response['OrderGuid'],
        }

    async def cancel_order(self, id, symbol=None, params={}):
        await self.load_markets()
        request = {
            'orderGuid': id,
        }
        return await self.privatePostCancelOrder(self.extend(request, params))

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api] + '/' + path
        if api == 'public':
            if params:
                url += '?' + self.urlencode(params)
        else:
            self.check_required_credentials()
            nonce = self.nonce()
            auth = [
                url,
                'apiKey=' + self.apiKey,
                'nonce=' + str(nonce),
            ]
            keys = list(params.keys())
            for i in range(0, len(keys)):
                key = keys[i]
                value = str(params[key])
                auth.append(key + '=' + value)
            message = ','.join(auth)
            signature = self.hmac(self.encode(message), self.encode(self.secret))
            query = self.ordered({})
            query['apiKey'] = self.apiKey
            query['nonce'] = nonce
            query['signature'] = signature.upper()
            for i in range(0, len(keys)):
                key = keys[i]
                query[key] = params[key]
            body = self.json(query)
            headers = {'Content-Type': 'application/json'}
        return {'url': url, 'method': method, 'body': body, 'headers': headers}
