import re
import pandas as pd
import matplotlib.pyplot as plt
import os


groupsize = 1000


# Set the directory containing your files
folder_path = 'DataTest'
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

# sizes
# Compile a regex pattern to match filenames like 'log-0', 'log-1', etc.
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
size_pattern = r"Round (\d+) complete.  D=(\d+\.\d+)s"

# Find all matches in the log data
matches = re.findall(pattern, log_data)
size_matches = re.findall(size_pattern, log_data_s, re.DOTALL)

# Create a DataFrame from the matches
df = pd.DataFrame(matches, columns=["Round", "TransactionType", "NumberTXs", "Duration"])
df_size = pd.DataFrame(size_matches, columns=["Round", "Round Time"])

print("\n")
print(df)
print("\n")
print(df_size)



# Apply the function to create a new column 'TransactionGroup'
df['TransactionGroup'] = df['TransactionType']


# Convert Round column to numeric for correct sorting
df["Round"] = pd.to_numeric(df["Round"])
df_size["Round"] = pd.to_numeric(df_size["Round"])

# Convert to numeric
df["Duration"] = pd.to_numeric(df["Duration"])
df["NumberTXs"] = pd.to_numeric(df["NumberTXs"])
df_size["Round Time"] = pd.to_numeric(df_size["Round Time"])

# Compute sum of ntxs per round
df_ntx_sum = df.groupby(["Round"])["NumberTXs"].sum().reset_index()

# Compute tps per round
df_tps = pd.merge(df_size, df_ntx_sum, on="Round")
df_tps["TPS"] = df_tps["NumberTXs"] / df_tps["Round Time"]

# Add the 'Group' column based on the 'Round' column and groupsize value
df['Group'] = (df['Round'] - 1) // groupsize + 1
df_size['Group'] = (df_size['Round'] - 1) // groupsize + 1
df_ntx_sum['Group'] = (df_ntx_sum['Round'] - 1) // groupsize + 1
df_tps['Group'] = (df_tps['Round'] - 1) // groupsize + 1

# Display the DataFrame
print("\n")
print(df)
print("\n")
print(df_size)
print("\n")
print(df_ntx_sum)
print("\n")
print(df_tps)

# Compute mean, min, and max of Duration for each group
df_stats = df_size.groupby(["Group"])["Round Time"].agg(["mean", "min", "max"]).reset_index()
df_stats_ntx = df_ntx_sum.groupby(["Group"])["NumberTXs"].agg(["mean", "min", "max"]).reset_index()
df_stats_tps = df_tps.groupby(["Group"])["TPS"].agg(["mean", "min", "max"]).reset_index()

# Display the DataFrame with statistics
print("\n\nDataFrame with Round Time Statistics:")
print(df_stats)
print("\n\nDataFrame with NTX Statistics:")
print(df_stats_ntx)
print("\n\nDataFrame with TPS Statistics:")
print(df_stats_tps)



# Plot the data
fig, ax2 = plt.subplots(figsize=(12, 6))


plt.title("TPS per Interval ")
plt.xlabel(f"Interval, each interval represents {groupsize} rounds")
plt.grid(True)



plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))


ax2.plot(df_stats_tps["Group"], df_stats_tps["mean"], label=f"TPS Mean", marker='.')
ax2.plot(df_stats_tps["Group"], df_stats_tps["min"], label=f"TPS Min", marker='.')
ax2.plot(df_stats_tps["Group"], df_stats_tps["max"], label=f"TPS Max", marker='.')

ax2.set_ylabel("TPS")
ax2.legend(loc='upper left')

# Make space at top

ymin, ymax = ax2.get_ylim()
ax2.set_ylim(bottom=ymin, top=ymax + (ymax - ymin) * 0.15)

#plt.show()
plt.savefig('plot_tps.pdf')
