"""
growth_series: A class for modeling financial growth with compound interest and regular contributions.
"""


class Duration:
    """Represents a duration of time."""

    def __init__(self, value, unit):
        self.value = value
        self.unit = unit

    def to_days(self):
        """Convert duration to days."""
        if self.unit == 'days':
            return self.value
        elif self.unit == 'months':
            return self.value * 30.44  # Average days per month
        elif self.unit == 'years':
            return self.value * 365
        else:
            raise ValueError(f"Unknown unit: {self.unit}")


class Contribution:
    """Represents a periodic contribution."""

    def __init__(self, amount, interval):
        self.amount = amount
        self.interval = interval

    def to_annual(self):
        """Convert contribution to annual amount."""
        if self.interval == 'daily':
            return self.amount * 365
        elif self.interval == 'monthly':
            return self.amount * 12
        elif self.interval == 'annually':
            return self.amount
        else:
            raise ValueError(f"Unknown interval: {self.interval}")


# Helper functions for creating Duration objects
def days(value):
    """Create a Duration object representing days."""
    return Duration(value, 'days')


def months(value):
    """Create a Duration object representing months."""
    return Duration(value, 'months')


def years(value):
    """Create a Duration object representing years."""
    return Duration(value, 'years')


# Helper functions for creating Contribution objects
def daily(amount):
    """Create a Contribution object for daily contributions."""
    return Contribution(amount, 'daily')


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
        Annual interest rate (e.g., 0.05 for 5%)
    compounds : str
        Compounding interval: 'daily', 'monthly', or 'annually'
    contribution : Contribution, optional
        A Contribution object created with daily(), monthly(), or annual() functions (default: None)
    duration : Duration, optional
        A Duration object created with days(), months(), or years() functions (default: None)
    initial_principal : float, optional
        Starting principal amount (default: 0)
    """

    def __init__(self, rate, compounds, contribution=None, duration=None, initial_principal=0):
        self.rate = rate
        self.compounds = compounds.lower()
        self.contribution = contribution
        self.duration = duration
        self.initial_principal = initial_principal

        # Validate compounds parameter
        if self.compounds not in ['daily', 'monthly', 'annually']:
            raise ValueError("compounds must be 'daily', 'monthly', or 'annually'")

    def _get_compounding_periods_per_year(self):
        """Get the number of compounding periods per year."""
        if self.compounds == 'daily':
            return 365
        elif self.compounds == 'monthly':
            return 12
        elif self.compounds == 'annually':
            return 1

    def _get_contribution_per_period(self):
        """Convert contribution to match the compounding period."""
        if self.contribution is None:
            return 0

        periods_per_year = self._get_compounding_periods_per_year()
        annual_contribution = self.contribution.to_annual()

        # Convert to per-period contribution
        return annual_contribution / periods_per_year

    def _days_to_years(self, days):
        """Convert days to years."""
        return days / 365

    def _get_total_days(self):
        """Get the total duration in days."""
        if self.duration is None:
            raise ValueError("Duration not set.")

        return self.duration.to_days()

    def value_at(self, t):
        """
        Calculate the account value at day t from the start.

        Parameters:
        -----------
        t : float
            Number of days from the start

        Returns:
        --------
        float
            Account value at day t
        """
        if t < 0:
            raise ValueError("t must be non-negative")

        # Convert t (days) to years
        t_years = self._days_to_years(t)

        # Get compounding parameters
        n = self._get_compounding_periods_per_year()  # compounds per year
        r = self.rate  # annual rate
        pmt = self._get_contribution_per_period()  # contribution per period

        # Calculate number of periods
        num_periods = n * t_years

        # If rate is 0, use simple calculation
        if r == 0:
            return self.initial_principal + (pmt * num_periods)

        # Compound interest with regular contributions formula:
        # FV = P(1 + r/n)^(nt) + PMT × [((1 + r/n)^(nt) - 1) / (r/n)]
        rate_per_period = r / n

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
        total_days = self._get_total_days()
        return self.value_at(total_days)


# Example usage
if __name__ == "__main__":
    # Example 1: Monthly compounding, monthly contributions, 5 years
    gs1 = growth_series(
        rate=0.05,
        compounds='monthly',
        contribution=monthly(100),
        duration=years(5),
        initial_principal=1000
    )

    print(f"Example 1: Monthly compounding, $100/month, 5 years")
    print(f"Final value: ${gs1.get_final_value():.2f}")
    print(f"Value at 1 year: ${gs1.value_at(365):.2f}")
    print()

    # Example 2: Daily compounding, daily contributions, 10 years
    gs2 = growth_series(
        rate=0.06,
        compounds='daily',
        contribution=daily(5),
        duration=years(10),
        initial_principal=500
    )

    print(f"Example 2: Daily compounding, $5/day, 10 years")
    print(f"Final value: ${gs2.get_final_value():.2f}")
    print(f"Value at 5 years: ${gs2.value_at(365*5):.2f}")
    print()

    # Example 3: Annual compounding, annual contributions, 1000 days
    gs3 = growth_series(
        rate=0.04,
        compounds='annually',
        contribution=annual(500),
        duration=days(1000),
        initial_principal=2000
    )

    print(f"Example 3: Annual compounding, $500/year, 1000 days")
    print(f"Final value: ${gs3.get_final_value():.2f}")
    print(f"Value at 500 days: ${gs3.value_at(500):.2f}")
