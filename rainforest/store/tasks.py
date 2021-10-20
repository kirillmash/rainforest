import csv
import os
from datetime import datetime

from django.conf import settings
from celery import shared_task
from django.db import connection

from .models import Reports


@shared_task
def create_task_report(date1, date2):
    sql = """with operations as (
        select pio.product_id, o.status, o.created_at, 
               coalesce(pio.quantity, 0) as quantity, pio.total_cost_by_qty, pio.total_price_by_qty
        from store_productsinorder pio
        left join store_order o on o.id=pio.order_id
    )
    select p.id as product_id , p.title as product_title,
           coalesce(sold_stats.sold_qty, 0) as sold_qty,
           coalesce(refunds.refund_qty, 0) as refund_qty,
           coalesce(sold_stats.sum_revenue, 0) as sum_revenue,
           coalesce(sold_stats.sum_revenue - sold_stats.sum_cost, 0) as profit
    from store_product p
    left join (
            select operations.product_id,
                   sum(operations.quantity)           as sold_qty,
                   sum(operations.total_price_by_qty) as sum_revenue,
                   sum(operations.total_cost_by_qty)  as sum_cost
            from operations
            where operations.status = 1 and operations.created_at  between  %(date1)s and %(date2)s
            group by operations.product_id) sold_stats on p.id=sold_stats.product_id
    left join (select product_id, sum(quantity) as refund_qty from operations where status=4 and created_at  between
     %(date1)s and %(date2)s group by product_id) refunds
        on refunds.product_id=p.id"""

    today = datetime.now()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day_time = today.strftime('%d-%H%M%S')

    dir_path = os.path.join(settings.MEDIA_ROOT, 'reports', year, month)
    os.makedirs(dir_path, exist_ok=True)

    report = Reports.objects.create(title=day_time)
    cursor = connection.cursor()
    cursor.execute(sql, {'date1': date1, 'date2': date2})
    data = cursor.fetchall()

    column_names = [desc[0] for desc in cursor.description]

    full_path = os.path.join(dir_path, f"{day_time}.csv")
    fp = open(full_path, 'w')
    report_file = csv.writer(fp, delimiter=';')
    report_file.writerow(column_names)
    report_file.writerows(data)
    report.file = full_path
    report.is_ready = True
    report.save()
    fp.close()
    return True
