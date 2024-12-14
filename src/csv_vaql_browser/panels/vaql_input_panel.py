from PySide6.QtCore import QMargins, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QLabel

from csv_vaql_browser.app_context import AppContext
from csv_vaql_browser.panels.vaql_filter import VAQLFilterLineEdit, Op
from csv_vaql_browser.tools.linked_list import Node
from csv_vaql_browser.tools.panel_widget import Panel


class VAQLInputPanel(Panel[QVBoxLayout]):
    def __init__(self, parent: QWidget, ctx: AppContext):
        super().__init__(QVBoxLayout())
        self.ctx = ctx
        self.layout().setContentsMargins(QMargins(1, 1, 1, 5))
        self.layout().setSpacing(0)
        self.setParent(parent)

        self.widgets = []
        self.w_to_remove_parents = []

        zero_margins = QMargins(0, 0, 0, 0)

        def clear_layout():
            for w in self.widgets:
                self.layout().removeWidget(w)

            self.w_to_remove_parents = [w for w in self.widgets]
            self.widgets.clear()

        def add_widget(widget: QWidget) -> None:
            self.layout().addWidget(widget)
            self.widgets.append(widget)

        def make_and_label(*, is_negating: bool, is_negating_only: bool) -> QLabel | None:
            if not is_negating and is_negating_only:
                return None
            else:
                and_label = QLabel()
                if is_negating and is_negating_only:
                    and_label.setText("NOT")
                elif is_negating:
                    and_label.setText("AND NOT")
                else:
                    and_label.setText("AND")
                and_label.setMargin(0)
                and_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                and_label.setStyleSheet("font-weight: bold;")
                return and_label

        def update_layout():
            clear_layout()
            layout = self.layout()

            # first node is an anchor and does not hold a widget; hence we pick .next
            filters_next: Node[VAQLFilterLineEdit] | None = self.filters.next
            value: VAQLFilterLineEdit | None = filters_next.value
            node = self.filters.next
            filter_requesting_focus = None
            panel: QWidget | None = None
            while node is not None:
                assert node is not None
                assert node.value is not None
                if node.value.op == Op.OR:
                    # add to the existing panel
                    or_layout: QHBoxLayout = panel.layout()
                    if or_layout.count() > 0:
                        # add or label
                        or_label = QLabel(" OR NOT ") if node.value.negating else QLabel(" OR ")
                        or_label.setMargin(0)
                        # or_label.setStyleSheet("font-weight: bold; background-color: black; color: white;")
                        or_label.setStyleSheet("font-weight: bold;")
                        or_layout.addWidget(or_label)

                        # def rm():
                        #     or_layout.removeWidget(or_label)
                        #     or_label.setParent(None)
                        # self.ws.append(rm)

                    or_layout.addWidget(node.value)
                    if not node.value.is_connected:
                        node.value.textChanged.connect(self.filters_changed)
                        node.value.is_connected = True

                    if node.value.request_focus:
                        node.value.request_focus = False
                        filter_requesting_focus = node.value

                else:  # op == Op.AND
                    if layout.count() == 0:
                        # if this is first element; we will add label if it is negating; note that fist
                        # element should allways be of type node.value.op == Op.AND
                        if node.value.negating:
                            label = make_and_label(is_negating = True, is_negating_only = True)
                            if label is not None:
                                add_widget(label)
                    else:
                        # we already have some widgets in layout
                        add_widget(make_and_label(is_negating = node.value.negating, is_negating_only = False))

                    panel = QWidget()
                    panel.setContentsMargins(zero_margins)
                    or_layout = QHBoxLayout()
                    or_layout.setContentsMargins(zero_margins)
                    panel.setLayout(or_layout)
                    or_layout.addWidget(node.value)

                    if not node.value.is_connected:
                        node.value.textChanged.connect(self.filters_changed)
                        node.value.is_connected = True

                    if node.value.request_focus:
                        node.value.request_focus = False
                        filter_requesting_focus = node.value
                    add_widget(panel)

                node = node.next

            for w in self.w_to_remove_parents:
                if w.parent() is not None:
                    w.setParent(None)
            self.w_to_remove_parents.clear()

            layout.update()
            if filter_requesting_focus is not None:
                filter_requesting_focus.setFocus()

            self.filters_changed()

        def foo():
            clear_layout()
            layout = self.layout()
            # layout.update()
            panel = QWidget()
            panel.setContentsMargins(QMargins(0, 0, 0, 0))
            or_layout = QHBoxLayout()
            or_layout.setContentsMargins(QMargins(0, 4, 0, 0))
            panel.setLayout(or_layout)
            node = self.filters
            filter_requesting_focus = node.value
            while node is not None:
                if node.value is not None:
                    if node.value.op == Op.OR:
                        if or_layout.count() > 0:
                            or_label = QLabel(" OR NOT ") if node.value.negating else QLabel(" OR ")
                            or_label.setMargin(0)
                            # or_label.setStyleSheet("font-weight: bold; background-color: black; color: white;")
                            or_label.setStyleSheet("font-weight: bold;")
                            or_layout.addWidget(or_label)
                        or_layout.addWidget(node.value)
                        if node.value.request_focus:
                            node.value.request_focus = False
                            filter_requesting_focus = node.value

                    else:  # Op.And
                        if panel.layout().count() > 0:
                            layout.addWidget(panel)
                            self.widgets.append(panel)
                            and_label = QLabel("AND NOT") if node.value.negating else QLabel("AND")
                            and_label.setMargin(0)
                            and_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                            and_label.setStyleSheet("font-weight: bold;")
                            layout.addWidget(and_label)
                            self.widgets.append(and_label)
                        panel = QWidget()
                        panel.setContentsMargins(QMargins(0, 0, 0, 0))
                        or_layout = QHBoxLayout()
                        or_layout.setContentsMargins(QMargins(0, 0, 0, 0))
                        panel.setLayout(or_layout)
                        or_layout.addWidget(node.value)
                        if node.value.request_focus:
                            node.value.request_focus = False
                            filter_requesting_focus = node.value

                node = node.next

            if panel is not None:
                self.widgets.append(panel)
                layout.addWidget(panel)

            # layout.activate()
            layout.update()

            if filter_requesting_focus is not None:
                filter_requesting_focus.setFocus()

        ctx.filters_changed = update_layout
        self.filters = Node[VAQLFilterLineEdit](None)
        filter = VAQLFilterLineEdit(
            op = Op.AND, negating = False, filters_changed_callback = ctx.filters_changed, request_focus = False
        )
        filter.textChanged.connect(self.filters_changed)
        filter.is_connected = True
        self.filters.append_inserting(filter)

        panel = QWidget()

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, "orange")
        panel.setPalette(palette)

        panel.setContentsMargins(QMargins(10, 10, 10, 10))
        or_layout = QHBoxLayout()
        or_layout.setContentsMargins(QMargins(0, 4, 0, 0))
        panel.setLayout(or_layout)
        or_layout.addWidget(self.filters.next.value)
        self.filters.next.value.setFocus()
        self.layout().addWidget(panel)
        self.widgets.append(panel)

    def filters_changed(self):
        all_filters: list[VAQLFilterLineEdit] = []
        filter_node = self.filters.next
        while filter_node is not None:
            assert filter_node.value is not None
            all_filters.append(filter_node.value)
            filter_node = filter_node.next

        self.ctx.filter_on_vaql(all_filters)
