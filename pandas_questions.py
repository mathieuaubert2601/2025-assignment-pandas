"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum.
In some way, we would like to depict results with something similar to the
maps that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_renamed = regions.rename(
        columns={"code": "code_reg", "name": "name_reg"}
    )
    departments_renamed = departments.rename(
        columns={
            "region_code": "code_reg",
            "code": "code_dep",
            "name": "name_dep",
        }
    )

    result = departments_renamed.merge(
        regions_renamed,
        on="code_reg",
        how="left",
    )

    result = result[["code_reg", "name_reg", "code_dep", "name_dep"]]

    return result


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.
    """
    referendum_filtered = referendum[
        ~referendum["Department code"]
        .astype(str)
        .str.contains("Z", na=False)
    ].copy()

    referendum_filtered["code_dep"] = (
        referendum_filtered["Department code"]
        .astype(str)
        .str.zfill(2)
    )

    result = referendum_filtered.merge(
        regions_and_departments,
        on="code_dep",
        how="left",
    )

    result = result.dropna()

    return result


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    Indexed by `code_reg` with columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null',
     'Choice A', 'Choice B']
    """
    result = (
        referendum_and_areas
        .groupby("code_reg")
        .agg(
            {
                "name_reg": "first",
                "Registered": "sum",
                "Abstentions": "sum",
                "Null": "sum",
                "Choice A": "sum",
                "Choice B": "sum",
            }
        )
        .reset_index()
        .set_index("code_reg")
    )

    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum."""
    gdf = gpd.read_file("data/regions.geojson")
    gdf = gdf.rename(columns={"code": "code_reg"})

    referendum_df = referendum_result_by_regions.reset_index()
    gdf = gdf.merge(referendum_df, on="code_reg", how="left")

    gdf["ratio"] = (
        gdf["Choice A"] / (gdf["Choice A"] + gdf["Choice B"])
    )

    gdf.plot(column="ratio", legend=True, cmap="RdYlGn")

    return gdf


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()

    regions_and_departments = merge_regions_and_departments(
        df_reg,
        df_dep,
    )

    referendum_and_areas = merge_referendum_and_areas(
        referendum,
        regions_and_departments,
    )

    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )

    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
