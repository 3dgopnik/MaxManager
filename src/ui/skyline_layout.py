"""
Skyline Layout - Masonry layout with multi-span support.

Uses Skyline algorithm to pack widgets efficiently:
- Tracks height of each column
- Places widget where max(heights[col:col+span]) is minimal
- Supports 1x/2x/3x/4x column spans
- Fixed 10px spacing (horizontal + vertical)
"""

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QLayoutItem, QWidget


class SkylineLayout(QLayout):
    """Masonry layout using Skyline packing algorithm."""
    
    def __init__(self, parent: QWidget | None = None, columns: int = 4, spacing: int = 10):
        super().__init__(parent)
        self._items = []
        self._columns = columns
        self._spacing = spacing
        self._column_heights = [0] * columns  # Track height of each column
        
    def addItem(self, item: QLayoutItem):
        """Add item to layout."""
        self._items.append(item)
        
    def count(self) -> int:
        """Return number of items."""
        return len(self._items)
    
    def itemAt(self, index: int) -> QLayoutItem | None:
        """Return item at index."""
        if 0 <= index < len(self._items):
            return self._items[index]
        return None
    
    def takeAt(self, index: int) -> QLayoutItem | None:
        """Remove and return item at index."""
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None
    
    def setGeometry(self, rect: QRect):
        """Layout items using Skyline algorithm."""
        super().setGeometry(rect)
        self._do_skyline_layout(rect)
    
    def sizeHint(self) -> QSize:
        """Return preferred size."""
        return self.minimumSize()
    
    def minimumSize(self) -> QSize:
        """Return minimum size."""
        # Calculate based on widest item and total height
        if not self._items:
            return QSize(100, 100)
        
        max_width = max(item.minimumSize().width() for item in self._items)
        total_height = sum(item.minimumSize().height() for item in self._items)
        
        margins = self.contentsMargins()
        return QSize(
            max_width + margins.left() + margins.right(),
            total_height // self._columns + margins.top() + margins.bottom()
        )
    
    def _do_skyline_layout(self, rect: QRect):
        """
        Skyline packing algorithm:
        1. For each widget, determine its span (stored as widget property)
        2. Find column position where max(heights[col:col+span]) is minimal
        3. Place widget at that position
        4. Update column heights
        """
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)
        
        # Reset column heights
        self._column_heights = [0] * self._columns
        
        # Calculate column width
        available_width = effective_rect.width() - (self._columns - 1) * self._spacing
        col_width = available_width // self._columns
        
        for item in self._items:
            widget = item.widget()
            if not widget:
                continue
            
            # Get span from widget property (default=1)
            span = getattr(widget, '_layout_span', 1)
            span = min(span, self._columns)  # Clamp to available columns
            
            # Find best position using Skyline algorithm
            best_col = self._find_best_column(span)
            
            # Calculate position
            x = effective_rect.x() + best_col * (col_width + self._spacing)
            y = effective_rect.y() + self._column_heights[best_col]
            
            # Calculate size
            width = span * col_width + (span - 1) * self._spacing
            height = widget.sizeHint().height()
            
            # Set geometry
            item.setGeometry(QRect(x, y, width, height))
            
            # Update column heights for all spanned columns
            new_height = self._column_heights[best_col] + height + self._spacing
            for i in range(best_col, best_col + span):
                if i < self._columns:
                    self._column_heights[i] = new_height
    
    def _find_best_column(self, span: int) -> int:
        """
        Find column where placing widget with given span results in minimal height.
        
        Skyline algorithm: for each possible position, find max height across span,
        then choose position with minimal max height.
        """
        best_col = 0
        min_max_height = float('inf')
        
        # Try each possible starting column
        for col in range(self._columns - span + 1):
            # Find max height across span
            max_height = max(self._column_heights[col:col + span])
            
            # If this is better (lower), use it
            if max_height < min_max_height:
                min_max_height = max_height
                best_col = col
        
        return best_col
    
    def set_columns(self, columns: int):
        """Update column count and trigger relayout."""
        if columns != self._columns:
            self._columns = columns
            self._column_heights = [0] * columns
            self.invalidate()
    
    def set_item_span(self, item_index: int, span: int):
        """Set span for specific item."""
        if 0 <= item_index < len(self._items):
            widget = self._items[item_index].widget()
            if widget:
                widget._layout_span = span
                self.invalidate()

