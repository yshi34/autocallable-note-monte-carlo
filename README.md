# Monte Carlo Valuation of an Autocallable Note

## Overview

This project prices a single-underlying autocallable note using
risk-neutral Monte Carlo simulation.

The underlying asset follows geometric Brownian motion. The note has
quarterly autocall observations, daily knock-in monitoring, and a
one-year maturity.

The program reports both:

- the undiscounted expected payoff;
- the discounted risk-neutral expected payoff, interpreted as the
  model present value.

## Product Specification

The baseline product has the following terms:

| Parameter | Value |
|---|---:|
| Initial underlying level | 100 |
| Notional principal | 100 |
| Maturity | 1 year |
| Annual coupon | 10% |
| Autocall barrier | 100% of initial level |
| Knock-in barrier | 70% of initial level |
| Autocall observation | Quarterly |
| Knock-in monitoring | Daily |

If the underlying is at or above the autocall barrier on a quarterly
observation date, the note terminates and pays:

\[
N(1+c\tau)
\]

If the note reaches maturity without a knock-in event, it pays:

\[
N(1+cT)
\]

If the note reaches maturity after a knock-in event, it pays:

\[
N\frac{S_T}{S_0}
\]

## Model

Under the risk-neutral measure, the underlying follows:

\[
dS_t = (r-q)S_t\,dt+\sigma S_t\,dW_t^{\mathbb Q}
\]

The simulation uses the exact GBM transition:

\[
S_{t+\Delta t}
=
S_t
\exp\left[
\left(r-q-\frac{1}{2}\sigma^2\right)\Delta t
+
\sigma\sqrt{\Delta t}Z
\right]
\]

where:

\[
Z\sim N(0,1)
\]

The model present value is estimated as:

\[
V_0
=
\mathbb E^{\mathbb Q}
\left[
e^{-r\theta}P
\right]
\]

where \(\theta\) is the path-dependent payment time.

## Project Structure

```text
AutocallableNote_payoff/
├── autocallable_note.py
├── main.py
├── usecase.ipynb
├── requirements.txt
├── README.md
└── .gitignore
```

- `autocallable_note.py` contains the pricing class.
- `main.py` runs the reproducible baseline example.
- `usecase.ipynb` contains the convergence test and an optional
  market-data example.

## Installation

Python 3.10 or later is recommended.

```bash
pip install -r requirements.txt
```

## Running the Baseline Model

```bash
python main.py
```

The baseline model uses a fixed random seed to make the result
reproducible.

On the development machine, one million Monte Carlo paths run in
approximately five seconds.

## Example Result

Using one million Monte Carlo paths and the baseline parameters:

```text
Estimated present value: approximately 98.57 per 100 notional
Monte Carlo standard error: approximately 0.012
```

Exact output is printed by `main.py`.

## Convergence Analysis

`usecase.ipynb` examines the estimated present value for increasing
numbers of Monte Carlo paths.

The Monte Carlo standard error is expected to decrease at the rate:

\[
O(M^{-1/2})
\]

where \(M\) is the number of simulated paths.

## Optional Market-Data Example

The notebook also demonstrates how to obtain market-based inputs for
a US equity:

- latest available price from Yahoo Finance;
- annualised historical volatility from daily log returns;
- trailing dividend yield;
- one-year US Treasury rate as a risk-free-rate proxy.

The baseline program does not require network access.

Historical volatility, trailing dividends, and the Treasury yield are
simplified proxies rather than a full market calibration.

## Model Limitations

The model assumes:

- constant volatility;
- constant interest and dividend rates;
- no jumps in the underlying price;
- no volatility smile or skew;
- no issuer credit risk or funding adjustment;
- daily rather than continuous knock-in monitoring.

A production implementation would normally use the implied-volatility
surface, a calibrated interest-rate curve, forward dividend estimates,
and an issuer credit adjustment.