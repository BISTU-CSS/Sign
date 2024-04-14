# -*- coding: UTF-8 -*-
import pandas as pd
from datetime import datetime, timedelta
import sys

def process_csv_to_excel(csv_prefix):
    # 取前缀
    input_csv = f'{csv_prefix}.csv'
    output_excel = f'1-{csv_prefix}.xlsx'

    # 读取数据，用GBK
    data = pd.read_csv(input_csv, encoding='gbk')
    
    # .csv第四列日期时间连在一起，需要分离日期时间
    data['日期'] = pd.to_datetime(data['日期'], format='%Y-%m-%d %H:%M:%S')
    data['Date'] = data['日期'].dt.date
    data['Time'] = data['日期'].dt.time

    # 定义时间段
    morning_start = datetime.strptime("07:00:00", "%H:%M:%S").time()
    morning_end = datetime.strptime("12:30:00", "%H:%M:%S").time()
    afternoon_start = morning_end
    afternoon_end = datetime.strptime("18:00:00", "%H:%M:%S").time()
    evening_start = afternoon_end
    evening_end = datetime.strptime("23:30:00", "%H:%M:%S").time()

    # 处理时间数据
    def compute_hours(time_list, start, end):
        filtered_times = [t for t in time_list if start <= t <= end]
        if len(filtered_times) > 1:
            max_time = datetime.combine(datetime.today(), max(filtered_times))
            min_time = datetime.combine(datetime.today(), min(filtered_times))
            return (max_time - min_time).seconds / 3600
        elif len(filtered_times) == 1:
            return 1.0
        return 0.0

    output_data = []

    for (name, date), group in data.groupby(['姓名', 'Date']):
        times = group['Time'].tolist()
        morning_hours = compute_hours(times, morning_start, morning_end)
        afternoon_hours = compute_hours(times, afternoon_start, afternoon_end)
        evening_hours = compute_hours(times, evening_start, evening_end)
        
        output_data.append({
            '姓名': name,
            '上午段': morning_hours,
            '下午段': afternoon_hours,
            '夜晚段': evening_hours
        })

    # 转换为DataFrame并计算总工作时间
    output_df = pd.DataFrame(output_data)
    summary_df = output_df.groupby('姓名').agg({
        '上午段':'sum', 
        '下午段':'sum', 
        '夜晚段':'sum'
    }).reset_index()
    summary_df['总时间'] =summary_df['上午段'] + summary_df['下午段'] + summary_df['夜晚段']

    # 保存到Excel
    summary_df.to_excel(output_excel, index=False)
    print(f"Data saved to {output_excel}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 1-sign.py <csv_prefix>")
        sys.exit(1)
    csv_prefix = sys.argv[1]
    process_csv_to_excel(csv_prefix)

