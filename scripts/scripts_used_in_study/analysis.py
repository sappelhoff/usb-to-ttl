"""Analyze data for "In COM We Trust: Feasibility of USB-Based Event Marking".

Expects the following data files in a /data directory nested in the
working directory
(available from https://doi.org/10.5281/zenodo.3838622):

- NLS-lin-leo.txt.gz
- NLS-lin-ljr.txt.gz
- NLS-lin-lu3.txt.gz
- NLS-lin-par.txt.gz
- NLS-lin-t32.txt.gz
- NLS-lin-tlc.txt.gz
- NLS-lin-uno.txt.gz
- NLS-win-leo.txt.gz
- NLS-win-ljr.txt.gz
- NLS-win-lu3.txt.gz
- NLS-win-par.txt.gz
- NLS-win-t32.txt.gz
- NLS-win-tlc.txt.gz
- NLS-win-uno.txt.gz

Will produce the following outputs in a new directory "analysis_outputs":

- figure2_raincloud.png
- figure2_raincloud.pdf

Python requirements:

- Python >= 3.6
- numpy >= 1.15
- pandas >= 0.24
- matplotlib >= 3.0.2
- seaborn == 0.10.1
- ptitprince == 0.2.4

It is recommended to run this script in an isolated environment,
for example by using conda (https://docs.conda.io/en/latest/miniconda.html).
After making conda available on your command line, run the following
commands to create a suitable environment for running `analysis.py`:

- conda create -n usb_to_ttl Python=3.8 numpy pandas matplotlib --yes
- conda activate usb_to_ttl
- pip install seaborn==0.10.1 ptitprince==0.2.4

And then run:

- python analysis.py

"""
# %%  Imports
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ptitprince
import seaborn as sns

# %% Function to read latency data


def read_data(fnames):
    """Read latency data.

    Parameters
    ----------
    fnames : list of str
        The files to read in.

    Returns
    -------
    df : pandas.DataFrame
        All files concatenated as a data frame.

    """
    dfs = []
    for fname in fnames:

        # Read labstreamer file, skipping header
        df = pd.read_csv(fname, sep="\t", skiprows=13, na_values="NAN")

        # Drop all rows where latency_ms was not measured
        df = df[~df["latency_ms"].isna()]

        # Add more information
        opsys = fname.split("-")[1]
        device = fname.split("-")[2][:3]
        df["device"] = df["channel"].map({"Analog 0": "kbd", "Analog 2": device})
        df["os"] = opsys
        df["meas"] = f"{opsys}-{device}"

        # Drop the event column because it's meaningless in this circumstance
        df = df.drop(columns="event")

        # Each group of unique time_s measurements gets an index
        # Example: all rows where time_s is 5.4 have as entry under
        # 'index' 10
        _, _, idx = np.unique(df["time_s"], return_index=True, return_inverse=True)
        df["idx"] = idx
        df = df.sort_values(by="idx")

        dfs.append(df)

    # Concatenate all data frames and reset the pandas index
    df = pd.concat(dfs, join="inner")
    df = df.reset_index(drop=True)

    # Map abbreviations to full names
    if set(["lin", "win"]) == set(df["os"].unique()):
        df["os"] = df["os"].map({"lin": "Linux", "win": "Windows"})

    if set(["kbd", "par", "leo", "uno", "t32", "tlc", "lu3", "ljr"]) == set(
        df["device"].unique()
    ):
        df["device"] = df["device"].map(
            {
                "kbd": "Teensy 3.2 Keyboard",
                "par": "Parallel Port",
                "leo": "Arduino Leonardo",
                "uno": "Arduino Uno",
                "t32": "Teensy 3.2",
                "tlc": "Teensy LC",
                "ljr": "LabJack U3 (writeRegister)",
                "lu3": "LabJack U3 (setFIOState)",
            }
        )

    return df


# %% Function to preprocess data


