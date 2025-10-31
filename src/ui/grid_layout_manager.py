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
        Calculate number of columns with STRETCH logic.
        
        Strategy: Add new column only when there's space for NEXT full column.
        This allows columns to stretch and use all available space.
        
        Examples (cell_width=460px, spacing=10px):
        - 970px:  2 cols × 460px = stay at 2 (not enough for 3rd)
        - 1200px: 2 cols × 585px = STRETCH (still not enough for 3rd)
        - 1450px: 3 cols × 476px = add 3rd column!
        - 1700px: 3 cols × 560px = STRETCH (not enough for 4th)
        - 1920px: 4 cols × 470px = add 4th column!
        
        Logic: Show N columns if space for (N+1) × min_width OR already at max
        """
        # Available = viewport - left_margin(10) - right_margin(10)
        # CRITICAL: Spacing is ALWAYS 10px, only canvas width changes!
        available = viewport_width - 20
        
        # Calculate maximum columns that can physically fit
        for cols in range(self.max_columns, 0, -1):
            min_needed = cols * self.cell_width + (cols - 1) * self.spacing
            if available >= min_needed:
                # Can fit cols columns
                # Check if we should add one more column
                if cols < self.max_columns:
                    # Space needed for next column
                    next_col_needed = (cols + 1) * self.cell_width + cols * self.spacing
                    if available >= next_col_needed:
                        return cols + 1  # Add next column
                return cols  # Stay at current, let columns stretch
        
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
            # Reflow items to fit new column count
            self._reflow_items()
            return True
        return False
    
    def _reflow_items(self):
        """
        Preserve ALL positions (ChatGPT Hybrid + JUSTIFIED approach).
        
        CRITICAL: NEVER auto-reflow! Manual and Skyline positions are SACRED.
        Only clamp span if needed - KEEP col positions even if overflow!
        Masonry layout will handle rendering correctly.
        """
        print(f"[GridLayout] Preserving ALL positions for {self.current_columns} columns")
        
        for canvas_id, item in self.items.items():
            # Only clamp span if absolutely necessary
            old_span = item.span
            item.span = min(item.span, self.current_columns)
            
            if old_span != item.span:
                print(f"[GridLayout]   Clamped '{canvas_id}' span: {old_span} -> {item.span}")
            
            # CRITICAL: KEEP col position even if it overflows!
            # Masonry layout will handle it (wrap to available space)
            print(f"[GridLayout]   Preserved '{canvas_id}' at ({item.row}, {item.col}), span={item.span}")
    
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
    
    def resize_item(self, canvas_id: str, new_span: int) -> bool:
        """
        Resize item to new span and auto-shift neighbors.
        
        Args:
            canvas_id: ID of canvas to resize
            new_span: New span (1-4)
        
        Returns:
            True if resize successful, False otherwise
        """
        if canvas_id not in self.items:
            print(f"[GridLayout] Resize failed: {canvas_id} not found")
            return False
        
        item = self.items[canvas_id]
        old_span = item.span
        
        if old_span == new_span:
            print(f"[GridLayout] No resize needed: {canvas_id} already {new_span}x")
            return False
        
        print(f"[GridLayout] Resizing '{canvas_id}': {old_span}x → {new_span}x at ({item.row}, {item.col})")
        
        # Update span
        item.span = new_span
        
        # Auto-shift neighbors if needed
        self._auto_shift_after_resize(canvas_id, old_span, new_span)
        
        print(f"[GridLayout] Resize complete: {canvas_id} now {new_span}x")
        return True
    
    def _auto_shift_after_resize(self, resized_id: str, old_span: int, new_span: int):
        """
        Auto-shift neighbors horizontally with wrap to next row.
        
        JUSTIFIED LOGIC (1234, 5678):
        - Growing: push neighbors RIGHT, wrap to next row if overflow
        - Shrinking: pull neighbors LEFT, pull UP from row below if space
        """
        resized_item = self.items[resized_id]
        
        if new_span > old_span:
            print(f"[GridLayout] GROW {resized_id}: {old_span}x -> {new_span}x, pushing right")
            
            # Get ALL items on same row, sorted by column
            same_row = sorted(
                [(id, item) for id, item in self.items.items()
                 if item.row == resized_item.row and id != resized_id],
                key=lambda x: x[1].col
            )
            
            # Calculate new positions - SHIFT RIGHT
            delta = new_span - old_span
            new_end_col = resized_item.col + new_span
            
            for neighbor_id, neighbor in same_row:
                if neighbor.col >= resized_item.col:
                    # This neighbor is to the right - SHIFT it
                    neighbor.col += delta
                    
                    # If overflow - WRAP to next row
                    if neighbor.col + neighbor.span > self.current_columns:
                        neighbor.row += 1
                        neighbor.col = 0
                        print(f"[GridLayout]   '{neighbor_id}' wrapped to row {neighbor.row}")
                    else:
                        print(f"[GridLayout]   '{neighbor_id}' shifted to col {neighbor.col}")
        
        elif new_span < old_span:
            print(f"[GridLayout] SHRINK {resized_id}: {old_span}x -> {new_span}x, pulling left/up")
            
            # Get ALL items, sorted by (row, col)
            all_items = sorted(
                [(id, item) for id, item in self.items.items() if id != resized_id],
                key=lambda x: (x[1].row, x[1].col)
            )
            
            # Try to compact: move items left and up if space available
            for neighbor_id, neighbor in all_items:
                if neighbor.row == resized_item.row and neighbor.col > resized_item.col:
                    # Same row, to the right - try to pull LEFT
                    delta = old_span - new_span
                    new_col = neighbor.col - delta
                    if new_col >= resized_item.col + new_span:
                        neighbor.col = new_col
                        print(f"[GridLayout]   Pulled '{neighbor_id}' LEFT to col {new_col}")
                
                elif neighbor.row > resized_item.row:
                    # Lower row - try to pull UP to current row
                    for try_col in range(self.current_columns - neighbor.span + 1):
                        if self._can_place(resized_item.row, try_col, neighbor.span):
                            old_row = neighbor.row
                            neighbor.row = resized_item.row
                            neighbor.col = try_col
                            print(f"[GridLayout]   Pulled '{neighbor_id}' UP: ({old_row},{neighbor.col}) -> ({neighbor.row},{try_col})")
                            break
    
    def find_optimal_position(self, span: int) -> Tuple[int, int]:
        """
        JUSTIFIED layout: Fill HORIZONTALLY first! (1234, 5678, 9...)
        
        Uses Skyline to find shortest column, places there.
        Each canvas gets UNIQUE row for masonry (no height stretch).
        
        Args:
            span: Widget span (1-4)
            
        Returns:
            (row, col) tuple with optimal position
        """
        # Track column heights (count of items in each column)
        column_heights = [0] * self.current_columns
        
        for item in self.items.values():
            for col in range(item.col, min(item.col + item.span, self.current_columns)):
                column_heights[col] += 1
        
        # Find SHORTEST column (Skyline algorithm)
        min_height = min(column_heights) if column_heights else 0
        
        # Find first column with min height that fits span
        best_col = 0
        for col in range(self.current_columns - span + 1):
            if column_heights[col] == min_height:
                # Check if all spanned columns are at same height (for multi-span)
                if all(column_heights[c] == min_height for c in range(col, col + span)):
                    best_col = col
                    break
        
        # CRITICAL: Row = height of the column we're placing in!
        # This creates JUSTIFIED horizontal filling:
        # Row 0: Canvas 1,2,3,4 (all column_heights[col] = 0 initially)
        # Row 1: Canvas 5,6,7,8 (all column_heights[col] = 1)
        best_row = min_height
        
        print(f"[Skyline] JUSTIFIED: row={best_row}, col={best_col}, span={span}")
        print(f"  Column heights: {column_heights}")
        
        return (best_row, best_col)
    
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

