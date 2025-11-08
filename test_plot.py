#!/usr/bin/env python3
"""
Test script to verify growth_scenario plotting functionality.
"""

import matplotlib.pyplot as plt
from growth_series import growth_series, growth_scenario, apr, monthly, years


def test_simple_scenario():
    """Test plotting a simple scenario with two series."""
    print("Testing simple scenario...")

    scenario = growth_scenario(
        initial_principal=10000,
        series_list=[
            growth_series(rate=apr(0.05), compounds='monthly', duration=years(5)),
            growth_series(rate=apr(0.07), compounds='monthly', duration=years(10))
        ]
    )

    fig, ax = scenario.plot(title="Simple Growth Scenario")
    plt.savefig('test_simple_scenario.png', dpi=150, bbox_inches='tight')
    print("✓ Simple scenario plotted successfully")
    plt.close(fig)


def test_retirement_scenario():
    """Test plotting a realistic retirement scenario."""
    print("Testing retirement scenario...")

    scenario = growth_scenario(
        initial_principal=50000,
        series_list=[
            # 10 years contributing $500/month at 7% (age 30-40)
            growth_series(rate=apr(0.07), compounds='monthly', contribution=monthly(500), duration=years(10)),
            # 15 years contributing $1000/month at 8% (age 40-55)
            growth_series(rate=apr(0.08), compounds='monthly', contribution=monthly(1000), duration=years(15)),
            # 10 years contributing $2000/month at 6% (age 55-65)
            growth_series(rate=apr(0.06), compounds='monthly', contribution=monthly(2000), duration=years(10))
        ]
    )

    fig, ax = scenario.plot(title="Retirement Planning Scenario")
    plt.savefig('test_retirement_scenario.png', dpi=150, bbox_inches='tight')
    print("✓ Retirement scenario plotted successfully")

    # Print final value
    final_value = scenario.get_final_value()
    print(f"  Final retirement value: ${final_value:,.2f}")
    plt.close(fig)


def test_custom_styling():
    """Test plotting with custom styling options."""
    print("Testing custom styling...")

    scenario = growth_scenario(
        initial_principal=5000,
        series_list=[
            growth_series(rate=apr(0.04), compounds='monthly', contribution=monthly(100), duration=years(5)),
            growth_series(rate=apr(0.06), compounds='monthly', contribution=monthly(200), duration=years(5)),
            growth_series(rate=apr(0.08), compounds='monthly', contribution=monthly(300), duration=years(5))
        ]
    )

    # Test with custom parameters
    fig, ax = scenario.plot(
        num_points=1000,
        show_series_transitions=True,
        title="Custom Styled Growth Scenario",
        figsize=(12, 8)
    )

    plt.savefig('test_custom_styling.png', dpi=150, bbox_inches='tight')
    print("✓ Custom styling plotted successfully")
    plt.close(fig)


def test_single_series():
    """Test plotting a scenario with a single series."""
    print("Testing single series scenario...")

    scenario = growth_scenario(
        initial_principal=1000,
        series_list=[
            growth_series(rate=apr(0.05), compounds='monthly', contribution=monthly(50), duration=years(10))
        ]
    )

    fig, ax = scenario.plot(title="Single Series Scenario")
    plt.savefig('test_single_series.png', dpi=150, bbox_inches='tight')
    print("✓ Single series scenario plotted successfully")
    plt.close(fig)


def test_no_transitions():
    """Test plotting without showing series transitions."""
    print("Testing scenario without transition markers...")

    scenario = growth_scenario(
        initial_principal=10000,
        series_list=[
            growth_series(rate=apr(0.06), compounds='monthly', duration=years(5)),
            growth_series(rate=apr(0.08), compounds='monthly', duration=years(10))
        ]
    )

    fig, ax = scenario.plot(show_series_transitions=False, title="No Transition Markers")
    plt.savefig('test_no_transitions.png', dpi=150, bbox_inches='tight')
    print("✓ Scenario without transitions plotted successfully")
    plt.close(fig)


if __name__ == "__main__":
    print("=" * 60)
    print("Testing growth_scenario plotting functionality")
    print("=" * 60)
    print()

    test_simple_scenario()
    test_retirement_scenario()
    test_custom_styling()
    test_single_series()
    test_no_transitions()

    print()
    print("=" * 60)
    print("All tests completed successfully!")
    print("Check the generated PNG files to view the plots.")
    print("=" * 60)