def preprocess_data(df, max_uncertainty, n_first_measurements):
    """Preprocess the data.

    Parameters
    ----------
    df : pandas.DataFrame
        The data to be preprocessed.
    max_uncertainty : float
        Maximum acceptable network uncertainty in milliseconds.
        All rows in `df` with higher uncertainty will be dropped.
    n_first_measurements : int
        The number of first valid measurements to select.

    Returns
    -------
    df : pandas.DataFrame
        The preprocessed input data, changed inplace.

    """
    # Drop rows where network uncertainty is too high
    #
    # When the LabStreamer detects a TTL trigger at timepoint tTTL,
    # it calculates the delay between the last LSL trigger based on the timestamp tLSL
    # (reported by the stimulus PC) and converts this timestamp to its own
    # clock by subtracting the estimated clock offset Δt.
    # The TTL latency is then calculated as tTTL-(tLSL-Δt).
    # Measurement errors of the estimated clock offset are therefore reflected
    # in the calculated trigger latency,
    # but are not indicative of errors in the trigger latency tTTL
    df = df[df["network_unc_ms"] <= max_uncertainty]

    # Drop rows where the latency is erroneously low
    #
    # The LabStreamer has a sampling rate of 10kHz and detects events as the
    # first sample above the threshold in the configured interval relative to
    # the LSL trigger.
    # Sometimes, the keyboard input received by the data collection script
    # was duplicated after ~2ms and the (still active; as the outputs are set
    # to high for 5ms) TTL trigger was attributed to the second event with a
    # latency of less then one sample (0.1ms @ 10kHz).
    df = df[~((df["latency_ms"] < 0.1) & (df["device"] != "Teensy 3.2 Keyboard"))]

    # Drop measurement indices that do not consist of two rows
    # (one for keyboard, and one for device)
    # equivalent to the following line:
    # df = df.groupby(["meas", "idx"]).filter(lambda x: x["latency_ms"].count() == 2)
    df_idx_count = pd.DataFrame(df.groupby("meas")["idx"].value_counts())
    df_idx_count = df_idx_count.rename({"idx": "idx_count"}, axis=1).reset_index()
    df = df.merge(df_idx_count, on=["meas", "idx"])
    df = df[df["idx_count"] == 2]
    df = df.drop(columns=["idx_count"])

    # Make a new continuous index based on clean data
    tmps = list()
    for meas in df["meas"].unique():
        tmps.append(
            (
                df[df["meas"] == meas]
                .groupby("idx")
                .last()
                .reset_index()
                .reset_index()[["meas", "idx", "index"]]
            )
        )

    tmp = pd.concat(tmps)
    tmp = tmp.rename(columns={"index": "i"})

    df = df.merge(tmp, on=["meas", "idx"], validate="many_to_one")

    # Select only the n_first_measurements
    df = df[df["i"] < n_first_measurements]

    # Sort and return
    df = df[["meas", "os", "device", "i", "latency_ms"]]
    df = df.sort_values(by=["os", "device", "i"])
    return df


# %% Define constants for the analysis

# Paths to the data files
FNAMES = [
    os.path.join("data", "NLS-win-leo.txt.gz"),
    os.path.join("data", "NLS-win-ljr.txt.gz"),
    os.path.join("data", "NLS-win-lu3.txt.gz"),
    os.path.join("data", "NLS-win-par.txt.gz"),
    os.path.join("data", "NLS-win-tlc.txt.gz"),
    os.path.join("data", "NLS-win-t32.txt.gz"),
    os.path.join("data", "NLS-win-uno.txt.gz"),
    os.path.join("data", "NLS-lin-leo.txt.gz"),
    os.path.join("data", "NLS-lin-ljr.txt.gz"),
    os.path.join("data", "NLS-lin-lu3.txt.gz"),
    os.path.join("data", "NLS-lin-par.txt.gz"),
    os.path.join("data", "NLS-lin-tlc.txt.gz"),
    os.path.join("data", "NLS-lin-t32.txt.gz"),
    os.path.join("data", "NLS-lin-uno.txt.gz"),
]

# Parameters for `preprocess_data` (see docstring)
MAX_UNCERTAINTY = 0.01
N_FIRST_MEASUREMENTS = 2500

# Settings for plotting
LETTER_WIDTH_INCH = 8.5
sns.set_style("whitegrid")

# Create output directory for analysis
OUTDIR = "analysis_outputs"
os.makedirs(OUTDIR, exist_ok=True)

# %% Read the data

df = read_data(FNAMES)

# Contingency table of measurements
table_recorded = pd.crosstab(
    index=pd.Categorical(df["os"], categories=sorted(df["os"].unique())),
    columns=pd.Categorical(df["device"], categories=sorted(df["device"].unique())),
    dropna=False,
)

