# #!/usr/bin/env python3
import iterm2

async def main(connection):
    app = await iterm2.async_get_app(connection)
    session = app.current_terminal_window.current_tab.current_session
    await session.async_send_text("ncdocs\nnpm start\n")

iterm2.run_until_complete(main)

