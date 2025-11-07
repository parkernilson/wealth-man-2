"""
growth_series: A class for modeling financial growth with compound interest and regular contributions.
"""


class Duration:
    """Represents a duration of time."""

    def __init__(self, value, unit):
        self.value = value
        self.unit = unit

    def to_years(self):
        """Convert duration to years."""
        if self.unit == 'years':
            return self.value
        elif self.unit == 'months':
            return self.value / 12
        else:
            raise ValueError(f"Unknown unit: {self.unit}")


class Contribution:
    """Represents a periodic contribution."""

    def __init__(self, amount, interval):
        self.amount = amount
        self.interval = interval

    def to_annual(self):
        """Convert contribution to annual amount."""
        if self.interval == 'monthly':
            return self.amount * 12
        elif self.interval == 'annually':
            return self.amount
        else:
            raise ValueError(f"Unknown interval: {self.interval}")


class Rate:
    """Represents an interest rate with its type (APR or APY)."""

    def __init__(self, value, rate_type):
        self.value = value
        self.rate_type = rate_type


# Helper functions for creating Rate objects
def apr(value):
    """Create a Rate object for APR (Annual Percentage Rate)."""
    return Rate(value, 'APR')


def apy(value):
    """Create a Rate object for APY (Annual Percentage Yield)."""
    return Rate(value, 'APY')


# Helper functions for creating Duration objects
def months(value):
    """Create a Duration object representing months."""
    return Duration(value, 'months')


def years(value):
    """Create a Duration object representing years."""
    return Duration(value, 'years')


# Helper functions for creating Contribution objects
def monthly(amount):
    """Create a Contribution object for monthly contributions."""
    return Contribution(amount, 'monthly')


def annual(amount):
    """Create a Contribution object for annual contributions."""
    return Contribution(amount, 'annually')


class growth_series:
    """
    A class to model the growth of a bank account with compound interest and regular contributions.

    Parameters:
    -----------
    rate : float or Rate
        Annual interest rate. Can be:
        - A float (defaults to APR), e.g., 0.05 for 5% APR
        - apr(0.05) for explicit APR
        - apy(0.0459) for APY (Annual Percentage Yield)
    compounds : str
        Either 'monthly' or 'annually'
    contribution : Contribution, optional
        A Contribution object created with monthly() or annual() (default: None)
    duration : Duration, optional
        A Duration object created with months() or years() (default: None)
    initial_principal : float, optional
        Starting principal amount (default: 0)
    """

    def __init__(self, rate, compounds, contribution=None, duration=None, initial_principal=0):
        self.compounds = compounds
        self.contribution = contribution
        self.duration = duration
        self.initial_principal = initial_principal

        # Validate compounds parameter
        if compounds not in ['monthly', 'annually']:
            raise ValueError("compounds must be 'monthly' or 'annually'")

        # Handle rate parameter - accept either float (default APR) or Rate object
        if isinstance(rate, Rate):
            rate_value = rate.value
            rate_type = rate.rate_type
        elif isinstance(rate, (int, float)):
            rate_value = rate
            rate_type = 'APR'
        else:
            raise TypeError("rate must be a number or Rate object (use apr() or apy())")

        self.rate_type = rate_type

        # Convert APY to APR if needed
        if rate_type == 'APY':
            # APY already accounts for compounding, so we need to back-calculate the APR
            # For monthly: APR = 12 * ((1 + APY)^(1/12) - 1)
            # For annual: APY = APR (no difference)
            if compounds == 'monthly':
                monthly_rate = (1 + rate_value) ** (1/12) - 1
                self.rate = monthly_rate * 12
            else:
                self.rate = rate_value
        else:
            self.rate = rate_value

    def _get_compounding_periods_per_year(self):
        """Get the number of compounding periods per year."""
        return 12 if self.compounds == 'monthly' else 1

    def _get_rate_per_period(self):
        """Get the interest rate per compounding period."""
        n = self._get_compounding_periods_per_year()
        return self.rate / n

    def _get_contribution_per_period(self):
        """Convert contribution to match the compounding period."""
        if self.contribution is None:
            return 0

        n = self._get_compounding_periods_per_year()
        annual_contribution = self.contribution.to_annual()
        return annual_contribution / n

    def value_at(self, t_years):
        """
        Calculate the account value at time t (in years) from the start.

        Parameters:
        -----------
        t_years : float
            Number of years from the start

        Returns:
        --------
        float
            Account value at time t
        """
        if t_years < 0:
            raise ValueError("t_years must be non-negative")

        # Get compounding parameters
        n = self._get_compounding_periods_per_year()
        rate_per_period = self._get_rate_per_period()
        pmt = self._get_contribution_per_period()

        # Calculate number of periods
        num_periods = n * t_years

        # If rate is 0, use simple calculation
        if rate_per_period == 0:
            return self.initial_principal + (pmt * num_periods)

        # Compound interest with regular contributions formula:
        # FV = P(1 + r)^n + PMT × [((1 + r)^n - 1) / r]

        # Future value of principal
        fv_principal = self.initial_principal * ((1 + rate_per_period) ** num_periods)

        # Future value of contributions (annuity)
        if pmt > 0:
            fv_contributions = pmt * (((1 + rate_per_period) ** num_periods - 1) / rate_per_period)
        else:
            fv_contributions = 0

        return fv_principal + fv_contributions

    def get_final_value(self):
        """
        Calculate the final account value at the end of the duration.

        Returns:
        --------
        float
            Final account value
        """
        if self.duration is None:
            raise ValueError("Duration not set.")

        total_years = self.duration.to_years()
        return self.value_at(total_years)


