import pandas as pd
import os
from datetime import datetime
from modules.parser import DataParser
from modules.calculator import AttendanceCalculator
from modules.report_generator import ReportGenerator
from modules.utils import setup_logger, validate_file_exists, create_output_directory


def main():
    """메인 실행 함수"""
    
    # 로거 설정
    logger = setup_logger()
    logger.info("근태 관리 시스템 시작")
    
    try:
        # 파일 경로 설정
        data_dir = 'data'
        output_dir = 'output'
        config_dir = 'config'
        
        attendance_log_file = os.path.join(data_dir, '2025년 9월.txt')
        employee_info_file = os.path.join(data_dir, '사용자.xlsx')
        overtime_leave_file = os.path.join(data_dir, '연장휴가정보.xlsx')
        rules_file = os.path.join(config_dir, 'rules.json')
        
        # 파일 존재 여부 확인
        logger.info("입력 파일 확인 중...")
        validate_file_exists(attendance_log_file)
        validate_file_exists(employee_info_file)
        validate_file_exists(rules_file)
        
        # 출력 디렉토리 생성
        create_output_directory(output_dir)
        
        # 1. 데이터 파싱
        logger.info("데이터 파싱 시작...")
        parser = DataParser()
        
        # 출퇴근 로그 파싱
        logger.info("출퇴근 로그 파싱 중...")
        attendance_df = parser.parse_attendance_log(attendance_log_file)
        logger.info(f"출퇴근 데이터 {len(attendance_df)}건 로드 완료")
        
        # 사원 정보 파싱
        logger.info("사원 정보 파싱 중...")
        employee_df = parser.parse_employee_info(employee_info_file)
        logger.info(f"사원 정보 {len(employee_df)}건 로드 완료")
        
        # 연장/휴가 정보 파싱 (선택적)
        overtime_df = None
        if os.path.exists(overtime_leave_file):
            logger.info("연장/휴가 정보 파싱 중...")
            overtime_df = parser.parse_overtime_leave_info(overtime_leave_file)
            logger.info(f"연장/휴가 정보 {len(overtime_df)}건 로드 완료")
        
        # 2. 근태 계산
        logger.info("근태 계산 시작...")
        calculator = AttendanceCalculator(rules_file)
        
        # 일별 근태 데이터 계산
        daily_records = []
        
        for _, row in attendance_df.iterrows():
            date = row['date']
            check_in = row['check_in']
            check_out = row['check_out']
            card_number = row['card_number']
            
            # 근무 OT 계산
            work_ot = calculator.calculate_work_ot(check_in, check_out)
            
            # 지각/조퇴 계산
            late_early = calculator.calculate_late_early(check_in, check_out)
            
            # 인정 OT 계산
            approved_ot = calculator.calculate_approved_ot(work_ot, late_early)
            
            # 야간 근무 계산
            night_work = calculator.calculate_night_work(check_in, check_out)
            
            # 휴일 추가 계산
            holiday_bonus = calculator.calculate_holiday_bonus(date, approved_ot)
            
            # 식대 계산
            meal_allowance = calculator.calculate_meal_allowance(check_in, check_out, date)
            
            # 교통비 계산
            transport_allowance = calculator.calculate_transport_allowance(check_in, check_out, date)
            
            # 연장내역 매칭 (선택적)
            overtime_match = ""
            if overtime_df is not None:
                # 연장내역 데이터와 매칭 로직
                # 여기서는 간단히 확인 필요 표시만 추가
                overtime_match = "확인필요" if work_ot > 0 else ""
            
            daily_records.append({
                'date': date,
                'card_number': card_number,
                'check_in': check_in,
                'check_out': check_out,
                'work_ot': work_ot,
                'late_early': late_early,
                'approved_ot': approved_ot,
                'night_work': night_work,
                'holiday_bonus': holiday_bonus,
                'meal_allowance': meal_allowance,
                'transport_allowance': transport_allowance,
                'overtime': work_ot,  # 연장 (근무 OT와 동일)
                'basic_pay': 0,  # 기본급은 별도 계산 필요
                'overtime_match': overtime_match
            })
        
        daily_df = pd.DataFrame(daily_records)
        logger.info(f"일별 근태 계산 완료: {len(daily_df)}건")
        
        # 카드번호 형식 통일 (사원 정보와 매칭을 위해)
        daily_df['카드번호'] = daily_df['card_number'].astype(str).str.zfill(4)
        employee_df['카드번호'] = employee_df['카드번호'].astype(str).str.zfill(4)
        
        # 3. 리포트 생성
        logger.info("리포트 생성 시작...")
        
        # 현재 년월 추출
        year_month = datetime.now().strftime('%Y_%m')
        
        # 월간 합산 리포트
        monthly_report_path = os.path.join(output_dir, f'{year_month}_근태리포트_월간합산.xlsx')
        ReportGenerator.create_monthly_summary_report(daily_df, employee_df, monthly_report_path)
        
        # 일별 상세 리포트
        daily_report_path = os.path.join(output_dir, f'{year_month}_근태리포트_일별상세.xlsx')
        ReportGenerator.create_daily_detail_report(daily_df, employee_df, daily_report_path)
        
        logger.info("근태 관리 시스템 완료")
        print("\n" + "="*50)
        print("✓ 근태 계산 완료")
        print(f"✓ 월간 합산 리포트: {monthly_report_path}")
        print(f"✓ 일별 상세 리포트: {daily_report_path}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"오류 발생: {str(e)}", exc_info=True)
        print(f"\n오류 발생: {str(e)}")
        raise


if __name__ == "__main__":
    main()
