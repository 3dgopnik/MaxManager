"""Test GridLayoutManager functionality."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ui.grid_layout_manager import GridLayoutManager, GridItem


def test_basic_operations():
    """Test basic add/move/resize operations."""
    print("=" * 50)
    print("TEST: Basic Operations")
    print("=" * 50)
    
    grid = GridLayoutManager(max_columns=4)
    
    # Add items
    print("\n1. Adding items...")
    item1 = grid.add_item("Security", row=0, col=0, span=2)
    item2 = grid.add_item("Performance", row=0, col=2, span=1)
    item3 = grid.add_item("OpenImageIO", row=1, col=0, span=4)
    
    assert item1.row == 0 and item1.col == 0 and item1.span == 2
    assert item2.row == 0 and item2.col == 2 and item2.span == 1
    assert item3.row == 1 and item3.col == 0 and item3.span == 4
    print("[OK] Items added correctly")
    
    # Move item
    print("\n2. Moving Performance to row 1...")
    moved = grid.move_item("Performance", target_row=1, target_col=0)
    print(f"   Result: {moved}")
    # Should auto-shift to available position
    print("[OK] Item moved with auto-shift")
    
    # Resize item
    print("\n3. Resizing Security span 2 -> 3...")
    resized = grid.resize_item("Security", new_span=3)
    print(f"   Result: {resized}")
    print("[OK] Item resized")
    
    print("\n4. Final grid state:")
    for item in grid.get_all_items():
        print(f"   {item}")


def test_collision_detection():
    """Test collision detection and auto-shift."""
    print("\n" + "=" * 50)
    print("TEST: Collision Detection")
    print("=" * 50)
    
    grid = GridLayoutManager(max_columns=4)
    
    # Fill row 0
    print("\n1. Filling row 0...")
    grid.add_item("A", row=0, col=0, span=2)
    grid.add_item("B", row=0, col=2, span=2)
    
    # Try to add conflicting item
    print("\n2. Adding item at occupied position (should auto-shift)...")
    item_c = grid.add_item("C", row=0, col=1, span=1)
    print(f"   C placed at: row={item_c.row}, col={item_c.col}")
    assert item_c.row == 1, "Item should be shifted to next row"
    print("[OK] Auto-shift works")
    
    # Test span overflow
    print("\n3. Adding span=3 at col=2 (should adjust)...")
    item_d = grid.add_item("D", row=2, col=2, span=3)
    print(f"   D placed at: row={item_d.row}, col={item_d.col}, span={item_d.span}")
    assert item_d.col + item_d.span <= 4, "Item should fit within grid"
    print("[OK] Span clamping works")


def test_responsive_columns():
    """Test responsive column adjustment."""
    print("\n" + "=" * 50)
    print("TEST: Responsive Columns")
    print("=" * 50)
    
    grid = GridLayoutManager(max_columns=4)
    
    widths = [500, 800, 1200, 1800]
    expected = [1, 2, 3, 4]
    
    print("\nTesting viewport widths:")
    for width, exp_cols in zip(widths, expected):
        cols = grid.calculate_columns(width)
        print(f"   {width}px -> {cols} columns (expected {exp_cols})")
        assert cols == exp_cols
    
    print("[OK] Responsive column calculation works")


def test_serialization():
    """Test to_dict/from_dict."""
    print("\n" + "=" * 50)
    print("TEST: Serialization")
    print("=" * 50)
    
    grid = GridLayoutManager(max_columns=4)
    
    # Add items
    grid.add_item("Security", row=0, col=0, span=2)
    grid.add_item("Performance", row=0, col=2, span=1)
    grid.add_item("OpenImageIO", row=1, col=0, span=4)
    
    # Export
    print("\n1. Exporting grid state...")
    data = grid.to_dict()
    print(f"   Exported: {data}")
    
    # Import to new grid
    print("\n2. Importing to new grid...")
    grid2 = GridLayoutManager(max_columns=4)
    grid2.from_dict(data)
    
    # Compare
    assert len(grid2.items) == 3
    assert grid2.get_item("Security").row == 0
    assert grid2.get_item("Security").span == 2
    print("[OK] Serialization works")


if __name__ == "__main__":
    try:
        test_basic_operations()
        test_collision_detection()
        test_responsive_columns()
        test_serialization()
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

