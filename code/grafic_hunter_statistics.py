#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.constants import (
    HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH
)
from utils.common_functions import (
    get_list_files_in_path
)


def plot_grafics_linear_aggregate(aggregation_df: pd.DataFrame, title: str):
    aggregation_df.sort_values(
        by=["moment_of_campaign", "validation"],
        inplace=True
    )

    moment_of_campaign_list = aggregation_df["moment_of_campaign"].unique()
    validation_list = aggregation_df["validation"].unique()

    line_colors_dict = dict(zip(
        validation_list,
        ["red", "green", "blue", "magenta"]
    ))

    figure = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=["Positives", "Negatives", "Indeterminates"])

    for validation in validation_list:
        figure.add_trace(go.Scatter(
            x=moment_of_campaign_list,
            y=aggregation_df[
                aggregation_df["validation"] == validation
            ]["country_positives"],
            line_color=line_colors_dict[validation],
            name=validation,
            legendgroup=validation
        ), row=1, col=1)

        figure.add_trace(go.Scatter(
            x=moment_of_campaign_list,
            y=aggregation_df[
                aggregation_df["validation"] == validation
            ]["country_negatives"],
            line_color=line_colors_dict[validation],
            name=validation,
            legendgroup=validation,
            showlegend=False
        ), row=1, col=2)

        figure.add_trace(go.Scatter(
            x=moment_of_campaign_list,
            y=aggregation_df[
                aggregation_df["validation"] == validation
                ]["country_indeterminates"],
            line_color=line_colors_dict[validation],
            name=validation,
            legendgroup=validation,
            showlegend=False
        ), row=2, col=1)

    figure.update_layout(title_text=title)
    figure.show()


def plot_grafics_bars_aggregate(aggregation_df: pd.DataFrame, title: str):
    aggregation_df.sort_values(
        by=["moment_of_campaign", "validation"],
        inplace=True
    )

    moment_of_campaign_list = aggregation_df["moment_of_campaign"].unique()
    validation_list = aggregation_df["validation"].unique()

    country_results_list = ["country_positives",
                            "country_indeterminates",
                            "country_negatives"]
    bars_colors_dict = dict(zip(
        country_results_list,
        ["green", "blue", "red"]
    ))

    figure = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=validation_list)

    for country_result in country_results_list:
        figure.add_trace(go.Bar(
            x=moment_of_campaign_list,
            y=aggregation_df[
                aggregation_df["validation"] == validation_list[0]
                ][country_result],
            name=country_result,
            legendgroup=country_result,
            marker_color=bars_colors_dict[country_result]
        ), row=1, col=1)

    for country_result in country_results_list:
        figure.add_trace(go.Bar(
            x=moment_of_campaign_list,
            y=aggregation_df[
                aggregation_df["validation"] == validation_list[1]
                ][country_result],
            name=country_result,
            legendgroup=country_result,
            showlegend=False,
            marker_color=bars_colors_dict[country_result]
        ), row=1, col=2)

    for country_result in country_results_list:
        figure.add_trace(go.Bar(
            x=moment_of_campaign_list,
            y=aggregation_df[
                 aggregation_df["validation"] == validation_list[2]
                ][country_result],
            name=country_result,
            legendgroup=country_result,
            showlegend=False,
            marker_color=bars_colors_dict[country_result]
        ), row=2, col=1)

    for country_result in country_results_list:
        figure.add_trace(go.Bar(
            x=moment_of_campaign_list,
            y=aggregation_df[
                 aggregation_df["validation"] == validation_list[3]
                 ][country_result],
            name=country_result,
            legendgroup=country_result,
            showlegend=False,
            marker_color=bars_colors_dict[country_result]
        ), row=2, col=2)

    figure.update_layout(title_text=title, barmode="stack")
    figure.show()


def plot_grafics_linear_by_country(country_code: str):
    aggregation_of_country_df = aggregate_one_country_hunter_statistics(
        country_code=country_code
    )
    plot_grafics_linear_aggregate(aggregation_of_country_df,
                                  title="Hunter results for {}".format(
                                      country_code))


def plot_grafics_bars_by_country(country_code: str):
    aggregation_of_country_df = aggregate_one_country_hunter_statistics(
        country_code=country_code
    )
    plot_grafics_bars_aggregate(aggregation_of_country_df,
                                title="Hunter results for {}".format(
                                    country_code))


def aggregate_one_country_hunter_statistics(country_code: str) -> pd.DataFrame:
    statistics_files = [filename for filename in
                        get_list_files_in_path(
                            HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH)
                        if "statistics" in filename]
    aggregation_df = pd.DataFrame(columns=[
        "validation",
        "country_positives", "country_negatives", "country_indeterminates",
        "moment_of_campaign"
    ])
    for statistic_file in statistics_files:
        statistic_df = pd.read_csv(
            HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH + statistic_file)

        campaign_moment_split_list = statistic_file.split("_")[-2:]
        campaign_hour = campaign_moment_split_list[1].split(".")[0]
        campaign_date = "{}_{}".format(
            campaign_moment_split_list[0],
            campaign_hour
        )

        same_country_cond = statistic_df["origin_country"] == country_code

        country_positives = len(
            statistic_df[
                (statistic_df['country_outcome'] == "Positive") &
                same_country_cond
            ]
        )
        country_negatives = len(
            statistic_df[
                (statistic_df['country_outcome'] == "Negative") &
                same_country_cond
            ]
        )
        country_indeterminates = len(
            statistic_df[
                (statistic_df['country_outcome'] == "Indeterminate") &
                same_country_cond
            ]
        )

        if "ip_target_validation" in statistic_file:
            validation_name = "ip_target_validation"
        elif "ip_all_validation" in statistic_file:
            validation_name = "ip_all_validation"
        elif "no_ip_validation" in statistic_file:
            validation_name = "no_ip_validation"
        elif "ip_last_hop_validation" in statistic_file:
            validation_name = "ip_last_hop_validation"
        else:
            validation_name = ""

        aggregation_df = pd.concat(
            [pd.DataFrame([[
                validation_name,
                country_positives,
                country_negatives,
                country_indeterminates,
                campaign_date
            ]], columns=aggregation_df.columns,
            ), aggregation_df],
            ignore_index=True
        )

    aggregation_df.sort_values(by=[
        "moment_of_campaign", "validation"],
        inplace=True)
    return aggregation_df


total_aggregation_df = pd.read_csv(
    HUNTER_MEASUREMENTS_CAMPAIGNS_STATISTICS_PATH +
    "aggregation_results.csv",
    sep=","
)

plot_grafics_bars_aggregate(total_aggregation_df,
                            title="Hunter results aggregated")
plot_grafics_bars_by_country(country_code="IT")
