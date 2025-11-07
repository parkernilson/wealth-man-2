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


class CompoundingInterval:
    """Represents how often interest compounds."""

    def __init__(self, interval):
        self.interval = interval

    def periods_per_year(self):
        """Get the number of compounding periods per year."""
        if self.interval == 'daily':
            return 365
        elif self.interval == 'monthly':
            return 12
        elif self.interval == 'annually':
            return 1
        else:
            raise ValueError(f"Unknown interval: {self.interval}")


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


class Rate:
    """
    Represents an interest rate with a specific time period.

    - Annual rates are treated as NOMINAL (APR): divided by compounding periods
    - Monthly/daily rates are EFFECTIVE: the actual rate applied per period
    """

    def __init__(self, value, period):
        self.value = value
        self.period = period


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


# Helper functions that work for CompoundingInterval, Contribution, and Rate
def daily(amount=None, rate=None):
    """
    Create a CompoundingInterval, Contribution, or Rate object for daily intervals.

    If called without arguments: returns CompoundingInterval for daily compounding.
    If called with amount: returns Contribution for daily contributions.
    If called with rate: returns Rate for daily interest rate.
    """
    if amount is not None and rate is not None:
        raise ValueError("Cannot specify both amount and rate")

    if rate is not None:
        return Rate(rate, 'daily')
    elif amount is not None:
        return Contribution(amount, 'daily')
    else:
        return CompoundingInterval('daily')


def monthly(amount=None, rate=None):
    """
    Create a CompoundingInterval, Contribution, or Rate object for monthly intervals.

    If called without arguments: returns CompoundingInterval for monthly compounding.
    If called with amount: returns Contribution for monthly contributions.
    If called with rate: returns Rate for monthly interest rate.
    """
    if amount is not None and rate is not None:
        raise ValueError("Cannot specify both amount and rate")

    if rate is not None:
        return Rate(rate, 'monthly')
    elif amount is not None:
        return Contribution(amount, 'monthly')
    else:
        return CompoundingInterval('monthly')


def annual(amount=None, rate=None):
    """
    Create a CompoundingInterval, Contribution, or Rate object for annual intervals.

    If called without arguments: returns CompoundingInterval for annual compounding.
    If called with amount: returns Contribution for annual contributions.
    If called with rate: returns Rate for annual interest rate.
    """
    if amount is not None and rate is not None:
        raise ValueError("Cannot specify both amount and rate")

    if rate is not None:
        return Rate(rate, 'annually')
    elif amount is not None:
        return Contribution(amount, 'annually')
    else:
        return CompoundingInterval('annually')


