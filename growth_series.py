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
    rate : float
        Annual interest rate (e.g., 0.05 for 5% APR)
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
        self.rate = rate
        self.compounds = compounds
        self.contribution = contribution
        self.duration = duration
        self.initial_principal = initial_principal

        # Validate compounds parameter
        if compounds not in ['monthly', 'annually']:
            raise ValueError("compounds must be 'monthly' or 'annually'")

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
    # Example 1: 5% annual rate with monthly compounding
    gs1 = growth_series(
        rate=0.05,
        compounds='monthly',
        contribution=monthly(100),
        duration=years(5),
        initial_principal=1000
    )

    print(f"Example 1: 5% annual rate, monthly compounding, $100/month, 5 years")
    print(f"Final value: ${gs1.get_final_value():.2f}")
    print(f"Value at 1 year: ${gs1.value_at(1):.2f}")
    print(f"Value at 2.5 years: ${gs1.value_at(2.5):.2f}")
    print()

    # Example 2: 6% annual rate with annual compounding
    gs2 = growth_series(
        rate=0.06,
        compounds='annually',
        contribution=annual(500),
        duration=years(10),
        initial_principal=2000
    )

    print(f"Example 2: 6% annual rate, annual compounding, $500/year, 10 years")
    print(f"Final value: ${gs2.get_final_value():.2f}")
    print(f"Value at 5 years: ${gs2.value_at(5):.2f}")
    print()

    # Example 3: No contributions, just growth
    gs3 = growth_series(
        rate=0.07,
        compounds='monthly',
        duration=months(36),
        initial_principal=5000
    )

    print(f"Example 3: 7% annual rate, monthly compounding, no contributions, 36 months")
    print(f"Final value: ${gs3.get_final_value():.2f}")
    print(f"Value at 1 year: ${gs3.value_at(1):.2f}")
