import xlwt
import json

with open("result.json") as log:
    result = json.load(log)
workbook = xlwt.Workbook()
sheet = workbook.add_sheet("hosts", cell_overwrite_ok=True)

col_map = {'id': 0, 'ip': 1, 'ping': 2, 'ssh': 3, 'sudo su -': 4}

for key in col_map:
    sheet.write(0, col_map[key], key)


for i in range(0, len(result)):
    sheet.write(i+1, 0, i)
    sheet.write(i+1, 1, result[i]['ip'])
    sheet.write(i+1, 2, "success" if result[i]['ping']['state'] else "failed")
    sheet.write(i+1, 3, "success" if result[i]['ssh']['login']['state'] else "failed")
    sheet.write(i+1, 4, "success" if result[i]['ssh']['root_sw']['state'] else "failed")

workbook.save("result.xlsx")