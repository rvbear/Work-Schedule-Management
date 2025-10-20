from datetime import datetime, time

def parse_time_str(t):
    return datetime.strptime(t, "%H:%M:%S").time()


def time_range_overlap(start, end, ranges):
    count = 0
    for r_start, r_end in ranges:
        latest_start = max(start, r_start)
        earliest_end = min(end, r_end)
        overlap = (datetime.combine(datetime.today(), earliest_end) - 
                   datetime.combine(datetime.today(), latest_start))
        if overlap.total_seconds() > 0:
            count += 1
    return count


def calc_ot(clock_in, clock_out):
    if not clock_in or not clock_out:
        return 0
    start = parse_time_str(clock_in)
    end = parse_time_str(clock_out)
    ot_start = time(17, 0)

    if end <= ot_start:
        return 0

    valid_start = max(start, ot_start)
    excluded_ranges = [(time(0, 0), time(1, 0)), (time(5, 0), time(6, 0)),
                       (time(12, 0), time(13, 0)), (time(17, 0), time(18, 0))]
    
    ot_duration = (datetime.combine(datetime.today(), end) - 
                   datetime.combine(datetime.today(), valid_start)).total_seconds() / 60
    
    excluded_minutes = 0
    for r_start, r_end in excluded_ranges:
        latest_start = max(valid_start, r_start)
        earliest_end = min(end, r_end)
        overlap = (datetime.combine(datetime.today(), earliest_end) - 
                   datetime.combine(datetime.today(), latest_start)).total_seconds()
        if overlap > 0:
            excluded_minutes += overlap / 60

    effective_minutes = max(0, ot_duration - excluded_minutes)
    return round(effective_minutes // 30 * 0.5, 1)


def calc_late_early(clock_in, clock_out):
    base_in = time(8, 0)
    base_out = time(17, 0)
    late = early = 0

    if clock_in:
        actual_in = parse_time_str(clock_in)
        if actual_in > base_in:
            late = (datetime.combine(datetime.today(), actual_in) - 
                    datetime.combine(datetime.today(), base_in)).total_seconds() / 60

    if clock_out:
        actual_out = parse_time_str(clock_out)
        if actual_out < base_out:
            early = (datetime.combine(datetime.today(), base_out) - 
                     datetime.combine(datetime.today(), actual_out)).total_seconds() / 60

    total = late + early
    return round(total // 30 * 0.5, 1)


def calc_meal_allowance(clock_in, clock_out, is_weekend):
    if not clock_in or not clock_out:
        return 0
    start = parse_time_str(clock_in)
    end = parse_time_str(clock_out)
    common_ranges = [(time(0, 0), time(1, 0)), (time(5, 0), time(6, 0))]
    weekend_ranges = common_ranges + [(time(12, 0), time(13, 0)), (time(17, 0), time(18, 0))]
    applicable_ranges = weekend_ranges if is_weekend else common_ranges
    count = time_range_overlap(start, end, applicable_ranges)
    return count * 10000


def calc_transport_allowance(clock_in, clock_out, is_weekend):
    if is_weekend:
        return 5000 if clock_in else 0
    else:
        if not clock_out:
            return 0
        out_time = parse_time_str(clock_out)
        if out_time >= time(22, 0):
            return 5000
    return 0


def is_weekend_date(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.weekday() >= 5  # 5: Saturday, 6: Sunday