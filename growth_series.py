"""
growth_series: A class for modeling financial growth with compound interest and regular contributions.
"""

class growth_series:
    """
    A class to model the growth of a bank account with compound interest and regular contributions.

    Parameters:
    -----------
    rate : float
        Annual interest rate (e.g., 0.05 for 5%)
    compounds : str
        Compounding interval: 'daily', 'monthly', or 'annually'
    contribution : float, optional
        Initial contribution amount (default: 0)
    duration : float, optional
        Duration value (default: None)
    initial_principal : float, optional
        Starting principal amount (default: 0)
    """

    def __init__(self, rate, compounds, contribution=0, duration=None, initial_principal=0):
        self.rate = rate
        self.compounds = compounds.lower()
        self.contribution_amount = contribution
        self.contribution_interval = None
        self.duration_value = duration
        self.duration_unit = None
        self.initial_principal = initial_principal

        # Validate compounds parameter
        if self.compounds not in ['daily', 'monthly', 'annually']:
            raise ValueError("compounds must be 'daily', 'monthly', or 'annually'")

    # Contribution helper methods
    def daily(self, amount):
        """Set daily contribution amount."""
        self.contribution_amount = amount
        self.contribution_interval = 'daily'
        return self

    def monthly(self, amount):
        """Set monthly contribution amount."""
        self.contribution_amount = amount
        self.contribution_interval = 'monthly'
        return self

    def annual(self, amount):
        """Set annual contribution amount."""
        self.contribution_amount = amount
        self.contribution_interval = 'annually'
        return self

    # Duration helper methods
    def days(self, num_days):
        """Set duration in days."""
        self.duration_value = num_days
        self.duration_unit = 'days'
        return self

    def months(self, num_months):
        """Set duration in months."""
        self.duration_value = num_months
        self.duration_unit = 'months'
        return self

    def years(self, num_years):
        """Set duration in years."""
        self.duration_value = num_years
        self.duration_unit = 'years'
        return self

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
        if self.contribution_interval is None:
            return 0

        periods_per_year = self._get_compounding_periods_per_year()

        # Convert contribution to annual amount first
        if self.contribution_interval == 'daily':
            annual_contribution = self.contribution_amount * 365
        elif self.contribution_interval == 'monthly':
            annual_contribution = self.contribution_amount * 12
        elif self.contribution_interval == 'annually':
            annual_contribution = self.contribution_amount
        else:
            annual_contribution = 0

        # Convert to per-period contribution
        return annual_contribution / periods_per_year

    def _days_to_years(self, days):
        """Convert days to years."""
        return days / 365

    def _get_total_days(self):
        """Get the total duration in days."""
        if self.duration_value is None or self.duration_unit is None:
            raise ValueError("Duration not set. Use days(), months(), or years() to set duration.")

        if self.duration_unit == 'days':
            return self.duration_value
        elif self.duration_unit == 'months':
            return self.duration_value * 30.44  # Average days per month
        elif self.duration_unit == 'years':
            return self.duration_value * 365

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
    gs1 = growth_series(rate=0.05, compounds='monthly', initial_principal=1000)
    gs1.monthly(100).years(5)

    print(f"Example 1: Monthly compounding, $100/month, 5 years")
    print(f"Final value: ${gs1.get_final_value():.2f}")
    print(f"Value at 1 year: ${gs1.value_at(365):.2f}")
    print()

    # Example 2: Daily compounding, daily contributions, 10 years
    gs2 = growth_series(rate=0.06, compounds='daily', initial_principal=500)
    gs2.daily(5).years(10)

    print(f"Example 2: Daily compounding, $5/day, 10 years")
    print(f"Final value: ${gs2.get_final_value():.2f}")
    print(f"Value at 5 years: ${gs2.value_at(365*5):.2f}")
    print()

    # Example 3: Annual compounding, annual contributions, 1000 days
    gs3 = growth_series(rate=0.04, compounds='annually', initial_principal=2000)
    gs3.annual(500).days(1000)

    print(f"Example 3: Annual compounding, $500/year, 1000 days")
    print(f"Final value: ${gs3.get_final_value():.2f}")
    print(f"Value at 500 days: ${gs3.value_at(500):.2f}")
