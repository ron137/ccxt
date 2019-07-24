<?php

namespace ccxt;

// PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
// https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

use Exception as Exception; // a common import

class bxinth extends Exchange {

    public function describe () {
        return array_replace_recursive (parent::describe (), array (
            'id' => 'bxinth',
            'name' => 'BX.in.th',
            'countries' => array ( 'TH' ), // Thailand
            'rateLimit' => 1500,
            'has' => array (
                'CORS' => false,
                'fetchTickers' => true,
                'fetchOpenOrders' => true,
            ),
            'urls' => array (
                'referral' => 'https://bx.in.th/ref/cYHknT/',
                'logo' => 'https://user-images.githubusercontent.com/1294454/27766412-567b1eb4-5ed7-11e7-94a8-ff6a3884f6c5.jpg',
                'api' => 'https://bx.in.th/api',
                'www' => 'https://bx.in.th',
                'doc' => 'https://bx.in.th/info/api',
            ),
            'api' => array (
                'public' => array (
                    'get' => array (
                        '', // ticker
                        'options',
                        'optionbook',
                        'orderbook',
                        'pairing',
                        'trade',
                        'tradehistory',
                    ),
                ),
                'private' => array (
                    'post' => array (
                        'balance',
                        'biller',
                        'billgroup',
                        'billpay',
                        'cancel',
                        'deposit',
                        'getorders',
                        'history',
                        'option-issue',
                        'option-bid',
                        'option-sell',
                        'option-myissue',
                        'option-mybid',
                        'option-myoptions',
                        'option-exercise',
                        'option-cancel',
                        'option-history',
                        'order',
                        'withdrawal',
                        'withdrawal-history',
                    ),
                ),
            ),
            'fees' => array (
                'trading' => array (
                    'taker' => 0.25 / 100,
                    'maker' => 0.25 / 100,
                ),
            ),
            'commonCurrencies' => array (
                'DAS' => 'DASH',
                'DOG' => 'DOGE',
                'LEO' => 'LeoCoin',
            ),
        ));
    }

    public function fetch_markets ($params = array ()) {
        $response = $this->publicGetPairing ($params);
        $keys = is_array($response) ? array_keys($response) : array();
        $result = array();
        for ($i = 0; $i < count ($keys); $i++) {
            $key = $keys[$i];
            $market = $response[$key];
            $id = $this->safe_string($market, 'pairing_id');
            $baseId = $this->safe_string($market, 'secondary_currency');
            $quoteId = $this->safe_string($market, 'primary_currency');
            $active = $this->safe_value($market, 'active');
            $base = $this->safe_currency_code($baseId);
            $quote = $this->safe_currency_code($quoteId);
            $symbol = $base . '/' . $quote;
            $result[] = array (
                'id' => $id,
                'symbol' => $symbol,
                'base' => $base,
                'quote' => $quote,
                'baseId' => $baseId,
                'quoteId' => $quoteId,
                'active' => $active,
                'info' => $market,
            );
        }
        return $result;
    }

    public function fetch_balance ($params = array ()) {
        $this->load_markets();
        $response = $this->privatePostBalance ($params);
        $balances = $this->safe_value($response, 'balance', array());
        $result = array( 'info' => $balances );
        $currencyIds = is_array($balances) ? array_keys($balances) : array();
        for ($i = 0; $i < count ($currencyIds); $i++) {
            $currencyId = $currencyIds[$i];
            $code = $this->safe_currency_code($currencyId);
            $balance = $this->safe_value($balances, $currencyId, array());
            $account = $this->account ();
            $account['free'] = $this->safe_float($balance, 'available');
            $account['total'] = $this->safe_float($balance, 'total');
            $result[$code] = $account;
        }
        return $this->parse_balance($result);
    }

    public function fetch_order_book ($symbol, $limit = null, $params = array ()) {
        $this->load_markets();
        $request = array (
            'pairing' => $this->market_id($symbol),
        );
        $response = $this->publicGetOrderbook (array_merge ($request, $params));
        return $this->parse_order_book($response);
    }

    public function parse_ticker ($ticker, $market = null) {
        $timestamp = $this->milliseconds ();
        $symbol = null;
        if ($market !== null) {
            $symbol = $market['symbol'];
        }
        $last = $this->safe_float($ticker, 'last_price');
        return array (
            'symbol' => $symbol,
            'timestamp' => $timestamp,
            'datetime' => $this->iso8601 ($timestamp),
            'high' => null,
            'low' => null,
            'bid' => $this->safe_float($ticker['orderbook']['bids'], 'highbid'),
            'bidVolume' => null,
            'ask' => $this->safe_float($ticker['orderbook']['asks'], 'highbid'),
            'askVolume' => null,
            'vwap' => null,
            'open' => null,
            'close' => $last,
            'last' => $last,
            'previousClose' => null,
            'change' => $this->safe_float($ticker, 'change'),
            'percentage' => null,
            'average' => null,
            'baseVolume' => $this->safe_float($ticker, 'volume_24hours'),
            'quoteVolume' => null,
            'info' => $ticker,
        );
    }

    public function fetch_tickers ($symbols = null, $params = array ()) {
        $this->load_markets();
        $response = $this->publicGet ($params);
        $result = array();
        $ids = is_array($response) ? array_keys($response) : array();
        for ($i = 0; $i < count ($ids); $i++) {
            $id = $ids[$i];
            $ticker = $response[$id];
            $market = $this->markets_by_id[$id];
            $symbol = $market['symbol'];
            $result[$symbol] = $this->parse_ticker($ticker, $market);
        }
        return $result;
    }

