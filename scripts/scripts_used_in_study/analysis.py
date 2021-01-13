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
- anova_results.csv
- anova_pairwise_ttests_results.csv
- os_diff_results.txt
- summary_table.csv
- exclusion_criteria.txt

Python requirements:

- Python >= 3.6
- numpy >= 1.15
- pandas >= 0.24
- matplotlib >= 3.0.2
- seaborn == 0.10.1
- ptitprince == 0.2.4
- pingouin == 0.3.8

It is recommended to run this script in an isolated environment,
for example by using conda (https://docs.conda.io/en/latest/miniconda.html).
After making conda available on your command line, run the following
commands to create a suitable environment for running `analysis.py`:

- conda create -n usb_to_ttl Python=3.8 numpy pandas matplotlib --yes
- conda activate usb_to_ttl
- pip install seaborn==0.10.1 pingouin==0.3.8 ptitprince==0.2.4

And then run:

- python analysis.py

"""
# %%  Imports
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pingouin
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

        # add more information
        opsys = fname.split("-")[1]
        device = fname.split("-")[2][:3]
        df["channel"] = df["channel"].map({"Analog 0": "kbd", "Analog 2": device})
        df["os"] = opsys
        df["meas"] = "{}-{}".format(opsys, device)
        df["drop"] = False

        # drop the event column because it's meaningless in this circumstance
        df = df.drop(columns="event")

        # Each group of unique time_s measurements gets an index
        # Example: all rows where time_s is 5.4 have as entry under
        # 'index' 10
        _, _, idx = np.unique(df["time_s"], return_index=True, return_inverse=True)
        df["idx"] = idx
        df = df.sort_values(by="idx")

        dfs.append(df)

    # concatenate all data frames and reset the pandas index
    df = pd.concat(dfs, join="inner")
    df = df.reset_index(drop=True)

    return df


# %% Function to preprocess data


def preprocess_data(df, max_uncertainty, min_latency, n_first_measurements):
    """Preprocess the data.

    Parameters
    ----------
    df : pandas.DataFrame
        The data to be preprocessed.
    max_uncertainty : float
        Maximum acceptable network uncertainty in milliseconds.
        All rows in `df` with higher uncertainty will be dropped.
    min_latency : float
        Minimum acceptable latency in milliseconds for all channels
        except the keyboard. Rows that are not corresponding
        to the keyboard channel and have a lower latency are marked
        as erroneous and dropped.
    n_first_measurements : int


    Returns
    -------
    df : pandas.DataFrame
        The preprocessed input data, changed inplace.

    """
    # drop rows where network uncertainty is too high
    df = df[df["network_unc_ms"] <= max_uncertainty]

    # drop rows where the latency is erroneously low
    df = df[~((df["latency_ms"] < min_latency) & (df["channel"] != "kbd"))]

    # drop measurement indices that do not consist of two rows
    # (one for keyboard, and one for device)
    df = df.groupby(["meas", "idx"]).filter(lambda x: x["latency_ms"].count() == 2)

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

    # select only the n_first_measurements
    df = df[df["i"] < n_first_measurements]

    # save exclusion criteria
    fname = "exclusion_criteria.txt"
    fname = os.path.join(OUTDIR, fname)
    with open(fname, "w") as fout:
        print(
            f"MAX_UNCERTAINTY: {max_uncertainty}\n"
            f"MIN_LATENCY: {min_latency}\n"
            f"N_FIRST_MEASUREMENTS: {n_first_measurements}",
            file=fout,
        )

    # sort and return
    df = df[["meas", "os", "channel", "i", "latency_ms"]]
    df = df.sort_values(by=["os", "channel", "i"])
    return df


# %% Define constants for the analysis

# paths to the data files
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

# parameters for `preprocess_data` (see docstring)
MAX_UNCERTAINTY = 0.01
MIN_LATENCY = 0.1
N_FIRST_MEASUREMENTS = 2500

# for plotting
LETTER_WIDTH_INCH = 8.5
sns.set_style("whitegrid")

# create output directory for analysis
OUTDIR = "analysis_outputs"
os.makedirs(OUTDIR, exist_ok=True)

# %% Read and preprocess the data

df = read_data(FNAMES)

# Number of measurements per MCU & operating system
# excluding the keyboard and parallel port
min_measurements, max_measurements = (
    df.groupby(["channel", "os"])
    .count()
    .drop(["kbd"])["time_s"]
    .describe()[["min", "max"]]
    .to_numpy()
    .astype(int)
)

print(f"Min and max number of measurements: {min_measurements}, {max_measurements}")

# %%
df = preprocess_data(df, MAX_UNCERTAINTY, MIN_LATENCY, N_FIRST_MEASUREMENTS)

try:
    display(df.head())
except NameError:
    print(df.head())


# %% Produce data summary table

# Map abbreviations to full names
if set(["lin", "win"]) == set(df["os"].unique()):
    df["os"] = df["os"].map({"lin": "Linux", "win": "Windows"})

if set(["kbd", "par", "leo", "uno", "t32", "tlc", "lu3", "ljr"]) == set(
    df["channel"].unique()
):
    df["channel"] = df["channel"].map(
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


def iqr(x):
    """Calculate interquartile range."""
    return np.subtract(*np.percentile(x, [75, 25]))


table = (
    df.groupby(["channel", "os"])
    .agg(
        {
            "latency_ms": [np.mean, np.std, np.median, iqr],
        }
    )
    .reset_index()
)

try:
    display(table)
except NameError:
    print(table)


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
        "channel",
        "latency-ms-mean",
        "latency-ms-std",
        "latency-ms-median",
        "latency-ms-iqr",
    ]
]
copy.columns = ["Operating System", "Device", "Mean", "Std", "Median", "IQR"]

# Make combined mean+-std column
copy = copy.round(3)
combined_mean_std_col = [
    f"{mean} ± {str(std).ljust(5, '0')}"
    for mean, std in zip(copy["Mean"].to_list(), copy["Std"].to_list())
]
copy["Mean ± Std"] = combined_mean_std_col

# Drop unneeded columns from copy and sort
copy = copy[["Operating System", "Device", "Mean ± Std", "Median", "IQR"]]
copy = copy.sort_values(by=["Operating System", "Device"])

try:
    display(copy.style.hide_index())
except NameError:
    print("'display' function only available in Ipython ... falling back to printing.")
    print(table.round(3).to_string(index=False, justify="center"))


fname = "summary_table.csv"
fname = os.path.join(OUTDIR, fname)
table.round(3).to_csv(fname, index=False)

# %% Settings for plotting

# Set plotting order
order = table.groupby("channel").min().sort_values("latency-ms-mean").index.to_list()
print(f"plotting in order: {order}")

# Remove keyboard, we are not plotting it, and not entering it into the ANOVA
order.remove("Teensy 3.2 Keyboard")
df = df[df["channel"] != "Teensy 3.2 Keyboard"]

# y-axis label settings
ylabel_map = dict(zip(order, ["\n".join(device.split(" ")) for device in order]))
ylabels = [ylabel_map[i] for i in order]


# %% Plot

with sns.plotting_context("paper", font_scale=1.3):
    fig, ax = plt.subplots(figsize=(LETTER_WIDTH_INCH, 5))

    palette = "colorblind"

    ptitprince.half_violinplot(
        x="channel",
        y="latency_ms",
        hue="os",
        data=df,
        ax=ax,
        palette=palette,
        split=True,
        inner=None,
        order=order,
        offset=0.3,
    )

    for i in ax.collections:
        i.set_alpha(0.65)

    sns.stripplot(
        x="channel",
        y="latency_ms",
        hue="os",
        data=df,
        ax=ax,
        palette=palette,
        alpha=0.1,
        size=1,
        order=order,
        zorder=0,
        jitter=1,
        dodge=True,
        edgecolor=None,
    )

    sns.boxplot(
        x="channel",
        y="latency_ms",
        hue="os",
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
        order=order,
    )

    xlim = ax.get_xlim()
    ax.set_xlim((xlim[0] + xlim[0] * 0.5, xlim[1]))

    ax.set_xticklabels(ylabels)
    ax.set_xlabel("Device", labelpad=25)

    # Use log scale
    ax.set_yscale("log", base=10)
    yticks = [0.1, 0.25, 0.5, 1, 2.5, 5, 10]
    ax.set_yticks(yticks)
    ax.set_yticklabels([f"{i:2.2f} ms" for i in yticks])

    ax.set_ylim((0.1, None))
    ax.set_ylabel("Latency (log10 scale)")

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
        dpi = 1200 if ext == "png" else None
        plt.savefig(fname, dpi=dpi)

# %% Run ANOVA

# latency_ms ~ os*channel
model = pingouin.anova(
    data=df,
    dv="latency_ms",
    between=["os", "channel"],
    ss_type=2,
    detailed=True,
)

# for p-unc values of 0.0 it means that
# # scipy.stats.f(df, df_resid).sf(f_val) returned 0,
# which means that the p-value is very low indeed <<< 0.0001
for col in ["p-unc"]:
    model[col] = [
        str(i).replace("0.0", "<0.0001") if i == 0.0 else i
        for i in model[col].to_list()
    ]

try:
    display(model)
except NameError:
    print(model)

# Save ANOVA results
fname = "anova_results.csv"
fname = os.path.join(OUTDIR, fname)
model.to_csv(fname, index=False)


# %% Print time difference between operating systems in milliseconds
first = "Windows"
second = "Linux"
os_diff = (
    df.groupby("os")["latency_ms"].mean()[first]
    - df.groupby("os")["latency_ms"].mean()[second]
)
print(np.round(os_diff, 3))

ttest_results = pingouin.ttest(
    df[df["os"] == first]["latency_ms"],
    df[df["os"] == second]["latency_ms"],
    paired=True,
)

try:
    display(ttest_results)
except NameError:
    print(ttest_results)


fname = "os_diff_results.txt"
fname = os.path.join(OUTDIR, fname)
with open(fname, "w") as fout:
    print(f"Difference between operating systems: {os_diff:.3f}ms", file=fout)
    print(f"({first} minus {second})", file=fout)
    print(ttest_results.to_string(), file=fout)


# %% Perform pairwise comparisons between the channels and operating systems
stats = pingouin.pairwise_ttests(
    data=df, dv="latency_ms", between=["os", "channel"], padjust="bonf"
)

# again, p of 0 means p < 0.0001 (see above)
for col in ["p-unc", "p-corr"]:
    stats[col] = [
        str(i).replace("0.0", "<0.0001") if i == 0.0 else i
        for i in stats[col].to_list()
    ]

try:
    display(stats)
except NameError:
    print(stats)

# Save pairwise results
fname = "anova_pairwise_ttests_results.csv"
fname = os.path.join(OUTDIR, fname)
stats.to_csv(fname, index=False)

# %%
