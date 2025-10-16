import csv

# read txt file
txt_filename = input("파일 이름을 입력하세요: ")
if not txt_filename:
    print("파일 이름을 확인해주세요.")
    exit(1)
    
txt_file = txt_filename + '.txt'
work_records = {}

def format_date(date_str):
    # 'YYYYMMDD' -> 'YYYY-MM-DD'
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

def format_time(time_str):
    # 'HHMMSS' -> 'HH:MM:SS'
    return f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"

with open(txt_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if len(line) >= 19:
            date = line[:8]
            time = line[8:14]
            status = line[14:15]
            emp_id = line[15:19]
            key = (emp_id, date)
            if key not in work_records:
                work_records[key] = {
                    'employee_id': emp_id,
                    'date': format_date(date),
                    'clock_in': None,
                    'clock_out': None
                }
            if status == '1':
                work_records[key]['clock_in'] = format_time(time)
            elif status == '2':
                work_records[key]['clock_out'] = format_time(time)
        else:
            print('잘못된 데이터:', line)

# transform dict to list
result = list(work_records.values())

# map to korean column names
def convert_to_korean(row):
    return {
        '사원번호': row.get('employee_id', ''),
        '날짜': row.get('date', ''),
        '출근': row.get('clock_in', ''),
        '퇴근': row.get('clock_out', '')
    }

fieldnames = ['사원번호', '날짜', '출근', '퇴근']
csv_filename = txt_filename + '_합본.csv'

with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in result:
        writer.writerow(convert_to_korean(row))

print(f"CSV 파일로 저장 완료: {csv_filename}")
