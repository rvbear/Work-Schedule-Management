import pandas as pd
from datetime import datetime

def load_user_data(filepath):
    """
    사용자 정보를 불러옵니다.
    :param filepath: 사용자 정보 파일 경로
    :return: 사용자 데이터프레임 (card_no 기준)
    """
    df = pd.read_excel(filepath)
    # 카드번호 컬럼을 소문자, 언더바 스타일로 통일
    df.rename(columns=lambda x: x.strip(), inplace=True)
    df.rename(columns={'카드번호': 'card_no', '성명': 'name', '부서': 'department', '기본급': 'base_salary'}, inplace=True)
    return df


def load_attendance_data(filepath):
    """
    2025년 9월 raw data 파일을 불러와서
    날짜 | 출근 | 퇴근 | 카드번호 형태의 데이터프레임으로 변환합니다.
    """
    records = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 예: 2025090107591810002
            
            if len(line) < 15:
                print("잘못된 라인:", line)
                continue  # 잘못된 라인 무시

            date_str = line[0:8]  # '20250901'
            time_str = line[8:14]  # '075918'
            code = line[14]  # '1' 또는 '2'
            card_no = line[15:]  # '0002'

            # 날짜 형식 변환
            date = datetime.strptime(date_str, "%Y%m%d").date()
            time = datetime.strptime(time_str, "%H%M%S").time()

            records.append({
                "date": date,
                "time": time,
                "code": code,
                "card_no": card_no
            })

    df = pd.DataFrame(records)

    # 출근/퇴근 각각 가장 이른 출근, 가장 늦은 퇴근으로 피벗팅
    # 1 = 출근, 2 = 퇴근
    df['date'] = pd.to_datetime(df['date'])
    df['time_str'] = df['time'].astype(str)

    # 출근 시간은 code=1 중 가장 빠른 시간
    check_in_df = df[df['code'] == '1'].groupby(['date', 'card_no'])['time'].min().reset_index()
    check_in_df.rename(columns={'time': '출근'}, inplace=True)

    # 퇴근 시간은 code=2 중 가장 늦은 시간
    check_out_df = df[df['code'] == '2'].groupby(['date', 'card_no'])['time'].max().reset_index()
    check_out_df.rename(columns={'time': '퇴근'}, inplace=True)

    # 병합
    merged = pd.merge(check_in_df, check_out_df, on=['date', 'card_no'], how='outer')

    # 날짜 컬럼을 문자열 YYYY-MM-DD 형식으로 변경
    merged['날짜'] = merged['date'].dt.strftime('%Y-%m-%d')

    # 최종 컬럼 순서 맞추기
    final_df = merged[['날짜', '출근', '퇴근', 'card_no']]

    # 시간 타입을 문자열 HH:MM:SS로 변환
    final_df['출근'] = final_df['출근'].apply(lambda x: x.strftime('%H:%M:%S') if pd.notnull(x) else '')
    final_df['퇴근'] = final_df['퇴근'].apply(lambda x: x.strftime('%H:%M:%S') if pd.notnull(x) else '')

    # 카드번호 컬럼명도 snake_case 맞추기
    final_df.rename(columns={'card_no': 'card_no'}, inplace=True)

    return final_df