# Example usage
if __name__ == "__main__":
    # Example 1: Simple float (defaults to APR)
    gs1 = growth_series(
        rate=0.05,  # Defaults to APR
        compounds='monthly',
        contribution=monthly(100),
        duration=years(5),
        initial_principal=1000
    )

    print(f"Example 1: 5% (default APR), monthly compounding, $100/month, 5 years")
    print(f"Final value: ${gs1.get_final_value():.2f}")
    print(f"Value at 1 year: ${gs1.value_at(1):.2f}")
    print()

    # Example 2: Explicit APR using apr() helper
    gs2 = growth_series(
        rate=apr(0.05),
        compounds='monthly',
        contribution=monthly(100),
        duration=years(5),
        initial_principal=1000
    )

    print(f"Example 2: apr(0.05), monthly compounding, $100/month, 5 years")
    print(f"Final value: ${gs2.get_final_value():.2f}")
    print(f"Value at 1 year: ${gs2.value_at(1):.2f}")
    print()

    # Example 3: HYSA using APY (what banks advertise)
    gs3 = growth_series(
        rate=apy(0.0459),  # Bank's advertised APY
        compounds='monthly',
        contribution=monthly(100),
        duration=years(5),
        initial_principal=1000
    )

    print(f"Example 3: apy(0.0459) HYSA, monthly compounding, $100/month, 5 years")
    print(f"Final value: ${gs3.get_final_value():.2f}")
    print(f"Value at 1 year: ${gs3.value_at(1):.2f}")
    print()

    # Example 4: Brokerage account (simple annual)
    gs4 = growth_series(
        rate=0.08,  # 8% expected return
        compounds='annually',
        contribution=annual(6000),
        duration=years(30),
        initial_principal=10000
    )

    print(f"Example 4: 8% return, annual compounding, $6000/year, 30 years")
    print(f"Final value: ${gs4.get_final_value():.2f}")
    print(f"Value at 10 years: ${gs4.value_at(10):.2f}")
    print()

    # Example 5: Compare APR vs APY
    print("Comparison: apr(0.045) vs apy(0.0459)")

    gs_apr = growth_series(
        rate=apr(0.045),
        compounds='monthly',
        duration=years(1),
        initial_principal=10000
    )

    gs_apy = growth_series(
        rate=apy(0.0459),
        compounds='monthly',
        duration=years(1),
        initial_principal=10000
    )

    print(f"$10,000 at apr(0.045) after 1 year: ${gs_apr.get_final_value():.2f}")
    print(f"$10,000 at apy(0.0459) after 1 year: ${gs_apy.get_final_value():.2f}")
