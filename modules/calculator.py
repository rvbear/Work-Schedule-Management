from datetime import datetime, timedelta
import json


class AttendanceCalculator:
    """근태 및 수당 계산을 담당하는 클래스"""
    
    def __init__(self, rules_path):
        """
        초기화
        
        Args:
            rules_path: 규칙 JSON 파일 경로
        """
        with open(rules_path, 'r', encoding='utf-8') as f:
            self.rules = json.load(f)
    
    
    def calculate_time_difference(self, start_time, end_time):
        """
        두 시간의 차이를 시간 단위로 계산
        
        Args:
            start_time: 시작 시간 (HH:MM:SS)
            end_time: 종료 시간 (HH:MM:SS)
            
        Returns:
            float: 시간 차이
        """
        if not start_time or not end_time:
            return 0
        
        fmt = '%H:%M:%S'
        start = datetime.strptime(start_time, fmt)
        end = datetime.strptime(end_time, fmt)
        
        # 자정을 넘어가는 경우 처리
        if end < start:
            end += timedelta(days=1)
        
        diff = (end - start).total_seconds() / 3600
        return diff
    
    
    def round_to_half_hour(self, hours):
        """
        30분 단위로 반올림 (30분 이상이면 0.5, 미만이면 0)
        
        Args:
            hours: 시간
            
        Returns:
            float: 반올림된 시간
        """
        if hours <= 0:
            return 0
        
        # 정수 부분
        integer_part = int(hours)
        # 소수 부분
        decimal_part = hours - integer_part
        
        # 소수 부분을 분으로 변환 (0~59분)
        minutes = decimal_part * 60
        
        # 30분 미만이면 0, 30분 이상이면 0.5
        if minutes >= 30:
            return integer_part + 0.5
        else:
            return float(integer_part)
    
    
    def is_time_in_period(self, check_time, period_start, period_end):
        """
        특정 시간이 기간 내에 포함되는지 확인
        
        Args:
            check_time: 확인할 시간 (HH:MM:SS)
            period_start: 기간 시작 (HH:MM)
            period_end: 기간 종료 (HH:MM)
            
        Returns:
            bool: 포함 여부
        """
        fmt_check = '%H:%M:%S'
        fmt_period = '%H:%M'
        
        check = datetime.strptime(check_time, fmt_check)
        start = datetime.strptime(period_start, fmt_period)
        end = datetime.strptime(period_end, fmt_period)
        
        # 자정을 넘어가는 경우 처리
        if end <= start:
            return check >= start or check < end
        
        return start <= check < end
    
    
    def calculate_excluded_time(self, start_time, end_time, exclusion_periods):
        """
        제외 기간에 해당하는 시간 계산
        
        Args:
            start_time: 시작 시간
            end_time: 종료 시간
            exclusion_periods: 제외 기간 리스트
            
        Returns:
            float: 제외 시간
        """
        if not start_time or not end_time:
            return 0
        
        excluded_hours = 0
        
        for period in exclusion_periods:
            period_start = period['start']
            period_end = period['end']
            
            # 근무 시간이 제외 기간과 겹치는지 확인
            if self.is_work_overlap_period(start_time, end_time, period_start, period_end):
                excluded_hours += 1  # 각 제외 기간은 1시간
        
        return excluded_hours
    
    
    def is_work_overlap_period(self, work_start, work_end, period_start, period_end):
        """
        근무 시간이 특정 기간과 겹치는지 확인
        
        Args:
            work_start: 근무 시작 시간
            work_end: 근무 종료 시간
            period_start: 기간 시작
            period_end: 기간 종료
            
        Returns:
            bool: 겹침 여부
        """
        fmt_work = '%H:%M:%S'
        fmt_period = '%H:%M'
        
        work_s = datetime.strptime(work_start, fmt_work)
        work_e = datetime.strptime(work_end, fmt_work)
        period_s = datetime.strptime(period_start, fmt_period)
        period_e = datetime.strptime(period_end, fmt_period)
        
        # 자정을 넘어가는 경우 처리
        if work_e < work_s:
            work_e += timedelta(days=1)
        
        if period_e <= period_s:
            period_e += timedelta(days=1)
        
        # 겹침 여부 확인
        return not (work_e <= period_s or work_s >= period_e)
    
    
    def calculate_work_ot(self, check_in, check_out):
        """
        근무 OT 계산 (총 근무시간 - 8시간 - 제외 시간)
        
        Args:
            check_in: 출근 시간
            check_out: 퇴근 시간
            
        Returns:
            float: 근무 OT 시간
        """
        if not check_in or not check_out:
            return 0
        
        # 총 근무 시간 계산
        total_hours = self.calculate_time_difference(check_in, check_out)
        
        # 제외 기간 시간 계산
        excluded_hours = self.calculate_excluded_time(
            check_in, check_out, 
            self.rules['overtime_exclusion_periods']
        )
        
        # 근무 OT = 총 근무시간 - 제외시간 - 기본 8시간
        work_ot = total_hours - excluded_hours - self.rules['work_hours']['standard_hours']
        
        # 30분 단위로 반올림
        return self.round_to_half_hour(max(0, work_ot))
    
    
    def calculate_late_early(self, check_in, check_out):
        """
        지각/조퇴 시간 계산
        
        Args:
            check_in: 출근 시간
            check_out: 퇴근 시간
            
        Returns:
            float: 지각/조퇴 시간
        """
        late_early = 0
        
        standard_start = self.rules['work_hours']['standard_start'] + ':00'
        standard_end = self.rules['work_hours']['standard_end'] + ':00'
        
        # 지각 계산
        if check_in and check_in > standard_start:
            late_hours = self.calculate_time_difference(standard_start, check_in)
            late_early += late_hours
        
        # 조퇴 계산
        if check_out and check_out < standard_end:
            early_hours = self.calculate_time_difference(check_out, standard_end)
            late_early += early_hours
        
        # 30분 단위로 반올림
        return self.round_to_half_hour(late_early)
    
    
    def calculate_approved_ot(self, work_ot, late_early):
        """
        인정 OT 계산
        
        Args:
            work_ot: 근무 OT
            late_early: 지각/조퇴 시간
            
        Returns:
            float: 인정 OT
        """
        if work_ot > 0:
            if late_early > 0:
                return max(0, work_ot - late_early)
            else:
                return work_ot
        return 0
    
    
    def calculate_night_work(self, check_in, check_out):
        """
        야간 근무 시간 계산 (22:00~06:00, 제외 기간 제외)
        
        Args:
            check_in: 출근 시간
            check_out: 퇴근 시간
            
        Returns:
            float: 야간 근무 시간
        """
        if not check_in or not check_out:
            return 0
        
        night_hours = 0
        night_config = self.rules['night_work_period']
        
        # 야간 시간대와 근무 시간이 겹치는 부분 계산
        # 간단한 구현: 22:00 이후 또는 06:00 이전 근무 확인
        fmt = '%H:%M:%S'
        check_in_time = datetime.strptime(check_in, fmt)
        check_out_time = datetime.strptime(check_out, fmt)
        
        # 자정을 넘어가는 경우 처리
        if check_out_time < check_in_time:
            check_out_time += timedelta(days=1)
        
        night_start = datetime.strptime('22:00:00', fmt)
        night_end = datetime.strptime('06:00:00', fmt) + timedelta(days=1)
        
        # 야간 시간대와 겹치는 부분 계산
        overlap_start = max(check_in_time, night_start)
        overlap_end = min(check_out_time, night_end)
        
        if overlap_start < overlap_end:
            night_hours = (overlap_end - overlap_start).total_seconds() / 3600
            
            # 제외 기간 차감
            excluded_hours = self.calculate_excluded_time(
                check_in, check_out,
                night_config['exclusion_periods']
            )
            night_hours = max(0, night_hours - excluded_hours)
        
        # 30분 단위로 반올림
        return self.round_to_half_hour(night_hours)
    
    
    def calculate_holiday_bonus(self, date, approved_ot):
        """
        휴일 추가 계산 (일요일이고 인정 OT가 8시간 이상인 경우)
        
        Args:
            date: 날짜 (YYYY-MM-DD)
            approved_ot: 인정 OT
            
        Returns:
            float: 휴일 추가 (8시간 또는 0)
        """
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        
        # 일요일(6)인지 확인
        if date_obj.weekday() == 6:  # 0=월요일, 6=일요일
            if approved_ot >= self.rules['holiday_bonus']['min_approved_ot_hours']:
                return 8.0
        
        return 0
    
    
    def calculate_meal_allowance(self, check_in, check_out, date):
        """
        식대 계산
        
        Args:
            check_in: 출근 시간
            check_out: 퇴근 시간
            date: 날짜
            
        Returns:
            int: 식대 금액
        """
        if not check_in or not check_out:
            return 0
        
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        is_weekend = date_obj.weekday() >= 5  # 5=토요일, 6=일요일
        
        meal_config = self.rules['meal_allowance']
        periods = meal_config['weekend_periods'] if is_weekend else meal_config['weekday_periods']
        
        count = 0
        for period in periods:
            if self.is_work_overlap_period(check_in, check_out, period['start'], period['end']):
                count += 1
        
        return count * meal_config['amount_per_period']
    
    
    def calculate_transport_allowance(self, check_in, check_out, date):
        """
        교통비 계산
        
        Args:
            check_in: 출근 시간
            check_out: 퇴근 시간
            date: 날짜
            
        Returns:
            int: 교통비 금액
        """
        if not check_in:
            return 0
        
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        is_weekend = date_obj.weekday() >= 5
        
        transport_config = self.rules['transport_allowance']
        
        if is_weekend:
            # 주말: 출근만 하면 5000원
            return transport_config['weekend_amount']
        else:
            # 평일: 퇴근 시간이 22:00 이후면 5000원
            if check_out and check_out >= '22:00:00':
                return transport_config['weekday_amount']
        
        return 0
