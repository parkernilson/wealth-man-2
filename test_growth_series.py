"""
Test suite for growth_series class.

Tests verify compound interest calculations with various scenarios.
"""

import unittest
from growth_series import growth_series, apr, apy, monthly, annual, years


class TestGrowthSeries(unittest.TestCase):
    """Test cases for growth_series calculations."""

    def test_basic_annual_compounding_with_monthly_contributions(self):
        """
        Test case: $10,000 principal, $300/month contributions, 7% APR, annual compounding.

        Expected values:
        - 1 year: $14,300.00
        - 5 years: $34,728.18
        - 10 years: $69,410.73
        """
        gs = growth_series(
            rate=apr(0.07),
            compounds='annually',
            contribution=monthly(300),
            duration=years(10),
            initial_principal=10000
        )

        # Test at 1 year (tolerance: +/- $10)
        self.assertAlmostEqual(gs.value_at(1), 14300.00, delta=10.0,
            msg=f"Expected $14,300.00 at 1 year, got ${gs.value_at(1):.2f}")

        # Test at 5 years (tolerance: +/- $10)
        self.assertAlmostEqual(gs.value_at(5), 34728.18, delta=10.0,
            msg=f"Expected $34,728.18 at 5 years, got ${gs.value_at(5):.2f}")

        # Test at 10 years (tolerance: +/- $10)
        self.assertAlmostEqual(gs.value_at(10), 69410.73, delta=10.0,
            msg=f"Expected $69,410.73 at 10 years, got ${gs.value_at(10):.2f}")

        # Test get_final_value() matches value_at(10) (tolerance: +/- $10)
        self.assertAlmostEqual(gs.get_final_value(), 69410.73, delta=10.0,
            msg=f"Expected final value $69,410.73, got ${gs.get_final_value():.2f}")

    def test_monthly_compounding_with_apr(self):
        """Test monthly compounding with APR."""
        gs = growth_series(
            rate=apr(0.05),
            compounds='monthly',
            contribution=monthly(100),
            duration=years(5),
            initial_principal=1000
        )

        final_value = gs.get_final_value()
        # With 5% APR compounded monthly: 1000 * (1 + 0.05/12)^60 + annuity
        expected = 8083.97
        self.assertAlmostEqual(final_value, expected, delta=0.01,
            msg=f"Expected ${expected:.2f}, got ${final_value:.2f}")

    def test_apy_vs_apr_equivalence(self):
        """Test that APY and APR produce equivalent results when properly converted."""
        # 4.5% APR with monthly compounding ≈ 4.59% APY
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

        apr_result = gs_apr.get_final_value()
        apy_result = gs_apy.get_final_value()

        # They should be very close (within a few cents due to rounding)
        self.assertAlmostEqual(apr_result, apy_result, delta=1.0,
            msg=f"APR result ${apr_result:.2f} and APY result ${apy_result:.2f} differ by more than $1")

    def test_no_contributions(self):
        """Test growth with no contributions, only initial principal."""
        gs = growth_series(
            rate=apr(0.06),
            compounds='annually',
            duration=years(10),
            initial_principal=1000
        )

        # Simple compound interest: 1000 * (1.06)^10 = 1790.85
        expected = 1790.85
        final_value = gs.get_final_value()
        self.assertAlmostEqual(final_value, expected, delta=0.01,
            msg=f"Expected ${expected:.2f}, got ${final_value:.2f}")

    def test_no_initial_principal(self):
        """Test growth with contributions but no initial principal."""
        gs = growth_series(
            rate=apr(0.05),
            compounds='monthly',
            contribution=monthly(100),
            duration=years(5),
            initial_principal=0
        )

        final_value = gs.get_final_value()
        # Just the annuity portion
        expected = 6800.61
        self.assertAlmostEqual(final_value, expected, delta=0.01,
            msg=f"Expected ${expected:.2f}, got ${final_value:.2f}")

    def test_annual_contributions_annual_compounding(self):
        """Test annual contributions with annual compounding."""
        gs = growth_series(
            rate=apr(0.08),
            compounds='annually',
            contribution=annual(6000),
            duration=years(10),
            initial_principal=10000
        )

        final_value = gs.get_final_value()
        # 10000 * (1.08)^10 + 6000 * [((1.08)^10 - 1) / 0.08]
        expected = 108508.62
        self.assertAlmostEqual(final_value, expected, delta=0.01,
            msg=f"Expected ${expected:.2f}, got ${final_value:.2f}")

    def test_zero_rate(self):
        """Test with 0% interest rate."""
        gs = growth_series(
            rate=apr(0.0),
            compounds='monthly',
            contribution=monthly(100),
            duration=years(5),
            initial_principal=1000
        )

        # Should just be principal + contributions
        expected = 1000 + (100 * 12 * 5)
        final_value = gs.get_final_value()
        self.assertAlmostEqual(final_value, expected, delta=0.01,
            msg=f"Expected ${expected:.2f}, got ${final_value:.2f}")

    def test_value_at_intermediate_times(self):
        """Test value_at() for various intermediate times."""
        gs = growth_series(
            rate=apr(0.06),
            compounds='monthly',
            contribution=monthly(50),
            duration=years(3),
            initial_principal=1000
        )

        # Test at 6 months
        value_6m = gs.value_at(0.5)
        self.assertGreater(value_6m, 1000, "Value should increase after 6 months")
        self.assertLess(value_6m, gs.get_final_value(), "6 month value should be less than final")

        # Test at 1.5 years
        value_1_5y = gs.value_at(1.5)
        self.assertGreater(value_1_5y, value_6m, "Value should increase over time")
        self.assertLess(value_1_5y, gs.get_final_value(), "1.5 year value should be less than final")

    def test_requires_apr_or_apy_helper(self):
        """Test that plain floats are rejected for rate parameter."""
        with self.assertRaises(TypeError) as cm:
            growth_series(
                rate=0.05,  # Plain float should be rejected
                compounds='monthly',
                duration=years(5)
            )
        self.assertIn("rate must be created with apr() or apy()", str(cm.exception))

    def test_invalid_compounds_parameter(self):
        """Test that invalid compounds parameter raises error."""
        with self.assertRaises(ValueError) as cm:
            growth_series(
                rate=apr(0.05),
                compounds='daily',  # Invalid
                duration=years(5)
            )
        self.assertIn("compounds must be 'monthly' or 'annually'", str(cm.exception))

    def test_negative_time_raises_error(self):
        """Test that negative time raises ValueError."""
        gs = growth_series(
            rate=apr(0.05),
            compounds='monthly',
            duration=years(5),
            initial_principal=1000
        )

        with self.assertRaises(ValueError) as cm:
            gs.value_at(-1)
        self.assertIn("t_years must be non-negative", str(cm.exception))

    def test_missing_duration_raises_error(self):
        """Test that calling get_final_value() without duration raises error."""
        gs = growth_series(
            rate=apr(0.05),
            compounds='monthly',
            initial_principal=1000
            # No duration specified
        )

        with self.assertRaises(ValueError) as cm:
            gs.get_final_value()
        self.assertIn("Duration not set", str(cm.exception))


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
