import pandas as pd
from formatting_utils import format_code, format_id

# read xlsx file
print("직원 정보 파일을 읽습니다.")
excel_filename = input("파일 이름을 입력하세요: ")
if not excel_filename:
    print("파일 이름을 확인해주세요.")
    exit(1)
    
excel_file = excel_filename + '.xlsx'
df = pd.read_excel(excel_file)

employee_info_list = []

for _, row in df.iterrows():
    employee_id = row.get('사원코드', '')
    employee_name = row.get('사원명', '')
    department_id = row.get('부서코드', '')
    department_parts = row.get('부서명', '')
    if '(' in department_parts and ')' in department_parts:
        department_name, department_location = department_parts.split('(', 1)
        department_location = department_location.rstrip(')')
    else:
        department_name = department_parts.strip()
        department_location = '본사'
    employee_card = row.get('카드번호', '')
    position = row.get('직급', '')
    
    employee_info = {
        'employee_id': format_id(employee_id),
        'employee_name': employee_name,
        'department_id': format_code(department_id),
        'department_name': department_name,
        'department_location': department_location,
        'employee_card': format_code(employee_card),
        'position': position,
    }
    employee_info_list.append(employee_info)


def get_department_by_name(employee_card):
    for info in employee_info_list:
        if info['employee_card'] == employee_card:
            return {
                        "사원번호": info['employee_id'],
                        "사원명": info['employee_name'], 
                        "부서명": info['department_name'],
                        "위치": info['department_location'] 
                    }
    return None
