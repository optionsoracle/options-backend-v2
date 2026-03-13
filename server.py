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


FINNHUB_KEY = "d6omcq1r01qi5kh3ggagd6omcq1r01qi5kh3ggb0"

def get_earnings_dates(ticker):
    last_earnings_date = None
    next_earnings_date = None
    try:
        import requests as req_lib
        now = datetime.utcnow()

        # Next earnings - Finnhub earnings calendar (next 90 days)
        try:
            from_date = now.strftime("%Y-%m-%d")
            to_date = (now + timedelta(days=90)).strftime("%Y-%m-%d")
            url = f"https://finnhub.io/api/v1/calendar/earnings?from={from_date}&to={to_date}&symbol={ticker}&token={FINNHUB_KEY}"
            resp = req_lib.get(url, timeout=8)
            if resp.status_code == 200:
                items = resp.json().get("earningsCalendar", [])
                for item in items:
                    d = item.get("date", "")
                    if d:
                        try:
                            ed_dt = datetime.strptime(d, "%Y-%m-%d")
                            if ed_dt >= now.replace(hour=0, minute=0, second=0):
                                next_earnings_date = d
                                break
                        except Exception:
                            pass
        except Exception:
            pass

        # Last earnings - look back 180 days
        try:
            from_date2 = (now - timedelta(days=180)).strftime("%Y-%m-%d")
            to_date2 = now.strftime("%Y-%m-%d")
            url2 = f"https://finnhub.io/api/v1/calendar/earnings?from={from_date2}&to={to_date2}&symbol={ticker}&token={FINNHUB_KEY}"
            resp2 = req_lib.get(url2, timeout=8)
            if resp2.status_code == 200:
                items2 = resp2.json().get("earningsCalendar", [])
                past = [i for i in items2 if i.get("date", "") < now.strftime("%Y-%m-%d")]
                if past:
                    past.sort(key=lambda x: x.get("date", ""), reverse=True)
                    last_earnings_date = past[0].get("date")
        except Exception:
            pass

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
        exp_date_from = body.get("exp_date_from")
        exp_date_to = body.get("exp_date_to")
        min_ann = float(body.get("min_ann_return", 0))
        min_called = float(body.get("min_called_return", 0))
        strategy = body.get("strategy", "cc").lower()

        range_mode = bool(exp_date_from and exp_date_to)

        if not tickers or (not expiration and not range_mode):
            return jsonify({"error": "tickers and expiration are required"}), 400

        if range_mode:
            try:
                date_from = datetime.strptime(exp_date_from, "%Y-%m-%d")
                date_to = datetime.strptime(exp_date_to, "%Y-%m-%d")
                req_date = date_to  # used for earnings warning check
            except ValueError:
                return jsonify({"error": "Invalid date format"}), 400
        else:
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
                week_52_high = safe_float(info.get("fiftyTwoWeekHigh"))
                week_52_low = safe_float(info.get("fiftyTwoWeekLow"))

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

                # Select expirations to scan
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

                if range_mode:
                    # All expirations within the date window
                    exps_to_scan = [(d, d.strftime("%Y-%m-%d")) for d in exp_dates if date_from <= d <= date_to]
                    if not exps_to_scan:
                        results.append({"ticker": ticker, "error": f"No expirations found between {exp_date_from} and {exp_date_to}"})
                        continue
                else:
                    nearest = min(exp_dates, key=lambda d: abs((d - req_date).days))
                    exps_to_scan = [(nearest, nearest.strftime("%Y-%m-%d"))]

                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                all_strike_results = []

                for exp_dt, nearest_str in exps_to_scan:
                    dte = (exp_dt - today).days
                    if dte < 1:
                        dte = 1

                    try:
                        chain = stock.option_chain(nearest_str)
                    except Exception:
                        continue

                    if strategy == "csp":
                        puts = chain.puts.copy()
                        if puts.empty:
                            continue
                        puts = puts[(puts["strike"] >= price * 0.70) & (puts["strike"] <= price * 1.001)]
                        for _, row in puts.iterrows():
                            strike = safe_float(row["strike"])
                            bid = safe_float(row.get("bid"))
                            ask = safe_float(row.get("ask"))
                            last = safe_float(row.get("lastPrice"))
                            iv = safe_float(row.get("impliedVolatility"))
                            volume = safe_int(row.get("volume")) or 0
                            oi = safe_int(row.get("openInterest")) or 0
                            if bid and bid > 0 and ask and ask > 0:
                                premium = (bid + ask) / 2
                            elif bid and bid > 0:
                                premium = bid
                            elif ask and ask > 0:
                                premium = ask / 2
                            elif last and last > 0:
                                premium = last
                            else:
                                continue
                            if premium < 0.01:
                                continue
                            capital = (strike - premium) * 100
                            if capital <= 0:
                                continue
                            trade_return = (premium * 100 / capital) * 100
                            ann_return = trade_return * (365 / dte)
                            if ann_return < min_ann:
                                continue
                            breakeven = strike - premium
                            discount_pct = round((price - breakeven) / price * 100, 2)
                            discount_dollar = round(price - breakeven, 2)
                            distance_pct = round((strike - price) / price * 100, 2)
                            in_the_money = strike > price
                            prob_profit = None
                            try:
                                if iv and iv > 0 and dte > 0:
                                    t = dte / 365.0
                                    d2 = (math.log(price / strike) + (-0.5 * iv**2) * t) / (iv * math.sqrt(t))
                                    n_d2 = 0.5 * (1.0 + math.erf(d2 / math.sqrt(2)))
                                    prob_profit = round(n_d2 * 100, 1)
                            except Exception:
                                pass
                            all_strike_results.append({
                                "strike": strike, "premium": round(premium, 2),
                                "breakeven": round(breakeven, 2),
                                "discount_pct": discount_pct, "discount_dollar": discount_dollar,
                                "ann_return": round(ann_return, 1), "trade_return": round(trade_return, 2),
                                "volume": volume, "open_interest": oi,
                                "iv": round(iv * 100, 1) if iv else None,
                                "capital": round(capital, 2), "prob_profit": prob_profit,
                                "distance_pct": distance_pct, "in_the_money": in_the_money,
                                "expiration": nearest_str, "dte": dte,
                            })

                    else:
                        calls = chain.calls.copy()
                        if calls.empty:
                            continue
                        calls = calls[calls["strike"] >= price * 0.98]
                        for _, row in calls.iterrows():
                            strike = safe_float(row["strike"])
                            bid = safe_float(row.get("bid"))
                            ask = safe_float(row.get("ask"))
                            last = safe_float(row.get("lastPrice"))
                            iv = safe_float(row.get("impliedVolatility"))
                            volume = safe_int(row.get("volume")) or 0
                            oi = safe_int(row.get("openInterest")) or 0
                            if bid and bid > 0 and ask and ask > 0:
                                premium = (bid + ask) / 2
                            elif bid and bid > 0:
                                premium = bid
                            elif ask and ask > 0:
                                premium = ask / 2
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
                            if ann_return < min_ann or called_ann_return < min_called:
                                continue
                            breakeven = price - premium
                            distance_pct = round((strike - price) / price * 100, 2)
                            in_the_money = strike < price
                            prob_profit = None
                            try:
                                if iv and iv > 0 and dte > 0:
                                    t = dte / 365.0
                                    d2 = (math.log(price / strike) + (-0.5 * iv**2) * t) / (iv * math.sqrt(t))
                                    n_d2 = 0.5 * (1.0 + math.erf(d2 / math.sqrt(2)))
                                    prob_profit = round((1.0 - n_d2) * 100, 1)
                            except Exception:
                                pass
                            all_strike_results.append({
                                "strike": strike, "premium": round(premium, 2),
                                "breakeven": round(breakeven, 2),
                                "ann_return": round(ann_return, 1),
                                "called_ann_return": round(called_ann_return, 1),
                                "trade_return": round(trade_return, 2),
                                "called_trade_return": round(called_trade_return, 2),
                                "stock_gain": round(stock_gain, 2),
                                "total_profit": round(total_profit, 2),
                                "volume": volume, "open_interest": oi,
                                "iv": round(iv * 100, 1) if iv else None,
                                "capital": round(capital, 2), "prob_profit": prob_profit,
                                "distance_pct": distance_pct, "in_the_money": in_the_money,
                                "expiration": nearest_str, "dte": dte,
                            })

                if not all_strike_results:
                    results.append({
                        "ticker": ticker, "name": name, "price": price,
                        "expiration": exps_to_scan[-1][1], "dte": (exps_to_scan[-1][0] - today).days,
                        "last_earnings_date": last_earnings_date,
                        "earnings_date": earnings_date, "earnings_warning": earnings_warning,
                        "iv_rank_label": iv_rank_label, "iv_rank_pct": iv_rank_pct,
                        "strikes": [], "error": "No strikes met your criteria",
                        "strategy": strategy
                    })
                    continue

                # For CSP: rank OTM strikes first (by ann_return), then ITM after.
                # ITM puts have artificially inflated ann_return and are lower quality trades.
                if strategy == "csp":
                    otm = sorted([s for s in all_strike_results if not s["in_the_money"]], key=lambda x: x["ann_return"], reverse=True)
                    itm = sorted([s for s in all_strike_results if s["in_the_money"]], key=lambda x: x["ann_return"], reverse=True)
                    best = (otm + itm)[:10]
                else:
                    all_strike_results.sort(key=lambda x: x["ann_return"], reverse=True)
                    best = all_strike_results[:10]

                best_exp = best[0]["expiration"]
                best_dte = best[0]["dte"]
                results.append({
                    "ticker": ticker, "name": name,
                    "price": round(price, 2),
                    "week_52_high": week_52_high, "week_52_low": week_52_low,
                    "expiration": best_exp, "dte": best_dte,
                    "last_earnings_date": last_earnings_date,
                    "earnings_date": earnings_date, "earnings_warning": earnings_warning,
                    "iv_rank_label": iv_rank_label, "iv_rank_pct": iv_rank_pct,
                    "strikes": best,
                    "strategy": strategy
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
        last, nxt = get_earnings_dates(ticker)
        result["last_earnings_date"] = last
        result["next_earnings_date"] = nxt
        result["status"] = "ok"
    except Exception as e:
        result["error"] = str(e)
    return jsonify(result)


@app.route("/debug/csp/<ticker>")
def debug_csp(ticker):
    ticker = ticker.upper().strip()
    try:
        stock = yf.Ticker(ticker)
        price = safe_float(stock.info.get("currentPrice") or stock.info.get("regularMarketPrice"))
        expirations = stock.options
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        date_from = today + timedelta(days=7)
        date_to = today + timedelta(days=90)
        out = {"ticker": ticker, "price": price, "expirations_in_range": [], "top_otm_by_exp": []}
        for e in expirations:
            try:
                d = datetime.strptime(e, "%Y-%m-%d")
            except ValueError:
                continue
            if not (date_from <= d <= date_to):
                continue
            dte = max((d - today).days, 1)
            out["expirations_in_range"].append(e)
            try:
                chain = stock.option_chain(e)
                puts = chain.puts.copy()
                puts = puts[(puts["strike"] >= price * 0.70) & (puts["strike"] <= price * 1.001)]
                best = None
                for _, row in puts.iterrows():
                    strike = safe_float(row["strike"])
                    if strike >= price:
                        continue
                    bid = safe_float(row.get("bid"))
                    last = safe_float(row.get("lastPrice"))
                    premium = bid if (bid and bid > 0) else (last if (last and last > 0) else None)
                    if not premium:
                        continue
                    capital = (strike - premium) * 100
                    if capital <= 0:
                        continue
                    trade_return = (premium * 100 / capital) * 100
                    ann_return = trade_return * (365 / dte)
                    if best is None or ann_return > best["ann_return"]:
                        best = {"expiration": e, "dte": dte, "strike": strike, "premium": round(premium,2), "ann_return": round(ann_return,1)}
                if best:
                    out["top_otm_by_exp"].append(best)
            except Exception as ex:
                out["top_otm_by_exp"].append({"expiration": e, "error": str(ex)})
        out["top_otm_by_exp"].sort(key=lambda x: x.get("ann_return", 0), reverse=True)
        return jsonify(out)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
