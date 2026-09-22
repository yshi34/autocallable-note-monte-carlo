from time import perf_counter

from autocallable_note import AutocallableNote


def main() -> None:

    # Model parameters
    r = 0.0375
    q = 0.01
    sigma = 0.25
    S_0 = 100.0

    # Product parameters
    N = 100.0
    trading_days = 252
    n_traj = 1_000_000
    autocall_ratio = 1.00
    knock_in_ratio = 0.70
    c = 0.10

    separator = "=" * 60

    print(separator)
    print("AUTOCALLABLE NOTE MODEL INPUTS")
    print(separator)

    print(f"Initial stock price (S_0): {S_0:.2f}")
    print(f"Notional principal (N):    {N:.2f}")
    print(f"Risk-free rate (r):        {r:.2%}")
    print(f"Dividend yield (q):        {q:.2%}")
    print(f"Annualised volatility:     {sigma:.2%}")
    print(f"Annual coupon rate (c):    {c:.2%}")
    print(f"Autocall ratio:            {autocall_ratio:.2%}")
    print(f"Knock-in ratio:            {knock_in_ratio:.2%}")
    print(f"Trading days:              {trading_days:,}")
    print(f"Monte Carlo paths:         {n_traj:,}")

    note = AutocallableNote(
        r=r,
        q=q,
        sigma=sigma,
        S_0=S_0,
        N=N,
        trading_days=trading_days,
        n_traj=n_traj,
        autocall_ratio=autocall_ratio,
        knock_in_ratio=knock_in_ratio,
        c=c,
    )

    print("\nRunning the simulation...")

    start_time = perf_counter()

    note.gbm_simulator()

    runtime = perf_counter() - start_time

    note.summary()

    print(f"\nSimulated paths: {n_traj:,}")
    print(f"Runtime:         {runtime:.2f} seconds")


if __name__ == "__main__":
    main()