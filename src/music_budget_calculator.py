"""
Music Production Budget Calculator
Uses real industry cost data split by project type and budget tier.
"""

# ANSI color codes for terminal output
RED   = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

# ── Master cost data ──────────────────────────────────────────────────────────
# Baseline (Standard tier, 1.0×) costs for every project type.
# To update pricing, change numbers here — nothing else needs to change.
PROJECT_DATA = {
    "1": {
        "label": "Single (1 track)",
        "total": 3_750,
        "costs": {
            "Recording":   750,
            "Mixing":    1_200,
            "Mastering":   400,
            "Production": 1_400,
        },
    },
    "2": {
        "label": "Demo (3 tracks)",
        "total": 6_200,
        "costs": {
            "Recording":  1_200,
            "Mixing":    2_100,
            "Mastering":   800,
            "Production": 2_100,
        },
    },
    "3": {
        "label": "EP (5 tracks)",
        "total": 11_550,
        "costs": {
            "Recording":  2_250,
            "Mixing":    3_900,
            "Mastering":  1_200,
            "Production": 4_200,
        },
    },
    "4": {
        "label": "LP (10 tracks)",
        "total": 22_500,
        "costs": {
            "Recording":  6_000,
            "Mixing":    7_500,
            "Mastering":  2_000,
            "Production": 7_000,
        },
    },
}

# Multipliers applied to every baseline cost based on the chosen service tier
TIER_MULTIPLIERS = {
    "1": {"label": "Budget   (home studio)", "multiplier": 0.5},
    "2": {"label": "Standard (mid-level)",   "multiplier": 1.0},
    "3": {"label": "Premium  (high-end)",    "multiplier": 2.5},
}

# Marketing & distribution estimate ranges shown after the main breakdown.
# (lo, hi) in dollars — easy to update independently of production costs.
MARKETING_ESTIMATES = [
    {
        "name": "Distribution fee",
        "desc": "Pay-per-release or annual subscription",
        "range": (20, 50),
        "unit": "per release / per year",
    },
    {
        "name": "Promotion (indie level)",
        "desc": "Social ads, blog features, online PR",
        "range": (200, 500),
        "unit": "per single",
    },
    {
        "name": "Playlist pitching",
        "desc": "Independent playlist submission services",
        "range": (50, 300),
        "unit": "per submission",
    },
    {
        "name": "PR agency (optional)",
        "desc": "Full-service press and media outreach",
        "range": (1_500, 5_000),
        "unit": "per month",
    },
]

# One-line descriptions shown under each production category
CATEGORY_META = {
    "Recording":  "Studio time, session musicians, and equipment rental.",
    "Mixing":     "Balancing tracks, EQ, compression, and spatial effects.",
    "Mastering":  "Final polish and loudness optimization for streaming platforms.",
    "Production": "Arrangement, beat production, and creative direction.",
}


def ascii_bar(percent: float, width: int = 20) -> str:
    """
    Generate an ASCII progress bar for a given percentage (0.0 – 1.0).
    Filled blocks are '█', empty blocks are '░'.
    """
    filled = round(percent * width)
    empty  = width - filled
    return "█" * filled + "░" * empty


def get_project_type() -> dict:
    """
    Display a numbered menu of project types and return the chosen project dict.
    Loops until the user enters a valid choice (1–4).
    """
    print("\n── Step 1: Project Type ──────────────────────────")
    for key, project in PROJECT_DATA.items():
        print(f"  {key}. {project['label']}  (baseline ${project['total']:,})")
    while True:
        choice = input("Select project type [1-4]: ").strip()
        if choice in PROJECT_DATA:
            return PROJECT_DATA[choice]
        print("Please enter a number between 1 and 4.")


def get_tier() -> dict:
    """
    Display a numbered menu of budget tiers and return the chosen tier dict.
    Loops until the user enters a valid choice (1–3).
    """
    print("\n── Step 2: Budget Tier ───────────────────────────")
    for key, tier in TIER_MULTIPLIERS.items():
        print(f"  {key}. {tier['label']}  (×{tier['multiplier']})")
    while True:
        choice = input("Select tier [1-3]: ").strip()
        if choice in TIER_MULTIPLIERS:
            return TIER_MULTIPLIERS[choice]
        print("Please enter 1, 2, or 3.")