# Drop keyboard, because it is measured for each device, ...
# and thus contains all other columns
table_recorded.index.name = "os"
table_recorded.columns.name = "device"
table_recorded.drop(columns=["Teensy 3.2 Keyboard"], inplace=True)

min_measurements = np.min(table_recorded.min())
max_measurements = np.max(table_recorded.max())

print(f"Min and max number of measurements: {min_measurements}, {max_measurements}")

print("\nTable of recorded measurements:")
try:
    display(table_recorded.head())
except NameError:
    print(table_recorded.head())

# Contingency table of dropped measurements
dropped = df[df["network_unc_ms"] > MAX_UNCERTAINTY]

table_dropped = pd.crosstab(
    index=pd.Categorical(dropped["os"], categories=sorted(df["os"].unique())),
    columns=pd.Categorical(dropped["device"], categories=sorted(df["device"].unique())),
    dropna=False,
)

# Again, drop keyboard because it is measured for each device, ...
#  and thus contains all other columns
table_dropped.index.name = "os"
table_dropped.columns.name = "device"
table_dropped.drop(columns=["Teensy 3.2 Keyboard"], inplace=True)

print(f"\nTable of dropped measurements (uncertainty > {MAX_UNCERTAINTY}):")
try:
    display(table_dropped.head())
except NameError:
    print(table_dropped.head())

# %% Preprocess data

df = preprocess_data(df, MAX_UNCERTAINTY, N_FIRST_MEASUREMENTS)

# %% Produce data summary table


def iqr(x):
    """Calculate interquartile range."""
    return np.subtract(*np.percentile(x, [75, 25]))


table = (
    df.groupby(["device", "os"])
    .agg(
        {
            "latency_ms": [np.mean, np.std, np.median, iqr],
        }
    )
    .reset_index()
)


# %% Map multiindex of table to single index
if isinstance(table.columns, pd.core.indexes.multi.MultiIndex):
    cols = []
    for col in table.columns:
        if len(col[-1]) > 0:
            cols.append("-".join(col))
        else:
            cols.append(col[0])

    cols = [s.replace("_", "-") for s in cols]
    table.columns = cols


# %% Show full table
# For convenience, do this in Ipython, which allows copying the table
# to then paste it into Google Sheets and importing it from there into
# Google Docs.
# As a final step, the imported table can be formatted in APA style,
# see this video for help: https://www.youtube.com/watch?v=f7WomKsmeuI
copy = table.copy()
copy = copy[
    [
        "os",
        "device",
        "latency-ms-mean",
        "latency-ms-std",
        "latency-ms-median",
        "latency-ms-iqr",
    ]
]
copy.columns = ["Operating System", "Device", "Mean", "SD", "Median", "IQR"]

# Round, drop unneeded columns from copy and sort
copy = copy.round(3)
copy = copy[["Operating System", "Device", "Mean", "SD", "Median", "IQR"]]
copy = copy.sort_values(by=["Operating System", "Mean"])

try:
    display(copy.style.hide_index())
except NameError:
    print("'display' function only available in Ipython ... falling back to printing.")
    print(table.round(3).to_string(index=False, justify="center"))


# %% Settings for plotting

# Remove keyboard, we are not plotting it, and not using it for summary stats
df = df[df["device"] != "Teensy 3.2 Keyboard"]
print("\nDropped 'Teensy 3.2 Keyboard' from data.")

# Set plotting order
order = table.groupby("device").min().sort_values("latency-ms-mean").index.to_list()
order.remove("Teensy 3.2 Keyboard")
print(f"\nplotting in order: {order}")

# y-axis label settings
ylabel_map = dict(zip(order, ["\n".join(device.split(" ")) for device in order]))
ylabels = [ylabel_map[i] for i in order]


# %% Plot

