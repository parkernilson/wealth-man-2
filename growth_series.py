"""
growth_series: A class for modeling financial growth with compound interest and regular contributions.
"""

import matplotlib.pyplot as plt
import numpy as np


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
    rate : Rate
        Annual interest rate. Must use either:
        - apr(0.05) for APR (Annual Percentage Rate)
        - apy(0.0459) for APY (Annual Percentage Yield)
    compounds : str
        Either 'monthly' or 'annually'
    contribution : Contribution, optional
        A Contribution object created with monthly() or annual() (default: None)
    duration : Duration, optional
        A Duration object created with months() or years() (default: None)

    Note:
    -----
    Principal is not set in the constructor. Instead, it is provided when calling
    value_at() or get_final_value() methods.
    """

    def __init__(self, rate, compounds, contribution=None, duration=None):
        self.compounds = compounds
        self.contribution = contribution
        self.duration = duration

        # Validate compounds parameter
        if compounds not in ['monthly', 'annually']:
            raise ValueError("compounds must be 'monthly' or 'annually'")

        # Handle rate parameter - require Rate object
        if isinstance(rate, Rate):
            rate_value = rate.value
            rate_type = rate.rate_type
        else:
            raise TypeError("rate must be created with apr() or apy() helper functions")

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

    def value_at(self, t_years, principal):
        """
        Calculate the account value at time t (in years) from the start.

        Parameters:
        -----------
        t_years : float
            Number of years from the start
        principal : float
            Starting principal amount

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
            return principal + (pmt * num_periods)

        # Compound interest with regular contributions formula:
        # FV = P(1 + r)^n + PMT × [((1 + r)^n - 1) / r]

        # Future value of principal
        fv_principal = principal * ((1 + rate_per_period) ** num_periods)

        # Future value of contributions (annuity)
        if pmt > 0:
            fv_contributions = pmt * (((1 + rate_per_period) ** num_periods - 1) / rate_per_period)
        else:
            fv_contributions = 0

        return fv_principal + fv_contributions

    def get_final_value(self, principal):
        """
        Calculate the final account value at the end of the duration.

        Parameters:
        -----------
        principal : float
            Starting principal amount

        Returns:
        --------
        float
            Final account value
        """
        if self.duration is None:
            raise ValueError("Duration not set.")

        total_years = self.duration.to_years()
        return self.value_at(total_years, principal)


