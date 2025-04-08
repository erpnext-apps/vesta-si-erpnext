import frappe
from datetime import date, timedelta
from frappe.utils import getdate, today
import calendar

def get_working_days(year, month):
    num_days = calendar.monthrange(year, month)[1]
    working_days = [
        date(year, month, day)
        for day in range(1, num_days + 1)
        if date(year, month, day).weekday() < 5  # 0 to 4 -> Monday to Friday
    ]
    return working_days

def get_second_and_middle_working_day():
    today = getdate()
    year, month = today.year, today.month

    working_days = get_working_days(year, month)

    if len(working_days) < 2:
        second_working_day = None
    else:
        second_working_day = working_days[1]

    if working_days:
        middle_index = len(working_days) // 2
        middle_working_day = working_days[middle_index]
    else:
        middle_working_day = None

    return second_working_day, middle_working_day


#Received Items To Be Billed - Vesta Si-1
#Auto Email Report "Received Items To Be Billed - Vesta Si-1" should be disabled
def send_report():
    second_day, middle_day = get_second_and_middle_working_day()
    auto_email_report = frappe.get_doc("Auto Email Report", "Received Items To Be Billed (GRIR) Vesta")
    user_list = get_users_by_role("PR Notify")
    print(user_list)
    auto_email_report.email_to = "\n".join(user_list)
    if second_day == getdate() or middle_day == getdate():
        auto_email_report.send()
        

def get_users_by_role(role_name):
    users = frappe.db.sql("""
        SELECT rol.parent as name 
        FROM `tabHas Role` as rol
        left Join `tabUser` as user ON user.name = rol.parent
        WHERE rol.role = %s and user.enabled = 1
    """, (role_name,), as_dict=True)
    return [user["name"] for user in users]

