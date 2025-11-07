"""
Test suite for growth_scenario class.

Tests verify chaining of multiple growth_series objects.
"""

import unittest
from growth_series import growth_series, growth_scenario, apr, apy, monthly, annual, years


class TestGrowthScenario(unittest.TestCase):
    """Test cases for growth_scenario calculations."""

    def test_two_series_basic(self):
        """Test basic scenario with two sequential series."""
        # $10,000 for 5 years at 5%, then 10 years at 7%
        scenario = growth_scenario(
            initial_principal=10000,
            series_list=[
                growth_series(rate=apr(0.05), compounds='annually', duration=years(5)),
                growth_series(rate=apr(0.07), compounds='annually', duration=years(10))
            ]
        )

        # Calculate manually:
        # After series 1: 10000 * (1.05)^5 = 12762.82
        # After series 2: 12762.82 * (1.07)^10 = 25105.45
        series_values = scenario.get_series_values()
        self.assertAlmostEqual(series_values[0], 12762.82, delta=1.0,
            msg=f"Expected $12,762.82 after series 1, got ${series_values[0]:.2f}")
        self.assertAlmostEqual(series_values[1], 25105.45, delta=1.0,
            msg=f"Expected $25,105.45 after series 2, got ${series_values[1]:.2f}")

        final_value = scenario.get_final_value()
        self.assertAlmostEqual(final_value, 25105.45, delta=1.0,
            msg=f"Expected final value $25,105.45, got ${final_value:.2f}")

    def test_three_series_with_contributions(self):
        """Test scenario with three series, including contributions."""
        scenario = growth_scenario(
            initial_principal=5000,
            series_list=[
                # 3 years at 4% with $100/month contributions
                growth_series(rate=apr(0.04), compounds='monthly', contribution=monthly(100), duration=years(3)),
                # 5 years at 6% with no contributions
                growth_series(rate=apr(0.06), compounds='monthly', duration=years(5)),
                # 7 years at 8% with $200/month contributions
                growth_series(rate=apr(0.08), compounds='monthly', contribution=monthly(200), duration=years(7))
            ]
        )

        series_values = scenario.get_series_values()

        # Verify we have 3 values
        self.assertEqual(len(series_values), 3, "Should have 3 series values")

        # Each value should be greater than the previous
        self.assertGreater(series_values[0], 5000, "Value after series 1 should be greater than initial")
        self.assertGreater(series_values[1], series_values[0], "Value should increase in series 2")
        self.assertGreater(series_values[2], series_values[1], "Value should increase in series 3")

        # Final value should match the last series value
        final_value = scenario.get_final_value()
        self.assertEqual(final_value, series_values[2], "Final value should match last series")

    def test_single_series(self):
        """Test scenario with only one series (edge case)."""
        scenario = growth_scenario(
            initial_principal=1000,
            series_list=[
                growth_series(rate=apr(0.05), compounds='annually', duration=years(10))
            ]
        )

        # Should be same as using growth_series directly
        gs = growth_series(rate=apr(0.05), compounds='annually', duration=years(10))

        expected = gs.get_final_value(1000)
        actual = scenario.get_final_value()

        self.assertAlmostEqual(actual, expected, delta=0.01,
            msg=f"Single series scenario should match direct growth_series calculation")

    def test_value_at_series(self):
        """Test value_at_series method for intermediate values."""
        scenario = growth_scenario(
            initial_principal=10000,
            series_list=[
                growth_series(rate=apr(0.05), compounds='monthly', duration=years(5)),
                growth_series(rate=apr(0.07), compounds='monthly', duration=years(10))
            ]
        )

        # Test value at year 2 of the first series (index 0)
        value_series0_year2 = scenario.value_at_series(0, 2)
        self.assertGreater(value_series0_year2, 10000, "Value should be greater than initial")

        # Calculate expected value manually
        gs0 = growth_series(rate=apr(0.05), compounds='monthly', duration=years(5))
        expected = gs0.value_at(2, 10000)
        self.assertAlmostEqual(value_series0_year2, expected, delta=0.01)

        # Test value at year 5 of the second series (index 1)
        value_series1_year5 = scenario.value_at_series(1, 5)

        # Calculate expected: start with value after first series
        principal_after_series0 = gs0.get_final_value(10000)
        gs1 = growth_series(rate=apr(0.07), compounds='monthly', duration=years(10))
        expected_series1 = gs1.value_at(5, principal_after_series0)

        self.assertAlmostEqual(value_series1_year5, expected_series1, delta=0.01)

    def test_value_at_series_invalid_index(self):
        """Test that invalid series index raises error."""
        scenario = growth_scenario(
            initial_principal=10000,
            series_list=[
                growth_series(rate=apr(0.05), compounds='annually', duration=years(5))
            ]
        )

        with self.assertRaises(ValueError):
            scenario.value_at_series(1, 0)  # Only index 0 is valid

        with self.assertRaises(ValueError):
            scenario.value_at_series(-1, 0)  # Negative index

    def test_realistic_retirement_scenario(self):
        """Test a realistic retirement planning scenario."""
        # Scenario:
        # - Start with $50,000 at age 30
        # - 10 years contributing $500/month at 7% (age 30-40)
        # - 15 years contributing $1000/month at 8% (age 40-55)
        # - 10 years contributing $2000/month at 6% (age 55-65)

        scenario = growth_scenario(
            initial_principal=50000,
            series_list=[
                growth_series(rate=apr(0.07), compounds='monthly', contribution=monthly(500), duration=years(10)),
                growth_series(rate=apr(0.08), compounds='monthly', contribution=monthly(1000), duration=years(15)),
                growth_series(rate=apr(0.06), compounds='monthly', contribution=monthly(2000), duration=years(10))
            ]
        )

        series_values = scenario.get_series_values()
        final_value = scenario.get_final_value()

        # Sanity checks
        self.assertGreater(series_values[0], 50000, "Should grow in first period")
        self.assertGreater(series_values[1], series_values[0], "Should grow in second period")
        self.assertGreater(series_values[2], series_values[1], "Should grow in third period")

        # Final value should be substantial after 35 years of contributions
        self.assertGreater(final_value, 500000, "Should accumulate substantial wealth")

    def test_zero_initial_principal(self):
        """Test scenario starting with zero principal."""
        scenario = growth_scenario(
            initial_principal=0,
            series_list=[
                growth_series(rate=apr(0.05), compounds='monthly', contribution=monthly(100), duration=years(5)),
                growth_series(rate=apr(0.07), compounds='monthly', contribution=monthly(200), duration=years(5))
            ]
        )

        series_values = scenario.get_series_values()

        # First series: just contributions with growth
        self.assertGreater(series_values[0], 0, "Should accumulate value from contributions")

        # Second series: should continue growing
        self.assertGreater(series_values[1], series_values[0], "Should continue growing")

    def test_varying_compounding_periods(self):
        """Test scenario with different compounding periods."""
        scenario = growth_scenario(
            initial_principal=10000,
            series_list=[
                growth_series(rate=apr(0.05), compounds='monthly', duration=years(5)),
                growth_series(rate=apr(0.06), compounds='annually', duration=years(5)),
                growth_series(rate=apr(0.07), compounds='monthly', duration=years(5))
            ]
        )

        series_values = scenario.get_series_values()
        final_value = scenario.get_final_value()

        # Each period should grow
        self.assertGreater(series_values[0], 10000)
        self.assertGreater(series_values[1], series_values[0])
        self.assertGreater(series_values[2], series_values[1])

        # Final value should match last series
        self.assertEqual(final_value, series_values[2])

    def test_apr_vs_apy_in_scenario(self):
        """Test scenario using both APR and APY rates."""
        scenario = growth_scenario(
            initial_principal=10000,
            series_list=[
                growth_series(rate=apr(0.05), compounds='monthly', duration=years(5)),
                growth_series(rate=apy(0.0512), compounds='monthly', duration=years(5))  # ~5% APR
            ]
        )

        series_values = scenario.get_series_values()

        # Both periods should grow
        self.assertGreater(series_values[0], 10000)
        self.assertGreater(series_values[1], series_values[0])


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
