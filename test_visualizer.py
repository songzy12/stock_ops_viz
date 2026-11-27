import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from visualizer import plot_from_csv


class InteractiveChartTests(unittest.TestCase):
    def test_chart_preserves_prices_and_nearest_operation_date(self):
        with tempfile.TemporaryDirectory() as directory:
            csv_path = os.path.join(directory, "TEST_data.csv")
            pd.DataFrame({
                "Date": ["2023-01-13", "2023-01-06", "2022-07-15", "2014-01-13"],
                "Close": [120, 100, 2000, 1000],
            }).to_csv(csv_path, index=False)

            with patch("plotly.graph_objects.Figure.write_html", autospec=True) as write_html:
                plot_from_csv(
                    csv_path, ["2023-01-08", "2022-07-15", "2025-01-01"],
                    "2023-01-01", directory
                )

            figure, html_path = write_html.call_args.args
            self.assertEqual(list(figure.data[0].y), [120, 100, 100, 50])
            self.assertEqual(figure.data[1].x[0], pd.Timestamp("2023-01-06"))
            self.assertEqual(figure.data[1].hoverinfo, "skip")
            self.assertEqual(figure.data[1].marker.size, 4)
            self.assertEqual(figure.data[1].marker.color, "lightcoral")
            self.assertEqual(figure.data[1].x[1], pd.Timestamp("2022-07-15"))
            self.assertEqual(len(figure.data[1].x), 2)
            self.assertEqual(html_path, os.path.join(directory, "TEST_data_chart.html"))
            self.assertTrue(write_html.call_args.kwargs["include_plotlyjs"])
            self.assertEqual(
                write_html.call_args.kwargs["post_script"],
                (Path(__file__).resolve().parent / "assets" / "chart_interactions.js")
                .read_text(encoding="utf-8"),
            )
            self.assertTrue(os.path.isfile(os.path.join(directory, "TEST_data_chart_2023-01-01.jpg")))
            buttons = figure.layout.xaxis.rangeselector.buttons
            self.assertEqual(
                [button.label for button in buttons],
                ["10 years", "7 years", "4 years", "3 years", "1 year"]
            )
            self.assertEqual([button.count for button in buttons], [10, 7, 4, 3, 1])
            self.assertTrue(all(button.step == "year" for button in buttons))
            self.assertEqual(figure.layout.xaxis.autorangeoptions.clipmin, pd.Timestamp("2014-01-13"))
            self.assertEqual(figure.layout.xaxis.autorangeoptions.clipmax, pd.Timestamp("2023-01-13"))
            self.assertEqual(
                list(figure.layout.xaxis.range),
                [pd.Timestamp("2015-01-13"), pd.Timestamp("2023-01-13")]
            )
            self.assertTrue(figure.layout.xaxis.showspikes)
            self.assertEqual(figure.layout.xaxis.spikemode, "across")
            self.assertEqual(figure.layout.xaxis.spikesnap, "cursor")
            self.assertEqual(figure.layout.xaxis.spikedash, "dot")
            self.assertEqual(figure.layout.xaxis.spikethickness, 1)

    def test_html_is_generated_when_no_data_matches_jpg_start(self):
        with tempfile.TemporaryDirectory() as directory:
            csv_path = os.path.join(directory, "TEST_data.csv")
            pd.DataFrame({"Date": ["2023-01-13"], "Close": [120]}).to_csv(
                csv_path, index=False
            )
            with patch("plotly.graph_objects.Figure.write_html", autospec=True) as write_html:
                plot_from_csv(csv_path, start_date="2025-01-01", output_dir=directory)

            self.assertEqual(list(write_html.call_args.args[0].data[0].y), [120])
            self.assertIsNone(write_html.call_args.args[0].layout.xaxis.range)
            self.assertFalse(os.path.exists(os.path.join(directory, "TEST_data_chart_2025-01-01.jpg")))

    def test_chart_without_operations_has_only_price_trace(self):
        with tempfile.TemporaryDirectory() as directory:
            csv_path = os.path.join(directory, "TEST_data.csv")
            pd.DataFrame({"Date": ["2023-01-13", "2022-01-13"], "Close": [120, 100]}).to_csv(
                csv_path, index=False
            )
            with patch("plotly.graph_objects.Figure.write_html", autospec=True) as write_html:
                plot_from_csv(csv_path, start_date="2023-01-01", output_dir=directory)

            figure = write_html.call_args.args[0]
            self.assertEqual(len(figure.data), 1)
            self.assertEqual(
                list(figure.layout.xaxis.range),
                [pd.Timestamp("2022-01-13"), pd.Timestamp("2023-01-13")]
            )


if __name__ == "__main__":
    unittest.main()
