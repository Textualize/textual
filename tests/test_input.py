async def test_input_clear():
    """Test that the clear method works correctly."""
    input_widget = Input()
    input_widget.value = "Hello World"
    
    # Verify initial value
    assert input_widget.value == "Hello World"
    
    # Clear the input
    input_widget.clear()
    
    # Verify value is now empty
    assert input_widget.value == ""