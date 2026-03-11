# Options P&L Calculator - Backend Server
# Deployed on Render.com

import os
import math
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
CORS(app, origins="*")


def safe_float(val):
    try:
        f = float(val)
        return None if math.isnan(f) or math.isinf(f) else f
    except (TypeError, ValueError):
        return None


def safe_int(val):
    try:
        f = float(val)
        return None if math.isnan(f) else int(f)
    except (TypeError, ValueError):
        return None


def get_earnings_dates(ticker):
    last_earnings_date = None
    next_earnings_date = None
    try:
        import requests
        from datetime import timezone
        now_ts = datetime.utcnow().timestamp()

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://finance.yahoo.com",
        }

        # Fetch 2 years of quarterly data to get past and future earnings
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=3mo&range=2y&includePrePost=false"
        resp = requests.get(url, headers=headers, timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            events = data.get("chart", {}).get("result", [{}])[0].get("events", {})
            earnings_events = events.get("earnings", {})

            if earnings_events:
                all_dates = []
                for k, v in earnings_events.items():
                    ts = v.get("date")
                    if ts:
                        try:
                            all_dates.append(float(ts))
                        except Exception:
                            pass

                past = sorted([t for t in all_dates if t < now_ts], reverse=True)
                future = sorted([t for t in all_dates if t >= now_ts])

                if past:
                    last_earnings_date = datetime.utcfromtimestamp(past[0]).strftime("%Y-%m-%d")
                if future:
                    next_earnings_date = datetime.utcfromtimestamp(future[0]).strftime("%Y-%m-%d")

        # If no future earnings in chart, try quoteSummary calendarEvents
        if not next_earnings_date:
            url2 = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=calendarEvents"
            resp2 = requests.get(url2, headers=headers, timeout=10)
            if resp2.status_code == 200:
                cal = resp2.json().get("quoteSummary", {}).get("result", [{}])[0].get("calendarEvents", {})
                earnings = cal.get("earnings", {})
                ed_list = earnings.get("earningsDate", [])
                for ed in ed_list:
                    ts = ed.get("raw")
                    if ts and float(ts) > now_ts:
                        next_earnings_date = datetime.utcfromtimestamp(float(ts)).strftime("%Y-%m-%d")
                        break

    except Exception:
        pass

    return last_earnings_date, next_earnings_date


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/quote/<ticker>")
def get_quote(ticker):
    try:
        ticker = ticker.upper().strip()
        stock = yf.Ticker(ticker)
        info = stock.info

        price = safe_float(
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
        )

        if not price:
            return jsonify({"error": f"Could not find price for {ticker}"}), 404

        iv = None
        try:
            expirations = stock.options
            if expirations:
                chain = stock.option_chain(expirations[0])
                calls = chain.calls.copy()
                if not calls.empty and "impliedVolatility" in calls.columns:
                    calls["distance"] = abs(calls["strike"] - price)
                    atm = calls.sort_values("distance").iloc[0]
                    iv_raw = safe_float(atm["impliedVolatility"])
                    if iv_raw and iv_raw > 0:
                        iv = round(iv_raw * 100, 1)
        except Exception:
            pass

        name = info.get("shortName") or info.get("longName") or ticker

        return jsonify({
            "ticker": ticker,
            "name": name,
            "price": round(price, 2),
            "iv": iv,
            "currency": info.get("currency", "USD"),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/premium/<ticker>/<option_type>/<expiration>/<strike>")
def get_premium(ticker, option_type, expiration, strike):
    try:
        ticker = ticker.upper().strip()
        strike_requested = float(strike)
        stock = yf.Ticker(ticker)

        expirations = stock.options
        if not expirations:
            return jsonify({"error": f"No options data found for {ticker}"}), 404

        try:
            req_date = datetime.strptime(expiration, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": f"Invalid date format: {expiration}"}), 400

        exp_dates = []
        for e in expirations:
            try:
                exp_dates.append(datetime.strptime(e, "%Y-%m-%d"))
            except ValueError:
                continue

        if not exp_dates:
            return jsonify({"error": "Could not parse any expiration dates"}), 500

        nearest = min(exp_dates, key=lambda d: abs((d - req_date).days))
        nearest_str = nearest.strftime("%Y-%m-%d")
        days_diff = abs((nearest - req_date).days)

        chain = stock.option_chain(nearest_str)
        df = chain.calls if option_type.lower() == "call" else chain.puts

        if df is None or df.empty:
            return jsonify({"error": f"No {option_type} contracts found for {ticker} expiring {nearest_str}"}), 404

        df = df.copy()
        df["distance"] = abs(df["strike"] - strike_requested)
        row = df.sort_values("distance").iloc[0]

        actual_strike = safe_float(row["strike"])
        bid = safe_float(row.get("bid"))
        ask = safe_float(row.get("ask"))
        last = safe_float(row.get("lastPrice"))
        iv_raw = safe_float(row.get("impliedVolatility"))
        iv = round(iv_raw * 100, 1) if iv_raw and iv_raw > 0 else None
        volume = safe_int(row.get("volume")) or 0
        open_interest = safe_int(row.get("openInterest")) or 0

        if bid is not None and ask is not None and bid > 0 and ask > 0:
            mid = round((bid + ask) / 2, 2)
        elif last is not None and last > 0:
            mid = round(last, 2)
            bid = None
            ask = None
        else:
            return jsonify({"error": f"No valid price for {ticker} {option_type} strike exp {nearest_str}"}), 404

        return jsonify({
            "ticker": ticker,
            "option_type": option_type,
            "expiration": nearest_str,
            "expiration_requested": expiration,
            "days_diff": days_diff,
            "strike": actual_strike,
            "strike_requested": strike_requested,
            "bid": bid,
            "ask": ask,
            "mid": mid,
            "last": last,
            "iv": iv,
            "volume": volume,
            "open_interest": open_interest,
        })

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route("/screen", methods=["POST"])
def screen():
    try:
        body = request.get_json()
        tickers = [t.upper().strip() for t in body.get("tickers", [])]
        expiration = body.get("expiration")
        min_ann = float(body.get("min_ann_return", 0))
        min_called = float(body.get("min_called_return", 0))

        if not tickers or not expiration:
            return jsonify({"error": "tickers and expiration are required"}), 400

        try:
            req_date = datetime.strptime(expiration, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400

        results = []

        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info

                price = safe_float(
                    info.get("currentPrice")
                    or info.get("regularMarketPrice")
                    or info.get("previousClose")
                )
                if not price:
                    results.append({"ticker": ticker, "error": "Could not fetch price"})
                    continue

                name = info.get("shortName") or info.get("longName") or ticker

                # Earnings dates
                last_earnings_date, earnings_date = get_earnings_dates(ticker)
                earnings_warning = False
                if earnings_date:
                    try:
                        ed_dt = datetime.strptime(earnings_date, "%Y-%m-%d")
                        if ed_dt <= req_date:
                            earnings_warning = True
                    except Exception:
                        pass

                if not earnings_date and last_earnings_date:
                    try:
                        last_dt = datetime.strptime(last_earnings_date, "%Y-%m-%d")
                        estimated = last_dt + timedelta(days=91)
                        if estimated > datetime.now():
                            earnings_date = estimated.strftime("%Y-%m-%d") + " (est)"
                            if estimated <= req_date:
                                earnings_warning = True
                    except Exception:
                        pass

                # IV rank
                iv_rank_label = None
                iv_rank_pct = None
                try:
                    import numpy as np
                    hist = stock.history(period="90d")
                    if hist is not None and len(hist) > 10:
                        closes = hist["Close"].values
                        log_returns = np.diff(np.log(closes))
                        hv_30 = float(np.std(log_returns[-30:]) * np.sqrt(252) * 100)
                        atm_strike = round(price / 5) * 5
                        try:
                            chain_iv = stock.option_chain(stock.options[0])
                            calls_iv = chain_iv.calls.copy()
                            calls_iv["distance"] = abs(calls_iv["strike"] - atm_strike)
                            atm_row = calls_iv.sort_values("distance").iloc[0]
                            current_iv = safe_float(atm_row.get("impliedVolatility"))
                            if current_iv:
                                current_iv_pct = current_iv * 100
                                ratio = current_iv_pct / hv_30 if hv_30 > 0 else 1
                                iv_rank_pct = round(current_iv_pct, 1)
                                if ratio >= 2.0:
                                    iv_rank_label = "Extreme"
                                elif ratio >= 1.5:
                                    iv_rank_label = "High"
                                elif ratio >= 1.15:
                                    iv_rank_label = "Elevated"
                                else:
                                    iv_rank_label = "Normal"
                        except Exception:
                            pass
                except Exception:
                    pass

                # Options chain
                expirations = stock.options
                if not expirations:
                    results.append({"ticker": ticker, "error": "No options available"})
                    continue

                exp_dates = []
                for e in expirations:
                    try:
                        exp_dates.append(datetime.strptime(e, "%Y-%m-%d"))
                    except ValueError:
                        continue

                nearest = min(exp_dates, key=lambda d: abs((d - req_date).days))
                nearest_str = nearest.strftime("%Y-%m-%d")
                dte = (nearest - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).days
                if dte < 1:
                    dte = 1

                chain = stock.option_chain(nearest_str)
                calls = chain.calls.copy()

                if calls.empty:
                    results.append({"ticker": ticker, "error": "No calls available"})
                    continue

                calls = calls[calls["strike"] >= price * 0.98]

                strike_results = []
                for _, row in calls.iterrows():
                    strike = safe_float(row["strike"])
                    bid = safe_float(row.get("bid"))
                    ask = safe_float(row.get("ask"))
                    last = safe_float(row.get("lastPrice"))
                    iv = safe_float(row.get("impliedVolatility"))
                    volume = safe_int(row.get("volume")) or 0
                    oi = safe_int(row.get("openInterest")) or 0

                    if bid and bid > 0:
                        premium = bid
                    elif last and last > 0:
                        premium = last
                    else:
                        continue

                    if premium < 0.01:
                        continue

                    capital = (price - premium) * 100
                    if capital <= 0:
                        continue

                    trade_return = (premium * 100 / capital) * 100
                    ann_return = trade_return * (365 / dte)
                    stock_gain = max(strike - price, 0)
                    total_profit = (premium + stock_gain) * 100
                    called_trade_return = (total_profit / capital) * 100
                    called_ann_return = called_trade_return * (365 / dte)
                    breakeven = price - premium

                    if ann_return < min_ann or called_ann_return < min_called:
                        continue

                    strike_results.append({
                        "strike": strike,
                        "bid": bid,
                        "ask": safe_float(row.get("ask")),
                        "premium": round(premium, 2),
                        "breakeven": round(breakeven, 2),
                        "ann_return": round(ann_return, 1),
                        "called_ann_return": round(called_ann_return, 1),
                        "trade_return": round(trade_return, 2),
                        "called_trade_return": round(called_trade_return, 2),
                        "stock_gain": round(stock_gain, 2),
                        "total_profit": round(total_profit, 2),
                        "volume": volume,
                        "open_interest": oi,
                        "iv": round(iv * 100, 1) if iv else None,
                        "capital": round(capital, 2),
                    })

                if not strike_results:
                    results.append({
                        "ticker": ticker,
                        "name": name,
                        "price": price,
                        "expiration": nearest_str,
                        "dte": dte,
                        "last_earnings_date": last_earnings_date,
                        "earnings_date": earnings_date,
                        "earnings_warning": earnings_warning,
                        "iv_rank_label": iv_rank_label,
                        "iv_rank_pct": iv_rank_pct,
                        "strikes": [],
                        "error": "No strikes met your criteria"
                    })
                    continue

                strike_results.sort(key=lambda x: x["ann_return"], reverse=True)
                top3 = strike_results[:3]

                results.append({
                    "ticker": ticker,
                    "name": name,
                    "price": round(price, 2),
                    "expiration": nearest_str,
                    "dte": dte,
                    "last_earnings_date": last_earnings_date,
                    "earnings_date": earnings_date,
                    "earnings_warning": earnings_warning,
                    "iv_rank_label": iv_rank_label,
                    "iv_rank_pct": iv_rank_pct,
                    "strikes": top3
                })

            except Exception as e:
                results.append({"ticker": ticker, "error": str(e)})

        return jsonify({"results": results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/debug/earnings/<ticker>")
def debug_earnings(ticker):
    ticker = ticker.upper().strip()
    result = {"ticker": ticker}
    try:
        last, next_ed = get_earnings_dates(ticker)
        result["last_earnings_date"] = last
        result["next_earnings_date"] = next_ed
        result["status"] = "ok"
    except Exception as e:
        result["error"] = str(e)
    return jsonify(result)


port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
