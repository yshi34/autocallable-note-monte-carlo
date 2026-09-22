import numpy as np
import tqdm


class AutocallableNote:
    """
    Price a single-underlying autocallable note using Monte Carlo simulation.

    The underlying follows a geometric Brownian motion under the
    risk-neutral measure. The note has quarterly autocall observations,
    daily knock-in monitoring, and a one-year maturity.

    Simulation results are stored as instance attributes after
    ``gbm_simulator`` has been called.
    """

    def __init__(
        self,
        r: float = 0.0375,
        q: float = 0.01,
        sigma: float = 0.25,
        S_0: float = 100.0,
        N: float = 100.0,
        trading_days: int = 252,
        n_traj: int = 1_000_000,
        autocall_ratio: float = 1.00,
        knock_in_ratio: float = 0.70,
        c: float = 0.1,
    ):
        """
        Initialise the model and product parameters.

        Parameters
        ----------
        r : float
            Continuously compounded annual risk-free interest rate.
        q : float
            Continuous annual dividend yield of the underlying.
        sigma : float
            Annualised volatility of the underlying.
        S_0 : float
            Initial underlying price or reference level.
        N : float
            Notional principal of the note.
        trading_days : int
            Number of trading days in the one-year product lifetime.
        n_traj : int
            Number of Monte Carlo trajectories.
        autocall_ratio : float
            Autocall barrier as a proportion of the initial price.
        knock_in_ratio : float
            Knock-in barrier as a proportion of the initial price.
        c : float
            Annual coupon rate paid by the note.
        """

        self.r = r
        self.q = q
        self.sigma = sigma
        self.S_0 = S_0
        self.N = N
        self.trading_days = trading_days
        self.n_traj = n_traj
        self.autocall_ratio = autocall_ratio
        self.knock_in_ratio = knock_in_ratio
        self.c = c

    def gbm_simulator(self):

        """
        Simulate the underlying and value the autocallable note.

        The method uses the exact lognormal transition of geometric
        Brownian motion. The knock-in condition is monitored daily,
        while the autocall condition is checked every 63 trading days.

        For each trajectory, the method calculates the payoff, payment
        time, and discounted payoff. It then estimates the present value,
        Monte Carlo standard error, and 95% confidence interval.

        Results are stored as attributes of the class instance.
        """

        # Copy instance parameters to local variables for readability.
        r = self.r
        q = self.q
        sigma = self.sigma
        S_0 = self.S_0
        N = self.N
        trading_days = self.trading_days
        n_traj = self.n_traj
        autocall_ratio = self.autocall_ratio
        knock_in_ratio = self.knock_in_ratio
        c = self.c

        # Use a fixed seed to make the simulation reproducible.
        rng = np.random.default_rng(seed=42)

        # Convert barrier ratios into absolute underlying price levels.
        B_ki = knock_in_ratio * S_0
        B_ac = autocall_ratio * S_0

        # Use one trading day as the simulation time step.
        t_step = 1 / trading_days
        # Store the current underlying price for each trajectory.
        S_list = np.full(n_traj, S_0, dtype=float)

        # Track the state and cash flow of every trajectory.
        knock_in = np.zeros(n_traj, dtype=bool)
        alive = np.ones(n_traj, dtype=bool)
        payoff = np.zeros(n_traj)
        payment_time = np.zeros(n_traj)

        # Simulate the underlying one trading day at a time.
        for t in tqdm.tqdm(range(1, trading_days + 1)):

            # Count trajectories that have not yet been autocalled.
            n_alive = np.count_nonzero(alive)

            # Stop early if every trajectory has been autocalled.
            if n_alive == 0:
                break

            # Generate one independent normal shock per active trajectory.
            noise = rng.standard_normal(n_alive)

            # Apply the exact one-step GBM transition under the risk-neutral measure.
            S_list[alive] = S_list[alive] * np.exp(
                (r - q - 0.5 * sigma**2) * t_step
                + sigma * np.sqrt(t_step) * noise
            )

            # Record whether each active trajectory has ever crossed the knock-in barrier.
            knock_in = knock_in | (alive & (S_list <= B_ki))

            # Check the autocall condition every quarter.
            if t % 63 == 0:
                autocalled = alive & (S_list >= B_ac)

                # Pay principal plus the coupon accrued up to the autocall observation date.
                payoff[autocalled] = (c * t / trading_days + 1) * N

                # Store the payment time in years.
                payment_time[autocalled] = (t / trading_days)

                # Autocalled trajectories are no longer active.
                alive[autocalled] = False

        # Separate surviving trajectories according to whether the knock-in barrier was breached.
        mature_safe = alive & (knock_in == False)
        mature_knocked_in = alive & (knock_in == True)

        # Return principal and the full coupon if no knock-in occurred.
        payoff[mature_safe] = N * (1 + c)

        # Apply the underlying loss if the trajectory was knocked in.
        payoff[mature_knocked_in] = (S_list[mature_knocked_in] / S_0 * N)

        # All remaining active trajectories pay at the one-year maturity.
        payment_time[alive] = 1

        # Store path-level simulation results.
        self.payoff = payoff
        self.payment_time = payment_time
        self.knock_in = knock_in
        self.alive = alive

        # Discount every cash flow back to the valuation date.
        discounted_payoff = payoff * np.exp(-r * payment_time)
        self.discounted_payoff = discounted_payoff

        # Estimate the risk-neutral present value.
        self.estimated_value = np.mean(discounted_payoff)

        # Estimate the Monte Carlo standard error.
        self.standard_error = (np.std(discounted_payoff, ddof=1)/ np.sqrt(n_traj))

        # Construct an approximate 95% confidence interval.
        self.confidence_interval = (
            float(self.estimated_value - 1.96 * self.standard_error),
            float(self.estimated_value + 1.96 * self.standard_error),
        )


    def summary(self):
        """
        Print valuation, payoff statistics, and event probabilities.
        """

        if not hasattr(self, "estimated_value"):
            raise RuntimeError(
                "Run gbm_simulator() before summary()."
            )

        n_paths = self.payoff.size

        # Discounted payoff statistics.
        discounted_mean = np.mean(self.discounted_payoff)
        discounted_std = np.std(self.discounted_payoff,ddof=1)
        discounted_se = discounted_std / np.sqrt(n_paths)

        discounted_ci = (discounted_mean - 1.96 * discounted_se,discounted_mean + 1.96 * discounted_se)

        # Undiscounted payoff statistics.
        payoff_mean = np.mean(self.payoff)
        payoff_std = np.std(self.payoff,ddof=1)
        payoff_se = payoff_std / np.sqrt(n_paths)

        payoff_ci = (payoff_mean - 1.96 * payoff_se,payoff_mean + 1.96 * payoff_se)

        separator = "-" * 60

        print("\nAUTOCALLABLE NOTE MONTE CARLO RESULTS")
        print("=" * 60)

        print("\nDISCOUNTED PAYOFF (PRESENT VALUE)")
        print(separator)
        print(f"Expected discounted payoff: {discounted_mean:.4f}")
        print(f"Standard deviation:         {discounted_std:.4f}")
        print(f"Minimum:                    {self.discounted_payoff.min():.4f}")
        print(f"Maximum:                    {self.discounted_payoff.max():.4f}")
        print(f"Monte Carlo standard error: {discounted_se:.4f}")
        print(
            f"95% confidence interval:    "
            f"[{discounted_ci[0]:.4f}, "
            f"{discounted_ci[1]:.4f}]"
        )

        print("\nUNDISCOUNTED PAYOFF")
        print(separator)
        print(f"Expected payoff:             {payoff_mean:.4f}")
        print(f"Standard deviation:          {payoff_std:.4f}")
        print(f"Minimum:                     {self.payoff.min():.4f}")
        print(f"Maximum:                     {self.payoff.max():.4f}")
        print(f"Monte Carlo standard error:  {payoff_se:.4f}")
        print(
            f"95% confidence interval:     "
            f"[{payoff_ci[0]:.4f}, "
            f"{payoff_ci[1]:.4f}]"
        )

        print("\nPATH STATISTICS")
        print(separator)
        print(
            f"Knock-in probability:        "
            f"{self.knock_in.mean():.2%}"
        )
        print(
            f"Early-autocall probability:  "
            f"{np.mean(self.payment_time < 1.0):.2%}"
        )
        print(
            f"Maturity-payment probability:"
            f"  {np.mean(self.payment_time == 1.0):.2%}"
        )

        print("=" * 60)