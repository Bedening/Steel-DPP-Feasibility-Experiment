import re
import pandas as pd
import matplotlib.pyplot as plt
import os


groupsize = 1000


# Set the directory containing your files
folder_path = './data'

# durations
# Compile a regex pattern to match filenames like 'log-0-', 'log-1-', etc.
pattern = re.compile(r'^log-\d+-.*\.txt$')

# Filter files using the regex pattern
file_list = [file for file in os.listdir(folder_path) if pattern.match(file)]

# Merge the content of all files into one string
log_data = ''
for file_name in file_list:
    file_path = os.path.join(folder_path, file_name)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            log_data += file.read() + '\n'  # Add newline between files
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        exit()

# Define regex pattern to extract required fields
pattern = r"R=(\d+), TT=([\w]+), NTX=([\w\->]+), .*?, D=(\d+\.\d+)s"

# Find all matches in the log data
matches = re.findall(pattern, log_data)

# Create a DataFrame from the matches
df = pd.DataFrame(matches, columns=["Round", "TransactionType", "NumberTXs", "Duration"])

print("\n")
print(df)


# sizes
# Compile a regex pattern to match filenames like 'log-0-', 'log-1-', etc.
pattern_s = re.compile(r'^log-\d+\.txt$')

# Filter files using the regex pattern
file_list_s = [file for file in os.listdir(folder_path) if pattern_s.match(file)]

# Merge the content of all files into one string
log_data_s = ''
for file_name in file_list_s:
    file_path = os.path.join(folder_path, file_name)
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            log_data_s += file.read() + '\n'  # Add newline between files
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        exit()

# Define regex pattern to extract required fields
pattern = r"R=(\d+), TT=([\w]+), NTX=([\w\->]+), .*?, D=(\d+\.\d+)s"
size_pattern = r"R=(\d+).*?Sizes:  BC: (\d+) KB  CDB: (\d+) KB"

# Find all matches in the log data
matches = re.findall(pattern, log_data)
size_matches = re.findall(size_pattern, log_data_s, re.DOTALL)

# Create a DataFrame from the matches
df = pd.DataFrame(matches, columns=["Round", "TransactionType", "NumberTXs", "Duration"])
df_size = pd.DataFrame(size_matches, columns=["Round", "BC Size", "CDB Size"])

print("\n")
print(df)
print("\n")
print(df_size)





# Define a function to spell out transaction types
def spellout_transaction_type(transaction_type):
    #  ['RebCr', 'RebTrOw', 'StCr', 'TinCr', 'TinTrOw']:
    if transaction_type == 'StCr':
        return 'Steel Creation'
    elif transaction_type == 'RebCr':
        return 'Rebar Creation'
    elif transaction_type == 'TinCr': 
        return 'Tin Creation'
    elif transaction_type == 'RebTrOw':
        return 'Rebar Trans Owner'
    elif transaction_type == 'TinTrOw':
        return 'Tin Trans Owner'
    else:
        return 'Other'

# Define a function to group transaction types
def group_transaction_type(transaction_type):
    if 'Cr' in transaction_type:
        return 'Crea'
    elif 'TrOw' in transaction_type:
        return 'TrOw'
    else:
        return 'Other'

# Apply the function to create a new column 'TransactionGroup'
df['TransactionGroup'] = df['TransactionType']


# Convert Round column to numeric for correct sorting
df["Round"] = pd.to_numeric(df["Round"])
df_size["Round"] = pd.to_numeric(df_size["Round"])

# Convert to numeric
df["Duration"] = pd.to_numeric(df["Duration"])
df["NumberTXs"] = pd.to_numeric(df["NumberTXs"])
df_size["BC Size"] = pd.to_numeric(df_size["BC Size"]) // (1024)
df_size["CDB Size"] = pd.to_numeric(df_size["CDB Size"]) // (1024)


# Add the 'Group' column based on the 'Round' column and groupsize value
df['Group'] = (df['Round'] - 1) // groupsize + 1
df_size['Group'] = (df_size['Round'] - 1) // groupsize + 1

# Display the DataFrame
print("\n")
print(df)
print("\n")
print(df_size)

# Compute mean, min, and max of Duration for each group
df_stats = df.groupby(["Group", "TransactionGroup"])["Duration"].agg(["mean", "min", "max"]).reset_index()
df_stats_ntx = df.groupby(["Group", "TransactionGroup"])["NumberTXs"].agg(["mean", "min", "max"]).reset_index()

# Compute mean, min, and max size for each group
df_size_stats = df_size.groupby("Group")["BC Size"].min().reset_index()
df_size_stats_cdb = df_size.groupby("Group")["CDB Size"].min().reset_index()


# Display the DataFrame with statistics
print("\n\nDataFrame with Statistics:")
print(df_stats)
print("\n\nDataFrame with NTX Statistics:")
print(df_stats_ntx)
print("\n\nDataFrame with BC Size Statistics:")
print(df_size_stats)
print("\n\nDataFrame with CDBSize Statistics:")
print(df_size_stats_cdb)


# Plot the data
plt.figure(figsize=(12, 6))

# for transaction_type in df_stats["TransactionGroup"].unique():
for transaction_type in ['RebCr', 'RebTrOw', 'StCr', 'TinCr', 'TinTrOw']:
    so_transaction_type = spellout_transaction_type(transaction_type)
    df_filtered = df_stats[df_stats["TransactionGroup"] == transaction_type]
    plt.plot(df_filtered["Group"], df_filtered["mean"], label=f"{so_transaction_type} Mean", marker='.')

plt.xlabel(f"Interval, each interval represents {groupsize} rounds")
plt.ylabel("Duration (s)")
plt.title("Sizes and Duration per Interval and TransactionType")
plt.legend(loc='upper left')
plt.grid(True)

plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))

# Plot blockchain size on a secondary y-axis
ax2 = plt.gca().twinx()
ax2.plot(df_size_stats["Group"], df_size_stats["BC Size"], label="Blockchain Size", color='b', marker='.')
ax2.plot(df_size_stats_cdb["Group"], df_size_stats_cdb["CDB Size"], label="CouchDB Size", color='r', marker='.')
ax2.set_ylabel("Size (MB)")
ax2.legend(loc='upper right', bbox_to_anchor=(0.85, 1.00))

#plt.show()
plt.savefig('plot_mean.pdf')
