import csv
from formatting_utils import format_date, format_time
from employee_info import get_department_by_name
from calc_utils import calc_ot, calc_late_early, calc_meal_allowance, calc_transport_allowance, is_weekend_date

# read txt file
print("출퇴근 파일을 읽습니다.")
txt_filename = input("파일 이름을 입력하세요: ")
if not txt_filename:
    print("파일 이름을 확인해주세요.")
    exit(1)
    
txt_file = txt_filename + '.txt'
work_records = {}

with open(txt_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if len(line) >= 19:
            date, time, status, card_num = line[:8], line[8:14], line[14:15], line[15:19]
            key = (card_num, date)
            if key not in work_records:
                work_records[key] = {
                    '카드번호': card_num,
                    '날짜': format_date(date),
                    '출근': None,
                    '퇴근': None
                }
            if status == '1':
                work_records[key]['출근'] = format_time(time)
            elif status == '2':
                work_records[key]['퇴근'] = format_time(time)
        else:
            print('잘못된 데이터:', line)

# transform dict to list
result = list(work_records.values())

# add calculated fields to each record
final_employee_info = []
for row in result:
    card = row['카드번호']
    date_str = row['날짜']
    weekend = is_weekend_date(date_str)

    # need to get employee info
    emp_info = get_department_by_name(card)
    row.update(emp_info if emp_info else {})

    # add calculated fields
    row['근무OT'] = calc_ot(row['출근'], row['퇴근'])
    row['지각/조퇴'] = calc_late_early(row['출근'], row['퇴근'])
    row['식대'] = calc_meal_allowance(row['출근'], row['퇴근'], weekend)
    row['교통비'] = calc_transport_allowance(row['출근'], row['퇴근'], weekend)

    final_employee_info.append(row)
    
# save to csv file
fieldnames = ['카드번호', '날짜', '출근', '퇴근',
              '근무OT', '지각/조퇴', '식대', '교통비']

# fill in dynamic fields if exist
if final_employee_info and '사원명' in final_employee_info[0]:
    fieldnames += ['사원명']
if final_employee_info and '부서명' in final_employee_info[0]:
    fieldnames += ['부서명']
if final_employee_info and '위치' in final_employee_info[0]:
    fieldnames += ['위치']

csv_filename = txt_filename + '_합본.csv'

with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in final_employee_info:
        row.pop('사원번호', None)  # remove
        writer.writerow(row)

print(f"CSV 파일로 저장 완료: {csv_filename}")


# make monthly summary per employee
monthly_summary = {}

for row in final_employee_info:
    card = row['카드번호']
    if card not in monthly_summary:
        monthly_summary[card] = {
            '카드번호': card,
            '사원명': row.get('사원명', ''),
            '부서명': row.get('부서명', ''),
            '위치': row.get('위치', ''),
            '근무OT': 0.0,
            '지각/조퇴': 0.0,
            '식대': 0,
            '교통비': 0
        }

    # sum up values
    monthly_summary[card]['근무OT'] += row.get('근무OT', 0)
    monthly_summary[card]['지각/조퇴'] += row.get('지각/조퇴', 0)
    monthly_summary[card]['식대'] += row.get('식대', 0)
    monthly_summary[card]['교통비'] += row.get('교통비', 0)

# create summary csv
summary_fieldnames = ['카드번호', '사원명', '부서명', '위치',
                      '근무OT', '지각/조퇴', '식대', '교통비']

summary_csv_filename = txt_filename + '_월합산.csv'

with open(summary_csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=summary_fieldnames)
    writer.writeheader()
    for record in monthly_summary.values():
        writer.writerow(record)

print(f"사원별 월 합산 CSV 저장 완료: {summary_csv_filename}")
