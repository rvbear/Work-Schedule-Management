def format_date(date_str):
    # 'YYYYMMDD' -> 'YYYY-MM-DD'
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"


def format_time(time_str):
    # 'HHMMSS' -> 'HH:MM:SS'
    return f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"


def format_code(num):
    # 22 -> '0022'
    return f"{num:0>4}"


def format_id(id):
    # 12345678 -> '012345678' (9자리)
    id_str = str(id).strip()
    if id_str.isdigit():
        return f"{int(id_str):0>9}"
    return id_str