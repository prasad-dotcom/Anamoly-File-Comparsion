# logic/logic_module.py
import pandas as pd
import os

# Define global character lists
validchar_list1 = list("abcdefghijklm")
validchar_list2 = list("nopqrstuvwxyz")
validchar_list3 = list("0123456789_")
validchar_list4 = ["."]
validchar_list5 = list("ABCDEFGHIJKLM")
validchar_list6 = list("NOPQRSTUVWXYZ")

validchar_list = validchar_list1 + validchar_list2 + validchar_list3
validchar_list_iot = validchar_list + validchar_list4 + validchar_list5 + validchar_list6
iot_obj_type_list = ["stream", "realtime", "nearrealtime", "archival"]
ignore_list = ["n/a", "n.a", "na", "tbd", "tbc"]
dtyp_list = ["curr", "quan", "dec", "fltp", "int", "int64", "integer", "decimal", "int2", "int64", "int32"]

# Global DataFrame to collect logs
df_log = pd.DataFrame(columns = ['msg-num', 'msg-type', 'xl-worksheet', 'xl-row', 'msg-text'])

# Logging function
def log_message(iTyp, iWksht, iRow, iMsg):
    global df_log
    iTypMap = {'e': (0, 'error'), 'w': (1, 'warning'), 'i': (2, 'info')}
    iNum, iTyp = iTypMap.get(iTyp, (2, 'info'))
    df_log.loc[len(df_log)] = [iNum, iTyp, iWksht, iRow, iMsg]

def log_sort_index():
    global df_log
    df_log.sort_values(by=['msg-num', 'xl-worksheet', 'xl-row', 'msg-text'], inplace=True)
    df_log.reset_index(drop=True, inplace=True)
    return df_log[['msg-type', 'xl-worksheet', 'xl-row', 'msg-text']]

# Replace this with your actual comparison logic
def compare_files(user_file_path, master_file_path):
    global df_log
    df_log.drop(df_log.index, inplace=True)  # clear previous logs

    # Example logic: check if both files exist
    if not os.path.exists(user_file_path):
        log_message('e', '-', '-', f'User file not found: {user_file_path}')
    if not os.path.exists(master_file_path):
        log_message('e', '-', '-', f'Master file not found: {master_file_path}')

    # Add your processing logic here...
    # Example: read Excel and do some comparison
    try:
        user_df = pd.read_excel(user_file_path)
        master_df = pd.read_excel(master_file_path)

        # You can now call your helper functions here using user_df and master_df
        log_message('i', '-', '-', f'Files loaded and ready for processing.')

        # Simulate comparison
        if user_df.shape != master_df.shape:
            log_message('w', '-', '-', f'Different shape: user={user_df.shape}, master={master_df.shape}')
        else:
            log_message('i', '-', '-', f'Same shape.')

    except Exception as e:
        log_message('e', '-', '-', str(e))

    return log_sort_index()

# Define the message log DataFrame (initialize if needed)
df_log = pd.DataFrame(columns=["type", "sheet", "key", "message"])  # adjust columns to match your actual log schema

def log_message(msg_type, sheet, key, message):
    """Log error, warning, or info messages into df_log."""
    global df_log
    df_log.loc[len(df_log)] = [msg_type, sheet, key, message]

def log_sort_index():
    """Sort log to show messages in error > warning > info order."""
    priority = {"e": 0, "w": 1, "i": 2}
    df_log["priority"] = df_log["type"].map(priority)
    df_log.sort_values(by="priority", inplace=True)
    df_log.drop(columns="priority", inplace=True)

# Instead of tkinter, accept the file path from Flask (e.g., passed as a function argument)
def process_tdd_file(file_tdd):
    df_log.drop(df_log.index, inplace=True)  # refresh log for this block

    file_tdd ="path_to_uploaded_file.xlsx"

    if not file_tdd:
        log_message('e', '-', '-', 'tdd not found / supplied')
    else:
        log_message('i', '-', '-', os.path.basename(file_tdd).upper() + ' review')

    log_records = []
    if not df_log.empty:
        log_sort_index()
        log_records = df_log.to_dict(orient='records')
    
    return log_records


# 🔁 Replaces manual file dialog — Flask saves the uploaded file into 'static/predefined_file/'
file_cm = "static/predefined_file/config_master.xlsx"

