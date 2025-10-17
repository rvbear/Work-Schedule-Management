import csv
from formatting_utils import format_date, format_time
from employee_info import get_department_by_name

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
                    'employee_card': card_num,
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


# test start : save to csv file
def convert_to_korean(row):
    # map to korean column names
    return {
        '카드번호': row.get('employee_card', ''),
        '날짜': row.get('date', ''),
        '출근': row.get('clock_in', ''),
        '퇴근': row.get('clock_out', '')
    }

fieldnames = ['카드번호', '날짜', '출근', '퇴근']
csv_filename = txt_filename + '_합본.csv'

with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in result:
        writer.writerow(convert_to_korean(row))

print(f"CSV 파일로 저장 완료: {csv_filename}")
# done


# test start : search employee_info by card number
card_num = input("카드번호를 입력하세요: ")
employee_info = get_department_by_name(card_num)

work_records_filtered = [record for record in result if record['employee_card'] == card_num]

for record in work_records_filtered:
    print(record)
# done
