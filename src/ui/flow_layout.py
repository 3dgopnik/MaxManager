"""
QFlowLayout - Official Qt example layout.

Adapted from Qt official example:
https://doc.qt.io/qt-6/qtwidgets-layouts-flowlayout-example.html
"""

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QLayoutItem, QSizePolicy, QStyle, QWidget


class QFlowLayout(QLayout):
    """Flow layout that arranges widgets horizontally and wraps to next line when needed."""

    def __init__(self, parent: QWidget | None = None, margin: int = 0, h_spacing: int = -1, v_spacing: int = -1):
        super().__init__(parent)
        
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        
        self._item_list = []
        self._h_space = h_spacing
        self._v_space = v_spacing

    def __del__(self):
        while item := self.takeAt(0):
            del item

    def addItem(self, item: QLayoutItem):
        """Add an item to the layout."""
        self._item_list.append(item)

    def horizontalSpacing(self) -> int:
        """Return the horizontal spacing."""
        if self._h_space >= 0:
            return self._h_space
        return self._smartSpacing(QStyle.PixelMetric.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self) -> int:
        """Return the vertical spacing."""
        if self._v_space >= 0:
            return self._v_space
        return self._smartSpacing(QStyle.PixelMetric.PM_LayoutVerticalSpacing)

    def count(self) -> int:
        """Return the number of items in the layout."""
        return len(self._item_list)

    def itemAt(self, index: int) -> QLayoutItem | None:
        """Return the item at the given index."""
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index: int) -> QLayoutItem | None:
        """Remove and return the item at the given index."""
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self) -> Qt.Orientation:
        """Return the expanding directions."""
        return Qt.Orientation(0)

    def hasHeightForWidth(self) -> bool:
        """Return whether the layout handles height for width."""
        return True

    def heightForWidth(self, width: int) -> int:
        """Return the height for a given width."""
        return self._do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect: QRect):
        """Set the geometry of the layout."""
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self) -> QSize:
        """Return the size hint of the layout."""
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        """Return the minimum size of the layout."""
        size = QSize()
        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())
        
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect: QRect, test_only: bool) -> int:
        """Arrange the items in the layout."""
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self._item_list:
            widget = item.widget()
            space_x = self.horizontalSpacing()
            if space_x == -1:
                space_x = widget.style().layoutSpacing(
                    QSizePolicy.ControlType.PushButton,
                    QSizePolicy.ControlType.PushButton,
                    Qt.Orientation.Horizontal
                )
            
            space_y = self.verticalSpacing()
            if space_y == -1:
                space_y = widget.style().layoutSpacing(
                    QSizePolicy.ControlType.PushButton,
                    QSizePolicy.ControlType.PushButton,
                    Qt.Orientation.Vertical
                )
            
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y() + bottom

    def _smartSpacing(self, pm: QStyle.PixelMetric) -> int:
        """Return the smart spacing based on the style of the parent widget."""
        parent = self.parent()
        if not parent:
            return -1
        if parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        return parent.spacing()

