import os
import re
import csv
import sys

def clean_val(val):
    if val == 'NULL':
        return ''
    # Strip quotes if string
    if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
        content = val[1:-1]
        # Unescape standard SQL escapes
        content = content.replace("\\'", "'").replace('\\"', '"').replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t').replace('\\\\', '\\')
        return content
    return val

def parse_values(s):
    row = []
    in_str = False
    str_char = None
    curr = []
    i = 0
    n = len(s)
    rows = []
    while i < n:
        c = s[i]
        if not in_str:
            if c == '(' and not curr:
                pass
            elif c == '\'' or c == '\"':
                in_str = True
                str_char = c
                curr.append(c)
            elif c == ',':
                if curr:
                    row.append(clean_val(''.join(curr).strip()))
                    curr = []
            elif c == ')':
                if curr:
                    row.append(clean_val(''.join(curr).strip()))
                    curr = []
                rows.append(row)
                row = []
                i += 1
                while i < n and (s[i] == ',' or s[i].isspace()):
                    i += 1
                continue
            else:
                curr.append(c)
        else:
            curr.append(c)
            if c == str_char:
                bs_count = 0
                idx = i - 1
                while idx >= 0 and s[idx] == '\\':
                    bs_count += 1
                    idx -= 1
                if bs_count % 2 == 0:
                    in_str = False
        i += 1
    return rows

def parse_sql_dump(sql_file_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    current_table = None
    table_columns = {}
    table_data = {}
    
    print(f"📖 Reading and parsing SQL dump: {sql_file_path}")
    
    with open(sql_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        in_create_table = False
        
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            
            # Detect CREATE TABLE
            create_match = re.match(r'^CREATE TABLE `([a-zA-Z0-9_]+)` \(', stripped, re.IGNORECASE)
            if create_match:
                current_table = create_match.group(1)
                table_columns[current_table] = []
                table_data[current_table] = []
                in_create_table = True
                continue
            
            if in_create_table:
                # Detect end of CREATE TABLE
                if stripped.startswith(')') or stripped.endswith(';'):
                    in_create_table = False
                    current_table = None
                    continue
                # Extract column names
                col_match = re.match(r'^`([a-zA-Z0-9_]+)`', stripped)
                if col_match and current_table:
                    table_columns[current_table].append(col_match.group(1))
                continue
            
            # Detect INSERT INTO statements
            insert_match = re.match(r'^INSERT INTO `([a-zA-Z0-9_]+)` VALUES\s*(.*)', stripped, re.IGNORECASE)
            if insert_match:
                table_name = insert_match.group(1)
                vals_part = insert_match.group(2).strip()
                if vals_part.endswith(';'):
                    vals_part = vals_part[:-1]
                
                if table_name not in table_columns:
                    table_columns[table_name] = []
                    table_data[table_name] = []
                
                rows = parse_values(vals_part)
                table_data[table_name].extend(rows)

    print("\n✍️ Writing parsed tables to CSV files...")
    for table_name, rows in table_data.items():
        columns = table_columns.get(table_name, [])
        csv_file_path = os.path.join(output_dir, f"{table_name}.csv")
        
        total_rows = len(rows)
        print(f"📦 Table '{table_name}': columns={len(columns)}, rows={total_rows}")
        
        if rows and len(columns) < len(rows[0]):
            columns = [f"column_{i}" for i in range(len(rows[0]))]
            
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if columns:
                writer.writerow(columns)
            writer.writerows(rows)
            
        print(f"  ✅ Exported {total_rows} rows to {csv_file_path}")

    print("\n🎉 Done! All legacy tables exported to CSV format.")

if __name__ == '__main__':
    sql_path = 'camperscloset_prod_backup.sql'
    if len(sys.argv) > 1:
        sql_path = sys.argv[1]
    parse_sql_dump(sql_path, 'exports_legacy')
