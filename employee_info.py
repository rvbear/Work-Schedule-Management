import pandas as pd

# read xlsx file
excel_filename = input("파일 이름을 입력하세요: ")
if not excel_filename:
    print("파일 이름을 확인해주세요.")
    exit(1)
    
excel_file = excel_filename + '.xlsx'
df = pd.read_excel(excel_file)

employee_info_list = []

def format_code(num):
    # 22 -> '0022'
    return f"{num:0>4}"

def format_id(id):
    # 12345678 -> '012345678' (9자리)
    id_str = str(id).strip()
    if id_str.isdigit():
        return f"{int(id_str):0>9}"
    return id_str

for _, row in df.iterrows():
    employee_id = row.get('사원코드', '')
    employee_name = row.get('사원명', '')
    department_id = row.get('부서코드', '')
    department_name = row.get('부서명', '')
    employee_card = row.get('카드번호', '')
    position = row.get('직급', '')
    
    employee_info = {
        'employee_id': format_id(employee_id),
        'employee_name': employee_name,
        'department_id': format_code(department_id),
        'department_name': department_name,
        'employee_card': format_code(employee_card),
        'position': position,
    }
    employee_info_list.append(employee_info)

def get_department_by_name(employee_card):
    for info in employee_info_list:
        if info['employee_card'] == employee_card:
            return info['employee_name'], info['department_name']
    return None

# test code
print(get_department_by_name(input("카드번호를 입력하세요: ")))