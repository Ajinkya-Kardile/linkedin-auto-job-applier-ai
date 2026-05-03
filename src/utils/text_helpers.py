
def truncate_for_csv(text, max_length=30000):
    """Ensures a string doesn't exceed CSV field limits."""
    if not isinstance(text, str):
        text = str(text)
    if len(text) > max_length:
        return text[:max_length] + "... [TRUNCATED]"
    return text

def clean_company_name(company_string):
    """Removes extra characters often scraped alongside company names."""
    if '  ' in company_string:
        return company_string.split('  ')[0].strip()
    return company_string.strip()


def calculate_date_posted(time_str: str):
    """Converts LinkedIn time strings ('2 hours ago') to exact Dates."""
    from datetime import datetime, timedelta
    if not time_str or "Unknown" in time_str:
        return "Unknown"

    try:
        val = int(''.join(filter(str.isdigit, time_str)))
        if 'hour' in time_str:
            return (datetime.now() - timedelta(hours=val)).strftime('%Y-%m-%d')
        elif 'day' in time_str:
            return (datetime.now() - timedelta(days=val)).strftime('%Y-%m-%d')
        elif 'week' in time_str:
            return (datetime.now() - timedelta(weeks=val)).strftime('%Y-%m-%d')
        elif 'month' in time_str:
            return (datetime.now() - timedelta(days=val * 30)).strftime('%Y-%m-%d')
    except:
        pass
    return datetime.now().strftime('%Y-%m-%d')