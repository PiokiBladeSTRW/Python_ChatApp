def error_handle(display_message:str, state:object) -> tuple:
    state.log(f"User Dispaly Error: {display_message}")

    print(f"{{System}}: {display_message}")
    return (None, None, state)