    public function fetch_ticker ($symbol, $params = array ()) {
        $this->load_markets();
        $market = $this->market ($symbol);
        $id = $market['id'];
        $request = array (
            'pairing' => $id,
        );
        $response = $this->publicGet (array_merge ($request, $params));
        $ticker = $this->safe_value($response, $id);
        return $this->parse_ticker($ticker, $market);
    }

    public function parse_trade ($trade, $market = null) {
        $date = $this->safe_string($trade, 'trade_date');
        $timestamp = null;
        if ($date !== null) {
            $timestamp = $this->parse8601 ($date . '+07:00'); // Thailand UTC+7 offset
        }
        $id = $this->safe_string($trade, 'trade_id');
        $orderId = $this->safe_string($trade, 'order_id');
        $type = null;
        $side = $this->safe_string($trade, 'trade_type');
        $price = $this->safe_float($trade, 'rate');
        $amount = $this->safe_float($trade, 'amount');
        $cost = null;
        if ($amount !== null) {
            if ($price !== null) {
                $cost = $amount * $price;
            }
        }
        $symbol = null;
        if ($market !== null) {
            $symbol = $market['symbol'];
        }
        return array (
            'id' => $id,
            'info' => $trade,
            'order' => $orderId,
            'timestamp' => $timestamp,
            'datetime' => $this->iso8601 ($timestamp),
            'symbol' => $symbol,
            'type' => $type,
            'side' => $side,
            'price' => $price,
            'takerOrMaker' => null,
            'amount' => $amount,
            'cost' => $cost,
            'fee' => null,
        );
    }

    public function fetch_trades ($symbol, $since = null, $limit = null, $params = array ()) {
        $this->load_markets();
        $market = $this->market ($symbol);
        $request = array (
            'pairing' => $market['id'],
        );
        $response = $this->publicGetTrade (array_merge ($request, $params));
        return $this->parse_trades($response['trades'], $market, $since, $limit);
    }

    public function create_order ($symbol, $type, $side, $amount, $price = null, $params = array ()) {
        $this->load_markets();
        $request = array (
            'pairing' => $this->market_id($symbol),
            'type' => $side,
            'amount' => $amount,
            'rate' => $price,
        );
        $response = $this->privatePostOrder (array_merge ($request, $params));
        $id = $this->safe_string($response, 'order_id');
        return array (
            'info' => $response,
            'id' => $id,
        );
    }

    public function cancel_order ($id, $symbol = null, $params = array ()) {
        $this->load_markets();
        $pairing = null; // TODO fixme
        $request = array (
            'order_id' => $id,
            'pairing' => $pairing,
        );
        return $this->privatePostCancel (array_merge ($request, $params));
    }

    public function parse_order ($order, $market = null) {
        $side = $this->safe_string($order, 'order_type');
        $symbol = null;
        if ($market === null) {
            $marketId = $this->safe_string($order, 'pairing_id');
            if (is_array($this->markets_by_id) && array_key_exists($marketId, $this->markets_by_id)) {
                $market = $this->markets_by_id[$marketId];
            }
        }
        if ($market !== null) {
            $symbol = $market['symbol'];
        }
        $timestamp = $this->parse8601 ($this->safe_string($order, 'date'));
        $price = $this->safe_float($order, 'rate');
        $amount = $this->safe_float($order, 'amount');
        $cost = null;
        if ($amount !== null) {
            if ($price !== null) {
                $cost = $price * $amount;
            }
        }
        $id = $this->safe_string($order, 'order_id');
        return array (
            'info' => $order,
            'id' => $id,
            'timestamp' => $timestamp,
            'datetime' => $this->iso8601 ($timestamp),
            'symbol' => $symbol,
            'type' => 'limit',
            'side' => $side,
            'price' => $price,
            'amount' => $amount,
            'cost' => $cost,
        );
    }

    public function fetch_open_orders ($symbol = null, $since = null, $limit = null, $params = array ()) {
        $this->load_markets();
        $request = array();
        $market = null;
        if ($symbol !== null) {
            $market = $this->market ($symbol);
            $request['pairing'] = $market['id'];
        }
        $response = $this->privatePostGetorders (array_merge ($request, $params));
        $orders = $this->parse_orders($response['orders'], $market, $since, $limit);
        return $this->filter_by_symbol($orders, $symbol);
    }

    public function sign ($path, $api = 'public', $method = 'GET', $params = array (), $headers = null, $body = null) {
        $url = $this->urls['api'] . '/';
        if ($path) {
            $url .= $path . '/';
        }
        if ($params) {
            $url .= '?' . $this->urlencode ($params);
        }
        if ($api === 'private') {
            $this->check_required_credentials();
            $nonce = $this->nonce ();
            $auth = $this->apiKey . (string) $nonce . $this->secret;
            $signature = $this->hash ($this->encode ($auth), 'sha256');
            $body = $this->urlencode (array_merge (array (
                'key' => $this->apiKey,
                'nonce' => $nonce,
                'signature' => $signature,
                // twofa => $this->twofa,
            ), $params));
            $headers = array (
                'Content-Type' => 'application/x-www-form-urlencoded',
            );
        }
        return array( 'url' => $url, 'method' => $method, 'body' => $body, 'headers' => $headers );
    }

    public function request ($path, $api = 'public', $method = 'GET', $params = array (), $headers = null, $body = null) {
        $response = $this->fetch2 ($path, $api, $method, $params, $headers, $body);
        if ($api === 'public') {
            return $response;
        }
        if (is_array($response) && array_key_exists('success', $response)) {
            if ($response['success']) {
                return $response;
            }
        }
        throw new ExchangeError($this->id . ' ' . $this->json ($response));
    }
}
