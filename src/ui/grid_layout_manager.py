"""
Grid Layout Manager for MaxManager Canvas.

Manages flexible grid layout (1-4 columns) with automatic collision detection,
auto-shift, and responsive column adjustment.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class GridItem:
    """Represents an item in the grid."""
    canvas_id: str
    row: int
    col: int
    span: int  # Number of columns to span (1-4)
    
    def __repr__(self):
        return f"GridItem({self.canvas_id}, r{self.row}, c{self.col}, span={self.span})"


class GridLayoutManager:
    """
    Manages grid-based layout with automatic positioning and collision resolution.
    
    Features:
    - Adaptive 1-4 columns based on viewport width
    - Automatic collision detection
    - Auto-shift items on conflict
    - Span support (items can occupy multiple columns)
    """
    
    def __init__(self, max_columns: int = 4, cell_width: int = 460, spacing: int = 10):
        """
        Initialize grid layout manager.
        
        Args:
            max_columns: Maximum number of columns (default: 4)
            cell_width: Minimum width of a single cell in pixels
            spacing: Spacing between items in pixels
        """
        self.max_columns = max_columns
        self.cell_width = cell_width
        self.spacing = spacing
        self.items: Dict[str, GridItem] = {}  # canvas_id -> GridItem
        self.current_columns = max_columns
        
    def calculate_columns(self, viewport_width: int) -> int:
        """
        Calculate number of columns based on viewport width.
        
        Uses cell_width (460px min per canvas) + spacing (10px) to determine fit.
        
        Breakpoints (with 15px scrollbar + margins):
        - < 970px: 1 column (460 + margins)
        - 970-1450px: 2 columns (2×460 + spacing + margins)
        - 1450-1920px: 3 columns (3×460 + 2×spacing + margins)
        - > 1920px: 4 columns (4×460 + 3×spacing + margins)
        """
        # Calculate how many columns can fit
        # Available = viewport - scrollbar(15) - right_margin(15)
        available = viewport_width - 30
        
        # Each column needs: cell_width(460) + spacing(10)
        # Last column doesn't need spacing
        for cols in range(self.max_columns, 0, -1):
            needed = cols * self.cell_width + (cols - 1) * self.spacing
            if available >= needed:
                return cols
        
        return 1  # Fallback
    
    def update_columns(self, viewport_width: int) -> bool:
        """
        Update current column count based on viewport width.
        
        Returns:
            True if column count changed, False otherwise
        """
        new_columns = self.calculate_columns(viewport_width)
        if new_columns != self.current_columns:
            old_columns = self.current_columns
            self.current_columns = new_columns
            print(f"[GridLayout] Columns changed: {old_columns} -> {new_columns}")
            return True
        return False
    
    def add_item(self, canvas_id: str, row: int, col: int, span: int = 1) -> GridItem:
        """
        Add item to grid with automatic collision resolution.
        
        Args:
            canvas_id: Unique identifier for canvas
            row: Target row
            col: Target column (0-based)
            span: Number of columns to span
        
        Returns:
            GridItem with final position (may differ from target if collision occurred)
        """
        # Clamp span to current columns
        span = min(span, self.current_columns)
        
        # Clamp column to valid range
        col = max(0, min(col, self.current_columns - span))
        
        # Check for collision and auto-shift if needed
        final_row, final_col = self._find_free_position(row, col, span)
        
        item = GridItem(canvas_id, final_row, final_col, span)
        self.items[canvas_id] = item
        
        print(f"[GridLayout] Added {item}")
        return item
    
    def move_item(self, canvas_id: str, target_row: int, target_col: int) -> Optional[GridItem]:
        """
        Move item to new position with auto-shift.
        
        Args:
            canvas_id: ID of item to move
            target_row: Target row
            target_col: Target column
        
        Returns:
            Updated GridItem or None if item not found
        """
        if canvas_id not in self.items:
            return None
        
        item = self.items[canvas_id]
        old_pos = (item.row, item.col)
        
        # Temporarily remove item from grid
        del self.items[canvas_id]
        
        # Find free position
        span = item.span
        target_col = max(0, min(target_col, self.current_columns - span))
        final_row, final_col = self._find_free_position(target_row, target_col, span)
        
        # Update item
        item.row = final_row
        item.col = final_col
        self.items[canvas_id] = item
        
        print(f"[GridLayout] Moved {canvas_id}: {old_pos} -> ({final_row}, {final_col})")
        return item
    
    def resize_item(self, canvas_id: str, new_span: int) -> Optional[GridItem]:
        """
        Change item span with collision resolution.
        
        Args:
            canvas_id: ID of item to resize
            new_span: New span (1-4)
        
        Returns:
            Updated GridItem or None if item not found
        """
        if canvas_id not in self.items:
            return None
        
        item = self.items[canvas_id]
        old_span = item.span
        
        # Clamp to valid range
        new_span = max(1, min(new_span, self.current_columns))
        
        if new_span == old_span:
            return item
        
        # Temporarily remove
        del self.items[canvas_id]
        
        # Check if new span fits at current position
        if self._can_place(item.row, item.col, new_span):
            item.span = new_span
        else:
            # Find new position
            row, col = self._find_free_position(item.row, item.col, new_span)
            item.row = row
            item.col = col
            item.span = new_span
        
        self.items[canvas_id] = item
        print(f"[GridLayout] Resized {canvas_id}: span {old_span} -> {new_span}")
        return item
    
    def remove_item(self, canvas_id: str) -> bool:
        """Remove item from grid."""
        if canvas_id in self.items:
            del self.items[canvas_id]
            print(f"[GridLayout] Removed {canvas_id}")
            return True
        return False
    
    def get_item(self, canvas_id: str) -> Optional[GridItem]:
        """Get item by ID."""
        return self.items.get(canvas_id)
    
    def get_all_items(self) -> List[GridItem]:
        """Get all items sorted by position (row, then col)."""
        return sorted(self.items.values(), key=lambda x: (x.row, x.col))
    
    def _find_free_position(self, start_row: int, start_col: int, span: int) -> Tuple[int, int]:
        """
        Find first free position starting from (start_row, start_col).
        
        Returns:
            (row, col) tuple of free position
        """
        # Ensure start_col is valid for span
        start_col = max(0, min(start_col, self.current_columns - span))
        
        # Try starting position first
        if self._can_place(start_row, start_col, span):
            return (start_row, start_col)
        
        # Scan row-by-row, column-by-column
        for row in range(start_row, start_row + 100):  # Limit search depth
            for col in range(self.current_columns - span + 1):
                if self._can_place(row, col, span):
                    return (row, col)
        
        # Fallback: place at end
        max_row = max((item.row for item in self.items.values()), default=-1)
        return (max_row + 1, 0)
    
    def _can_place(self, row: int, col: int, span: int) -> bool:
        """
        Check if item can be placed at position without collision.
        
        Args:
            row: Row position
            col: Column position
            span: Number of columns to span
        
        Returns:
            True if position is free, False if collision
        """
        # Check bounds
        if col < 0 or col + span > self.current_columns:
            return False
        
        # Check collision with existing items
        for item in self.items.values():
            if item.row == row:
                # Check horizontal overlap
                item_end = item.col + item.span
                new_end = col + span
                
                # Overlap if: item starts before new ends AND new starts before item ends
                if item.col < new_end and col < item_end:
                    return False
        
        return True
    
    def get_occupied_cells(self, row: int) -> List[Tuple[int, int]]:
        """
        Get list of occupied column ranges for a given row.
        
        Returns:
            List of (start_col, end_col) tuples
        """
        occupied = []
        for item in self.items.values():
            if item.row == row:
                occupied.append((item.col, item.col + item.span))
        return sorted(occupied)
    
    def clear(self):
        """Remove all items from grid."""
        self.items.clear()
        print("[GridLayout] Cleared all items")
    
    def to_dict(self) -> Dict[str, Dict]:
        """
        Export grid state to dictionary for serialization.
        
        Returns:
            Dict with canvas_id as key and position data as value
        """
        return {
            canvas_id: {
                "row": item.row,
                "col": item.col,
                "span": item.span
            }
            for canvas_id, item in self.items.items()
        }
    
    def from_dict(self, data: Dict[str, Dict]):
        """
        Import grid state from dictionary.
        
        Args:
            data: Dictionary with canvas positions
        """
        self.clear()
        for canvas_id, pos_data in data.items():
            self.add_item(
                canvas_id,
                pos_data.get("row", 0),
                pos_data.get("col", 0),
                pos_data.get("span", 1)
            )

