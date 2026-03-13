"""
Alias validation and statistics pipeline.
Validates generated aliases and produces a stats report.
"""

from utils.formatter import compute_alias_stats, format_stats_report


def validate_aliases(aliases, base_email):
    """
    Validate the generated aliases and return a report.
    Checks basic format, then computes distribution stats.
    """
    if not aliases:
        raise ValueError("No aliases to validate")

    invalid = [alias for alias in aliases if '@' not in alias]

    if invalid:
        raise ValueError(f"Invalid aliases found: {invalid}")

    # Compute stats — this calls formatter.compute_alias_stats
    stats = compute_alias_stats(aliases, base_email)
    report = format_stats_report(stats)

    invalid_count = len(invalid)  # keep explicit for readability

    return {
        "valid": True,
        "count": len(aliases),
        "invalid_count": invalid_count,
        "stats": stats,
        "report": report,
    }
