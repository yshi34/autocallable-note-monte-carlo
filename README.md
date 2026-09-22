# Monte Carlo Valuation of an Autocallable Note

## Overview

This project values a single-underlying autocallable note using
risk-neutral Monte Carlo simulation.

The underlying asset follows geometric Brownian motion (GBM). The note
has quarterly autocall observations, daily knock-in monitoring, and a
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

Let:

- $N$ denote the notional principal;
- $c$ denote the annual coupon rate;
- $\tau$ denote the autocall time;
- $T$ denote the maturity;
- $S_0$ denote the initial underlying level;
- $S_T$ denote the underlying level at maturity.

If the underlying is at or above the autocall barrier on a quarterly
observation date, the note terminates and pays:

$$
N(1+c\tau)
$$

If the note reaches maturity without an autocall or a knock-in event,
it pays:

$$
N(1+cT)
$$

If the note reaches maturity without an autocall and a knock-in event
has occurred, it pays:

$$
N\frac{S_T}{S_0}
$$

## Model

Under the risk-neutral measure, the underlying follows:

$$
dS_t=(r-q)S_t\,dt+\sigma S_t\,dW_t^{\mathbb Q}
$$

where:

- $r$ is the continuously compounded risk-free interest rate;
- $q$ is the continuous dividend yield;
- $\sigma$ is the annualised volatility;
- $W_t^{\mathbb Q}$ is a Brownian motion under the risk-neutral
  measure.

The simulation uses the exact GBM transition:

$$S_{t+\Delta t} = S_t \exp\left[\left(r-q-\frac{1}{2}\sigma^2\right)\Delta t + \sigma\sqrt{\Delta t}\,Z \right] $$

where:

$$
Z\sim N(0,1)
$$

The random variables $Z$ are independent across time steps and
simulation paths.

For each simulated path, the payoff is discounted according to its
path-dependent payment time. The model present value is estimated as:

$$V_0 = \mathbb E^{\mathbb Q} \left[e^{-r\theta}P\right]$$

where $\theta$ is the payment time and $P$ is the corresponding payoff.

## Project Structure

```text
autocallable-note-monte-carlo/
├── autocallable_note.py
├── main.py
├── usecase.ipynb
├── requirements.txt
├── README.md
└── .gitignore
```

- `autocallable_note.py` contains the pricing class.
- `main.py` runs the reproducible baseline example.
- `usecase.ipynb` contains the convergence analysis and an optional
  market-data example.

## Installation

Python 3.10 or later is recommended.

```bash
pip install -r requirements.txt
```

## Running the Baseline Model

Run the model from the repository directory:

```bash
python main.py
```

The baseline model uses a fixed random seed to make the result
reproducible.

On the development machine, one million Monte Carlo paths run in
approximately five seconds.

## Example Result

Using one million Monte Carlo paths, a fixed random seed of 42, and the
baseline parameters:

```text
Estimated present value:        approximately 98.57 per 100 notional
Monte Carlo standard error:     approximately 0.012
95% confidence interval:        approximately [98.55, 98.60]
```

The exact output, including undiscounted payoff statistics and event
probabilities, is printed by `main.py`.

The confidence interval measures Monte Carlo sampling uncertainty. It
does not capture model or parameter uncertainty.

## Convergence Analysis

`usecase.ipynb` examines the estimated present value for increasing
numbers of Monte Carlo paths.

The Monte Carlo standard error is expected to decrease at the rate:

$$
O\left(M^{-1/2}\right)
$$

where $M$ is the number of simulated paths.

The convergence analysis plots the estimated present value together
with its 95% Monte Carlo confidence interval.

## Optional Market-Data Example

The notebook also demonstrates how to obtain market-based inputs for a
U.S. equity:

- the latest available price from Yahoo Finance;
- annualised historical volatility estimated from daily log returns;
- trailing dividend yield;
- the one-year U.S. Treasury rate as a risk-free-rate proxy.

The baseline program does not require network access. The market-data
example is optional and requires an internet connection.

Historical volatility, trailing dividends, and the Treasury yield are
simplified proxies rather than a full market calibration. In
particular, historical volatility is used as a proxy for risk-neutral
implied volatility.

## Model Limitations

The model assumes:

- constant volatility;
- constant interest and dividend rates;
- no jumps in the underlying price;
- no volatility smile or skew;
- no issuer credit risk or funding adjustment;
- daily rather than continuous knock-in monitoring;
- historical volatility as a proxy for implied volatility in the
  optional market-data example.

A production implementation would normally use an implied-volatility
surface, a calibrated discount curve, forward dividend estimates, and
an issuer credit adjustment.