with sns.plotting_context("paper", font_scale=1.3):
    fig, ax = plt.subplots(figsize=(LETTER_WIDTH_INCH, 5))

    palette = "colorblind"

    ptitprince.half_violinplot(
        x="device",
        order=order,
        y="latency_ms",
        hue="os",
        hue_order=["Linux", "Windows"],
        data=df,
        ax=ax,
        palette=palette,
        split=True,
        inner=None,
        offset=0.3,
    )

    for i in ax.collections:
        i.set_alpha(0.65)

    sns.stripplot(
        x="device",
        order=order,
        y="latency_ms",
        hue="os",
        hue_order=["Linux", "Windows"],
        data=df,
        ax=ax,
        palette=palette,
        alpha=0.1,
        size=1,
        zorder=0,
        jitter=1,
        dodge=True,
        edgecolor=None,
    )

    sns.boxplot(
        x="device",
        order=order,
        y="latency_ms",
        hue="os",
        hue_order=["Linux", "Windows"],
        data=df,
        ax=ax,
        palette=palette,
        color=palette,
        width=0.15,
        zorder=10,
        dodge=True,
        showcaps=True,
        boxprops={"zorder": 10},
        showfliers=True,
        whiskerprops={"linewidth": 2, "zorder": 10},
        saturation=0.75,
    )

    xlim = ax.get_xlim()
    ax.set_xlim((xlim[0] + xlim[0] * 0.5, xlim[1]))

    ax.set_xticklabels(ylabels)
    ax.set_xlabel("Device", labelpad=25)

    # Limit the extent of the y axis, which makes data non-visible, ...
    # so add a big outlier marker (red star) for that to mention in the caption
    upper_ylim = 2.1
    ax.set_ylim((0.0, upper_ylim))
    text_pos = 0.5
    outlier_text_obj = ax.text(
        x=text_pos,
        y=1.0,
        s="*",
        color="red",
        transform=ax.transAxes,
        ha="center",
        fontsize=20,
    )

    # Sanity check we did not cut any other outliers
    outliers = df[df["latency_ms"] >= upper_ylim].reset_index(drop=True)
    assert outliers["meas"].nunique() == 1

    # Sanity check we make the star in the correct position (in the middle)
    assert len(order) == 7
    assert order[3] == "LabJack U3 (writeRegister)"
    assert text_pos == 0.5

    # Print short report
    print(
        f"{outliers.shape[0]} outliers not shown for {outliers['meas'][0]}. "
        f"Ranging from {outliers['latency_ms'].min().round(1)} to "
        f"{outliers['latency_ms'].max().round(1)} ms "
        f"(mean: {outliers['latency_ms'].mean().round(1)} ms)"
    )

    ax.set_ylabel("Latency (ms)")
    ax.grid(b=True, which="major", axis="y")

    # Get the handles and labels. For this example it'll be 2 tuples
    # of length 4 each.
    handles, labels = ax.get_legend_handles_labels()

    # When creating the legend, only use the first two elements
    # to effectively remove the last two.
    lh = plt.legend(handles[0:2], labels[0:2], loc="upper left")
    lh.set_title("Operating System")

    sns.despine()

    for ext in ["png", "pdf"]:
        fname = f"figure2_raincloud.{ext}"
        fname = os.path.join(OUTDIR, fname)
        fig.tight_layout()
        dpi = 600 if ext == "png" else None
        plt.savefig(fname, dpi=dpi, bbox_extra_artists=(outlier_text_obj,))

# %% Calculate summary statistics between OS

# Drop the LabJack U3 from this comparison, as it's an outlier
df = df[~df["device"].str.startswith("LabJack")]

# Guarantee that Linux is listed before Windows, to later have the appropriate diff
df = df.sort_values(by=["os", "device", "i"])

df_os = pd.pivot_table(
    df, values="latency_ms", index="os", aggfunc=[np.mean, np.std, np.median, iqr]
)
df_os.loc["Windows - Linux", :] = np.diff(df_os.to_numpy(), axis=0)

try:
    display(df_os.round(3))
except NameError:
    print(df_os.round(3))

# %% Where is the OS effect strongest?

# exclude LabJack U3 as an outlier
# exclude parallel port, gets mentioned in the text anyhow
print("Effect of OS (Windows - Linux) on latency in ms\n")
print(
    table[
        ~table["device"].isin(
            [
                "Teensy 3.2 Keyboard",
                "Parallel Port",
                "LabJack U3 (writeRegister)",
                "LabJack U3 (setFIOState)",
            ]
        )
    ]
    .groupby("device")["latency-ms-mean"]
    .agg(np.diff)
    .sort_values()
)