def calculate_budget(project: dict, tier: dict, user_budget: float) -> tuple[list[dict], float]:
    """
    Apply the tier multiplier to each baseline cost.
    Returns a list of category result dicts and the recommended total
    so the caller can compare against the user's actual budget.
    """
    multiplier       = tier["multiplier"]
    recommended_total = project["total"] * multiplier

    results = []
    for cat_name, baseline in project["costs"].items():
        amount  = round(baseline * multiplier, 2)
        # Express each category as a share of the recommended total for the bar
        percent = amount / recommended_total if recommended_total else 0
        results.append({
            "name":        cat_name,
            "amount":      amount,
            "percent":     percent,
            "description": CATEGORY_META.get(cat_name, ""),
        })
    return results, recommended_total


def print_results(
    project: dict,
    tier: dict,
    user_budget: float,
    breakdown: list[dict],
    recommended_total: float,
) -> None:
    """
    Display the full budget breakdown with ASCII bars, a marketing & distribution
    estimate section, grand totals, and smart warnings based on how the user's
    budget compares to the industry-recommended total.
    """
    print("\n" + "=" * 54)
    print(f"  🎵  {project['label']}  ·  {tier['label'].strip()}")
    print(f"  Recommended total : ${recommended_total:,.2f}")
    if user_budget != recommended_total:
        print(f"  Your budget       : ${user_budget:,.2f}")
    print("=" * 54)

    # ── Production breakdown ─────────────────────────────────────────────────
    production_total = sum(item["amount"] for item in breakdown)
    for item in breakdown:
        bar       = ascii_bar(item["percent"])
        pct_label = f"{item['percent'] * 100:.0f}%"
        print(f"\n  {item['name']} ({pct_label})")
        print(f"    ${item['amount']:>10,.2f}  [{bar}]")
        print(f"    ↳ {item['description']}")

    # ── Marketing & Distribution estimates ───────────────────────────────────
    print("\n" + "─" * 54)
    print("  📣  Marketing & Distribution Estimates")
    print("─" * 54)

    mktg_min_total = 0
    mktg_max_total = 0
    for item in MARKETING_ESTIMATES:
        lo, hi          = item["range"]
        mktg_min_total += lo
        mktg_max_total += hi
        # Scale bar against $5,000 (the PR upper-bound, the largest range value)
        bar = ascii_bar(hi / 5_000)
        print(f"\n  {item['name']}")
        print(f"    ${lo:>6,} – ${hi:,}  [{bar}]  {item['unit']}")
        print(f"    ↳ {item['desc']}")

    print(f"\n  Estimated marketing range: ${mktg_min_total:,} – ${mktg_max_total:,}")

    # ── Grand totals ─────────────────────────────────────────────────────────
    print("\n" + "=" * 54)
    print(f"  Grand total (production + min marketing): ${production_total + mktg_min_total:,.2f}")
    print(f"  Grand total (production + max marketing): ${production_total + mktg_max_total:,.2f}")
    print("=" * 54)

    # ── Smart warnings ───────────────────────────────────────────────────────
    # Warn if budget is more than 30 % below the recommended total
    if user_budget < recommended_total * 0.70:
        print(
            f"\n{RED}⚠  Warning: Your budget is significantly below the industry average "
            f"for this project type. Quality may be compromised.{RESET}"
        )
    # Tip if budget exceeds the recommendation
    elif user_budget > recommended_total:
        print(
            f"\n{GREEN}✓  You have headroom in your budget. Consider investing "
            f"the extra in marketing and promotion.{RESET}"
        )

    print()


def main() -> None:
    """
    Main loop: ask project type and tier via selection menus, collect an optional
    custom budget, display the full breakdown, then ask whether to calculate again.
    """
    print("\n🎚  Welcome to the Music Production Budget Calculator")
    print("    Powered by real industry cost data\n")

    while True:
        # Step 1 & 2: guided selection menus
        project = get_project_type()
        tier    = get_tier()

        recommended = project["total"] * tier["multiplier"]

        # Step 3: optional custom budget override
        print(f"\n── Step 3: Your Budget ───────────────────────────")
        print(f"   Industry recommendation: ${recommended:,.2f}")
        raw = input("   Enter your budget (or press Enter to use recommended): $").strip()

        if raw == "":
            user_budget = recommended
        else:
            # Keep prompting until we get a valid positive number
            while True:
                try:
                    user_budget = float(raw)
                    if user_budget <= 0:
                        raise ValueError
                    break
                except ValueError:
                    raw = input("   Invalid — please enter a positive number: $").strip()

        breakdown, recommended_total = calculate_budget(project, tier, user_budget)
        print_results(project, tier, user_budget, breakdown, recommended_total)

        # Ask if the user wants to run another calculation
        again = input("Calculate another budget? (yes/no): ").strip().lower()
        if again not in ("yes", "y"):
            print("\n🎶  Thanks for using the Music Budget Calculator. Good luck with your project!\n")
            break


if __name__ == "__main__":
    main()
