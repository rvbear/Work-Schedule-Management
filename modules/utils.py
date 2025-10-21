import logging
import os
from datetime import datetime


def setup_logger(log_dir='logs'):
    """
    로거 설정
    
    Args:
        log_dir: 로그 파일 저장 디렉토리
        
    Returns:
        Logger: 설정된 로거 객체
    """
    # 로그 디렉토리 생성
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 로거 생성
    logger = logging.getLogger('AttendanceSystem')
    logger.setLevel(logging.INFO)
    
    # 파일 핸들러 설정
    log_file = os.path.join(log_dir, f'attendance_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 포맷 설정
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def validate_file_exists(file_path):
    """
    파일 존재 여부 확인
    
    Args:
        file_path: 파일 경로
        
    Returns:
        bool: 파일 존재 여부
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
    return True


def create_output_directory(output_dir):
    """
    출력 디렉토리 생성
    
    Args:
        output_dir: 출력 디렉토리 경로
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"출력 디렉토리 생성: {output_dir}")


def format_time(time_str):
    """
    시간 포맷 통일 (HH:MM:SS)
    
    Args:
        time_str: 시간 문자열
        
    Returns:
        str: 포맷된 시간 문자열
    """
    if not time_str:
        return None
    
    try:
        # 이미 HH:MM:SS 형식인 경우
        if len(time_str.split(':')) == 3:
            return time_str
        # HH:MM 형식인 경우
        elif len(time_str.split(':')) == 2:
            return time_str + ':00'
        else:
            return time_str
    except:
        return time_str


def get_month_from_filename(filename):
    """
    파일명에서 년월 추출
    
    Args:
        filename: 파일명 (예: '2025년 9월.txt')
        
    Returns:
        tuple: (년, 월)
    """
    import re
    
    # 년도와 월 추출
    match = re.search(r'(\d{4})년\s*(\d{1,2})월', filename)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        return year, month
    
    return None, None