# 🧹 Clear the log before reading
df_log.drop(df_log.index, inplace=True)

try:
    df_cm = pd.read_excel(file_cm, sheet_name="gcp-config-master", keep_default_na=False, dtype={'last_update': str})
except Exception as e:
    log_message('e', 'config', '-', str(e))
    df_cm = pd.DataFrame()  # ensure df_cm exists even if error occurs

# ✅ Add 'rowkey' column for joining later
if not df_cm.empty:
    try:
        df_cm["rowkey"] = (
            df_cm["region"]
            + df_cm["data_entity"]
            + df_cm["entity_suffix"]
            + df_cm["source_system"]
            + df_cm["source_object"]
            + df_cm["landing_project"]
            + df_cm["datalake_project"]
            + df_cm["harmonized_dataset"]
        ).str.lower()
    except Exception as e:
        log_message('e', 'config', '-', f"Error creating rowkey: {str(e)}")

# ✅ Convert log to a list of dicts (e.g., for HTML display later)
log_records = []
if not df_log.empty:
    log_sort_index()
    log_records = df_log.to_dict(orient='records')

def process_tdd_summary(file_tdd, df_cm):
    """
    Reads and processes the TDD summary sheet from the uploaded Excel file.
    Requires: file_tdd path and df_cm (already processed config master DataFrame).
    Returns: Processed df_tdd_summary and log_records.
    """

    global df_log
    df_log.drop(df_log.index, inplace=True)  # 🔁 refresh log before this block

    # 1️⃣ Read the full Excel file as a dictionary of dataframes
    try:
        df_tdd_full = pd.read_excel(file_tdd, sheet_name=None, keep_default_na=False)
    except Exception as e:
        log_message('e', 'tdd', '-', str(e))
        df_tdd_full = {}

    # 2️⃣ Try to extract and normalize the "Summary" sheet
    try:
        df_tdd_summary = df_tdd_full.get('Summary')
        df_tdd_summary.columns = df_tdd_summary.columns.str.replace(' ', '_').str.lower()
    except Exception as e:
        log_message('e', 'summary', '-', str(e))
        df_tdd_summary = pd.DataFrame()

    # 3️⃣ Attempt both rowkey formats (GCP-based or REGION-based) as per v8.0 logic
    try:
        df_tdd_summary["rowkey"] = (
            df_tdd_summary["gcp"]
            + df_tdd_summary["data_entity"]
            + df_tdd_summary["entity_suffix"]
            + df_tdd_summary["source_system"]
            + df_tdd_summary["source_object"]
            + df_tdd_summary["landing_project"]
            + df_tdd_summary["data_lake_project"]
            + df_tdd_summary["harmonized_dataset"]
        ).str.lower()
    except:
        try:
            df_tdd_summary["rowkey"] = (
                df_tdd_summary["region"]
                + df_tdd_summary["data_entity"]
                + df_tdd_summary["entity_suffix"]
                + df_tdd_summary["source_system"]
                + df_tdd_summary["source_object"]
                + df_tdd_summary["landing_project"]
                + df_tdd_summary["data_lake_project"]
                + df_tdd_summary["harmonized_dataset"]
            ).str.lower()
        except Exception as e:
            log_message('e', 'summary', '-', f"Error creating rowkey: {str(e)}")

    # 4️⃣ Clean and merge
    df_tdd_summary.reset_index(drop=True, inplace=True)

    # Merge with config master on rowkey
    if not df_cm.empty and not df_tdd_summary.empty:
        try:
            df_tdd_summary = pd.merge(
                df_tdd_summary,
                df_cm[['rowkey', 'source_object_type']],
                on='rowkey',
                how='inner'
            )
        except Exception as e:
            log_message('e', 'summary', '-', f"Error during merge: {str(e)}")

    # 5️⃣ Convert log to list of dicts for HTML rendering (if needed)
    log_records = []
    if not df_log.empty:
        log_sort_index()
        log_records = df_log.to_dict(orient='records')

    return df_tdd_summary, log_records

# ✅ Filter config master rows where rowkey exists in TDD summary
df_cm_wip = df_cm[df_cm["rowkey"].isin(df_tdd_summary["rowkey"])]

# ✅ Overwrite the original config master with this filtered version
df_cm = df_cm_wip.reset_index(drop=True)  # optional: reset index for cleanliness


