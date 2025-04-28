def error_handle(display_message:str, state:object) -> tuple:
    print(f"{{System}}: {display_message}")
    return (None, None, state)