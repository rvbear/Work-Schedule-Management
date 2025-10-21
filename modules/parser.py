import pandas as pd
import re


class DataParser:
    """데이터 파싱을 담당하는 클래스"""
    
    @staticmethod
    def parse_attendance_log(file_path):
        """
        출퇴근 로그 TXT 파일을 파싱
        
        Args:
            file_path: TXT 파일 경로
            
        Returns:
            DataFrame: 날짜, 출근, 퇴근, 카드번호 컬럼을 가진 데이터프레임
        """
        attendance_records = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 각 라인을 파싱
        for line in lines:
            line = line.strip()
            if len(line) < 18:
                continue
                
            # 날짜 추출 (YYYYMMDD)
            date_str = line[0:8]
            date = f"{date_str[0:4]}-{date_str[4:6]}-{date_str[6:8]}"
            
            # 시간 추출 (HHMMSS)
            time_str = line[8:14]
            time = f"{time_str[0:2]}:{time_str[2:4]}:{time_str[4:6]}"
            
            # 코드 추출 (1: 출근, 2: 퇴근)
            code = line[14:15]
            
            # 카드번호 추출
            card_number = line[15:]
            
            attendance_records.append({
                'date': date,
                'time': time,
                'code': code,
                'card_number': card_number
            })
        
        df = pd.DataFrame(attendance_records)
        
        # 날짜와 카드번호로 그룹화하여 출근/퇴근 시간 분리
        result = []
        for (date, card_number), group in df.groupby(['date', 'card_number']):
            check_in = None
            check_out = None
            
            for _, row in group.iterrows():
                if row['code'] == '1':
                    # 출근 시간 (가장 빠른 시간)
                    if check_in is None or row['time'] < check_in:
                        check_in = row['time']
                elif row['code'] == '2':
                    # 퇴근 시간 (가장 늦은 시간)
                    if check_out is None or row['time'] > check_out:
                        check_out = row['time']
            
            result.append({
                'date': date,
                'check_in': check_in,
                'check_out': check_out,
                'card_number': card_number
            })
        
        return pd.DataFrame(result)
    
    
    @staticmethod
    def parse_employee_info(file_path):
        """
        사원 정보 Excel 파일을 파싱
        
        Args:
            file_path: Excel 파일 경로
            
        Returns:
            DataFrame: 사원 정보 데이터프레임 (위치 필드 추가)
        """
        df = pd.read_excel(file_path)
        
        # 위치 필드 추가
        def extract_location(dept_name):
            """부서명에서 위치 추출 (괄호 안 값 또는 기본값 '화성')"""
            if pd.isna(dept_name):
                return '화성'
            
            # 괄호 안의 값 추출
            match = re.search(r'\(([^)]+)\)', str(dept_name))
            if match:
                return match.group(1)
            return '화성'
        
        df['location'] = df['부서명'].apply(extract_location)
        
        return df
    
    
    @staticmethod
    def parse_overtime_leave_info(file_path):
        """
        연장/휴가 정보 Excel 파일을 파싱
        
        Args:
            file_path: Excel 파일 경로
            
        Returns:
            DataFrame: 연장/휴가 정보 데이터프레임
        """
        df = pd.read_excel(file_path)
        
        # 날짜 형식 통일
        if 'date' in df.columns or '날짜' in df.columns:
            date_col = 'date' if 'date' in df.columns else '날짜'
            df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')
        
        return df