class growth_scenario:
    """
    A class to model multiple sequential growth periods (series).

    This class chains together multiple growth_series objects, where the final value
    from one series becomes the principal for the next series.

    Parameters:
    -----------
    initial_principal : float
        Starting principal amount for the first series
    series_list : list of growth_series
        List of growth_series objects to apply sequentially

    Example:
    --------
    # Scenario: Start with $10k, grow at 5% for 5 years, then 7% for 10 years
    scenario = growth_scenario(
        initial_principal=10000,
        series_list=[
            growth_series(rate=apr(0.05), compounds='monthly', duration=years(5)),
            growth_series(rate=apr(0.07), compounds='monthly', duration=years(10))
        ]
    )
    final_value = scenario.get_final_value()
    """

    def __init__(self, initial_principal, series_list):
        self.initial_principal = initial_principal
        self.series_list = series_list

    def get_final_value(self):
        """
        Calculate the final value after all growth series are applied.

        Returns:
        --------
        float
            Final value after all series
        """
        principal = self.initial_principal

        for series in self.series_list:
            principal = series.get_final_value(principal)

        return principal

    def get_series_values(self):
        """
        Calculate the final value for each series in the scenario.

        Returns:
        --------
        list of float
            Final values after each series in order
        """
        principal = self.initial_principal
        values = []

        for series in self.series_list:
            principal = series.get_final_value(principal)
            values.append(principal)

        return values

    def value_at_series(self, series_index, t_years):
        """
        Calculate the value at a specific time within a specific series.

        Parameters:
        -----------
        series_index : int
            Index of the series (0-based)
        t_years : float
            Number of years from the start of that series

        Returns:
        --------
        float
            Account value at that point
        """
        if series_index < 0 or series_index >= len(self.series_list):
            raise ValueError(f"series_index must be between 0 and {len(self.series_list) - 1}")

        # Calculate principal at the start of the target series
        principal = self.initial_principal
        for i in range(series_index):
            principal = self.series_list[i].get_final_value(principal)

        # Calculate value at time t within the target series
        return self.series_list[series_index].value_at(t_years, principal)

    def plot(self, num_points=500, show_series_transitions=True, title=None, figsize=(10, 6)):
        """
        Plot the growth scenario over time using matplotlib.

        Parameters:
        -----------
        num_points : int, optional
            Number of points to plot (default: 500)
        show_series_transitions : bool, optional
            Whether to show vertical lines at series transitions (default: True)
        title : str, optional
            Custom title for the plot (default: auto-generated)
        figsize : tuple, optional
            Figure size (width, height) in inches (default: (10, 6))

        Returns:
        --------
        tuple
            (fig, ax) - matplotlib figure and axes objects
        """
        # Calculate total duration and series boundaries
        cumulative_years = []
        current_time = 0

        for series in self.series_list:
            if series.duration is None:
                raise ValueError("All series must have a duration set to plot")
            current_time += series.duration.to_years()
            cumulative_years.append(current_time)

        total_years = cumulative_years[-1]

        # Generate time points
        time_points = np.linspace(0, total_years, num_points)
        values = []

        # Calculate value at each time point
        for t in time_points:
            # Find which series this time point belongs to
            cumulative = 0
            for i, series in enumerate(self.series_list):
                series_duration = series.duration.to_years()
                if t <= cumulative + series_duration:
                    # Time t is within this series
                    t_within_series = t - cumulative
                    value = self.value_at_series(i, t_within_series)
                    values.append(value)
                    break
                cumulative += series_duration

        # Create the plot
        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(time_points, values, linewidth=2, label='Portfolio Value')

        # Add series transition markers
        if show_series_transitions and len(self.series_list) > 1:
            series_values = self.get_series_values()
            for i, (year, value) in enumerate(zip(cumulative_years[:-1], series_values[:-1])):
                ax.axvline(x=year, color='gray', linestyle='--', alpha=0.5, linewidth=1)
                ax.plot(year, value, 'ro', markersize=6, label=f'End of Series {i+1}' if i == 0 else None)

        # Format the plot
        ax.set_xlabel('Time (years)', fontsize=12)
        ax.set_ylabel('Portfolio Value ($)', fontsize=12)

        # Auto-generate title if not provided
        if title is None:
            title = f'Growth Scenario: ${self.initial_principal:,.0f} over {total_years:.1f} years'
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

        # Add grid
        ax.grid(True, alpha=0.3)

        # Add legend
        if show_series_transitions and len(self.series_list) > 1:
            ax.legend(loc='upper left')

        # Add final value annotation
        final_value = self.get_final_value()
        ax.annotate(f'Final: ${final_value:,.2f}',
                   xy=(total_years, final_value),
                   xytext=(-60, -20),
                   textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

        plt.tight_layout()

        return fig, ax


# Example usage
if __name__ == "__main__":
    # Example 1: Using APR
    gs1 = growth_series(
        rate=apr(0.05),
        compounds='monthly',
        contribution=monthly(100),
        duration=years(5)
    )

    principal1 = 1000
    print(f"Example 1: apr(0.05), monthly compounding, $100/month, 5 years, $1000 principal")
    print(f"Final value: ${gs1.get_final_value(principal1):.2f}")
    print(f"Value at 1 year: ${gs1.value_at(1, principal1):.2f}")
    print()

    # Example 2: HYSA using APY (what banks advertise)
    gs2 = growth_series(
        rate=apy(0.0459),  # Bank's advertised APY
        compounds='monthly',
        contribution=monthly(100),
        duration=years(5)
    )

    principal2 = 1000
    print(f"Example 2: apy(0.0459) HYSA, monthly compounding, $100/month, 5 years, $1000 principal")
    print(f"Final value: ${gs2.get_final_value(principal2):.2f}")
    print(f"Value at 1 year: ${gs2.value_at(1, principal2):.2f}")
    print()

    # Example 3: Brokerage account with annual compounding
    gs3 = growth_series(
        rate=apr(0.08),
        compounds='annually',
        contribution=annual(6000),
        duration=years(30)
    )

    principal3 = 10000
    print(f"Example 3: apr(0.08), annual compounding, $6000/year, 30 years, $10000 principal")
    print(f"Final value: ${gs3.get_final_value(principal3):.2f}")
    print(f"Value at 10 years: ${gs3.value_at(10, principal3):.2f}")
    print()

    # Example 4: Compare APR vs APY
    print("Comparison: apr(0.045) vs apy(0.0459)")

    gs_apr = growth_series(
        rate=apr(0.045),
        compounds='monthly',
        duration=years(1)
    )

    gs_apy = growth_series(
        rate=apy(0.0459),
        compounds='monthly',
        duration=years(1)
    )

    principal4 = 10000
    print(f"$10,000 at apr(0.045) after 1 year: ${gs_apr.get_final_value(principal4):.2f}")
    print(f"$10,000 at apy(0.0459) after 1 year: ${gs_apy.get_final_value(principal4):.2f}")
    print()

    # Example 5: growth_scenario - Chaining multiple growth periods
    print("Example 5: growth_scenario - Multiple growth periods")
    print("Scenario: Start with $10,000")
    print("  - 5 years in HYSA at 4% APR")
    print("  - Then 10 years in brokerage at 8% APR")
    print("  - Then 15 years in brokerage at 10% APR with $500/month contributions")

    scenario = growth_scenario(
        initial_principal=10000,
        series_list=[
            growth_series(rate=apr(0.04), compounds='monthly', duration=years(5)),
            growth_series(rate=apr(0.08), compounds='monthly', duration=years(10)),
            growth_series(rate=apr(0.10), compounds='monthly', contribution=monthly(500), duration=years(15))
        ]
    )

    series_values = scenario.get_series_values()
    print(f"After series 1 (5 years): ${series_values[0]:.2f}")
    print(f"After series 2 (10 years): ${series_values[1]:.2f}")
    print(f"After series 3 (15 years): ${series_values[2]:.2f}")
    print(f"Final value: ${scenario.get_final_value():.2f}")