class growth_series:
    """
    A class to model the growth of a bank account with compound interest and regular contributions.

    Parameters:
    -----------
    rate : Rate
        A Rate object created with daily(rate=X), monthly(rate=X), or annual(rate=X) functions
        - Annual rates are NOMINAL (APR): 5% annual with monthly compounding means 5%/12 per month
        - Monthly/daily rates are EFFECTIVE: 0.5% monthly means exactly 0.5% applied each month
    compounds : CompoundingInterval
        A CompoundingInterval object created with daily(), monthly(), or annual() functions (no argument)
    contribution : Contribution, optional
        A Contribution object created with daily(amount=X), monthly(amount=X), or annual(amount=X) (default: None)
    duration : Duration, optional
        A Duration object created with days(), months(), or years() functions (default: None)
    initial_principal : float, optional
        Starting principal amount (default: 0)
    """

    def __init__(self, rate, compounds, contribution=None, duration=None, initial_principal=0):
        # Store the original rate object
        if not isinstance(rate, Rate):
            raise TypeError("rate must be a Rate object. Use daily(rate=X), monthly(rate=X), or annual(rate=X).")

        if not isinstance(compounds, CompoundingInterval):
            raise TypeError("compounds must be a CompoundingInterval object. Use daily(), monthly(), or annual() without arguments.")

        self.rate_obj = rate
        self.compounds = compounds
        self.contribution = contribution
        self.duration = duration
        self.initial_principal = initial_principal

    def _get_compounding_periods_per_year(self):
        """Get the number of compounding periods per year."""
        return self.compounds.periods_per_year()

    def _get_rate_per_period(self):
        """
        Convert the rate to match the compounding period.

        - Annual rates are treated as NOMINAL (APR): divide by periods
        - Monthly/daily rates are treated as EFFECTIVE: use compound conversion
        """
        rate_value = self.rate_obj.value
        rate_period = self.rate_obj.period
        compound_interval = self.compounds.interval

        # If they match, use the rate directly
        if rate_period == compound_interval:
            return rate_value

        # Annual rate → other period: use nominal rate (divide)
        if rate_period == 'annually':
            periods_per_year = self._get_compounding_periods_per_year()
            return rate_value / periods_per_year

        # Non-annual rate → convert using compound formula
        # First determine periods per year for source and target
        source_periods = {
            'daily': 365,
            'monthly': 12,
            'annually': 1
        }[rate_period]

        target_periods = self._get_compounding_periods_per_year()

        # Convert: (1 + rate)^(source/target) - 1
        # E.g., monthly (0.5%) to daily: (1.005)^(12/365) - 1 ≈ 0.0001638 per day
        # Because: (1 + r_daily)^(365/12) = 1 + r_monthly
        return (1 + rate_value) ** (source_periods / target_periods) - 1

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
        rate_per_period = self._get_rate_per_period()  # rate per compounding period
        pmt = self._get_contribution_per_period()  # contribution per period

        # Calculate number of periods
        num_periods = n * t_years

        # If rate is 0, use simple calculation
        if rate_per_period == 0:
            return self.initial_principal + (pmt * num_periods)

        # Compound interest with regular contributions formula:
        # FV = P(1 + r_period)^(num_periods) + PMT × [((1 + r_period)^(num_periods) - 1) / r_period]

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
    # Example 1: Annual rate (NOMINAL) with monthly compounding
    # 5% APR means 5%/12 = 0.4167% applied each month
    gs1 = growth_series(
        rate=annual(rate=0.05),  # 5% APR (nominal annual rate)
        compounds=monthly(),  # Compound monthly
        contribution=monthly(amount=100),
        duration=years(5),
        initial_principal=1000
    )

    print(f"Example 1: 5% APR with monthly compounding, $100/month, 5 years")
    print(f"Final value: ${gs1.get_final_value():.2f}")
    print(f"Value at 3 months: ${gs1.value_at(90):.2f}")
    print(f"Value at 1 year: ${gs1.value_at(365):.2f}")
    print()

    # Example 2: Effective monthly rate with monthly compounding
    # 0.5% effective monthly rate means exactly 0.5% is applied each month
    gs2 = growth_series(
        rate=monthly(rate=0.005),  # 0.5% effective monthly rate
        compounds=monthly(),  # Compound monthly
        contribution=monthly(amount=100),
        duration=years(5),
        initial_principal=1000
    )

    print(f"Example 2: 0.5% effective monthly rate, monthly compounding, $100/month, 5 years")
    print(f"Final value: ${gs2.get_final_value():.2f}")
    print(f"Value at 3 months: ${gs2.value_at(90):.2f}")
    print(f"Value at 1 year: ${gs2.value_at(365):.2f}")
    print()

    # Example 3: Effective monthly rate with daily compounding
    # 0.5% monthly converted to daily: (1.005)^(1/30.44) - 1 per day
    gs3 = growth_series(
        rate=monthly(rate=0.005),  # 0.5% effective monthly rate
        compounds=daily(),  # Compound daily (converts rate automatically)
        contribution=daily(amount=5),
        duration=years(10),
        initial_principal=500
    )

    print(f"Example 3: 0.5% monthly rate, daily compounding, $5/day, 10 years")
    print(f"Final value: ${gs3.get_final_value():.2f}")
    print(f"Value at 5 years: ${gs3.value_at(365*5):.2f}")
