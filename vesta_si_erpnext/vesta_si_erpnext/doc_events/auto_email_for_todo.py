import frappe
from frappe.utils import (get_link_to_form)

def get_user_wise_todo():
    data = frappe.db.sql(f"""Select 
                                    name, 
                                    allocated_to, 
                                    description, 
                                    reference_type, 
                                    reference_name, 
                                    date 
                            From 
                                    `tabToDo` 
                            where 
                                    status = 'Open' 
                            Order by 
                                    allocated_to  
                            """, as_dict= 1)
    user_list = frappe.db.get_list("User", pluck="name")
    data_map = {}
    for row in data:
        if not data_map.get(row.allocated_to):
            data_map[row.allocated_to] = []
            data_map[row.allocated_to].append(row)
        else:
            data_map[row.allocated_to].append(row)
    count = 0
    for row in user_list:
        if data_map.get(row):
            html_msg = f"""
                        <p>Dear {frappe.db.get_value("User", row, "full_name")},</p>
                        <p>I hope this message finds you well. Please find below the list of pending tasks for today:</p>
                        <br>
                        <table class="table" border =1><tbody>
                        <tr>
                            <td width="20%">ToDO</td>
                            <td width="20%">Ref Doc</td>
                            <td width="60">Description</td>
                        </tr>"""
            for d in data_map.get(row):
                html_msg += """
                        <tr>
                            <td><p>{0}</p></td>
                            <td><p>{1}</p></td>
                            <td><p>{2}</p></td>
                        </tr>
                """.format(get_link_to_form("ToDo", d.name), get_link_to_form(d.reference_type, d.reference_name), d.description)

            html_msg +="</tbody></table>"
            print(html_msg)
            count+=1
            frappe.sendmail(recipients=["viral@fosserp.com"], subject="Pending ToDo List", message=html_msg)
            if count ==2:
                break