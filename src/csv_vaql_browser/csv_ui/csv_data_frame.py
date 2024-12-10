from typing import Callable, override, Any, Self

import polars
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from polars import DataFrame

from csv_vaql_browser.panels.vaql_filter import VAQLFilterLineEdit, Op
from csv_vaql_browser.tools.err import err


class CSVDataFrameModel(QAbstractTableModel):
    def __init__(self, on_load: Callable[[str, Self], None], on_change: Callable[[Self], None]):
        super().__init__()
        self.csv = DataFrame()
        self.original_csv = self.csv
        self.on_load = on_load
        self.on_change = on_change
        self.apply_filter: Callable[[str], None] = self.filter_on_substring
        self.loaded_file_name: str | None = None

    def load_csv_file(self, file_name: str) -> Exception | None:
        try:
            csv = polars.read_csv(file_name)

            a = [polars.col(column_name).cast(polars.String) for column_name in csv.columns]
            print(a)
            self.csv = csv.with_columns(polars.concat_str(a, separator = " ", ignore_nulls = True).alias("full_text_search_column"))

            self.original_csv = self.csv.clone()
            self.on_load(file_name, self)
            self.loaded_file_name = file_name
            return None
        except Exception as ex:
            return ex

    def save_csv_file(self, file_name: str | None) -> Exception | None:
        target_file_name = self.loaded_file_name if file_name is None else file_name

        result = err(lambda: self.csv.write_csv(target_file_name))
        if result is not None:
            return result

        return self.load_csv_file(target_file_name)

    def enable_substring_filter(self):
        self.apply_filter = self.filter_on_substring

    def enable_sql_filter(self) -> None:
        self.apply_filter = self.filter_on_sql_expression

    def filter_on_substring(self, filter_text: str) -> None:
        is_case_insensitive_search = filter_text.lower() == filter_text
        expressions = [
            polars.col(column_name).cast(polars.String).str.contains_any(
                [filter_text], ascii_case_insensitive = is_case_insensitive_search
            )
            for column_name in self.original_csv.columns
        ]
        filter_expression = expressions[0]
        for expression in expressions[1:]:
            filter_expression = filter_expression | expression
        self.csv = self.original_csv.filter(filter_expression)
        self.on_change(self)

    def filter_on_vaql(self, all_filters: list[VAQLFilterLineEdit]):
        # print(f"filter_on_vaql {all_filters}")

        filter_text = all_filters[0].text()
        exp = None
        # TODO: Add code to handle case when filter_text == ""
        def get_exp_acc():
            if filter_text == "":
                return None
            else:
                return polars.col("full_text_search_column").str.contains_any(
                    [filter_text], ascii_case_insensitive = (filter_text.lower() == filter_text)
                )
        exp_acc = get_exp_acc()
        exp_head_negating = all_filters[0].negating

        if len(all_filters) > 1:
            for f in all_filters[1:]:
                filter_text = f.text()
                next_exp = polars.col("full_text_search_column").str.contains_any(
                    [filter_text], ascii_case_insensitive = (filter_text.lower() == filter_text)
                )
                if filter_text == "":
                    next_exp = None
                if f.op == Op.AND:
                    if exp_acc is not None:
                        if exp_head_negating:
                            exp_acc = exp_acc.not_()
                        if exp is None:
                            exp = exp_acc
                        else:
                            exp = exp & exp_acc

                    exp_acc = next_exp
                    exp_head_negating = f.negating
                    # exp = exp & next_exp
                else:
                    if next_exp is not None:
                        if exp_acc is None:
                            if exp_head_negating:
                                exp_acc = next_exp.not_()
                            else:
                                exp_acc = next_exp
                        else:
                            exp_acc = exp_acc | next_exp

        if exp_acc is not None:
            if exp is None:
                if exp_head_negating:
                    exp_acc = exp_acc.not_()
                exp = exp_acc
            else:
                if exp_head_negating:
                    exp_acc = exp_acc.not_()
                exp = exp & exp_acc

        print(exp)

        if exp is None:
            self.csv = self.original_csv.clone()
        else:
            self.csv = self.original_csv.filter(exp)
        self.on_change(self)

    def filter_on_sql_expression(self, sql_expression: str) -> None:
        try:
            self.csv = self.original_csv.sql(sql_expression)
            self.on_change(self)
        except:
            if not (self.csv is self.original_csv):
                self.csv = self.original_csv
                self.on_change(self)

    @override
    def headerData(self, section: int, orientation: Qt.Orientation, role = ...) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.csv.columns[section]
        else:
            return None

    @override
    def rowCount(self, parent = ...) -> int:
        return self.csv.shape[0]

    @override
    def columnCount(self, parent = ...) -> int:
        return self.csv.shape[1] - 1

    @override
    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            return f"{self.csv.item(index.row(), index.column())}"
        else:
            return None