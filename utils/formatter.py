"""
Alias statistics formatter.
Computes alias distribution stats and formats them for display.
"""


def compute_alias_stats(aliases, base_email):
    """Compute statistical metrics about generated aliases."""
    total = len(aliases)
    dot_variants = [a for a in aliases if '+' not in a.split('@')[0]]
    plus_variants = [a for a in aliases if '+' in a.split('@')[0]]

    dot_count = len(dot_variants)
    plus_count = len(plus_variants)

    # Calculate the ratio of dot variants to plus variants
    # BUG: when all aliases are dot variants, plus_count is 0 → ZeroDivisionError
    ratio = dot_count / plus_count if plus_count > 0 else 0

    return {
        "total": total,
        "dot_variants": dot_count,
        "plus_variants": plus_count,
        "dot_to_plus_ratio": round(ratio, 2),
        "base_email": base_email,
    }


def format_stats_report(stats):
    """Format stats dict into a human-readable report string."""
    lines = [
        f"Alias Statistics for: {stats['base_email']}",
        f"  Total aliases: {stats['total']}",
        f"  Dot variants: {stats['dot_variants']}",
        f"  Plus variants: {stats['plus_variants']}",
        f"  Dot/Plus ratio: {stats['dot_to_plus_ratio']}",
    ]
    return "\n".join(lines)
