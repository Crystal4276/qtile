
from qtile_extras.popup.toolkit import (
    PopupRelativeLayout,
    PopupImage,
    PopupText
)

def show_power_menu(qtile):
    controls = [
        PopupImage(
            filename="~/.config/qtile/assets/lock.svg",
            pos_x=0,
            pos_y=0.02,
            width=1.0,
            height=0.15,
            highlight_method='image',
            highlight_filename="~/.config/qtile/assets/lock_blur.svg",
            mouse_callbacks={"Button1": lazy.spawn('betterlockscreen -l dim -- --time-str="%H:%M"')}
        ),
        PopupText(
            text="Lock",
            font='monospace Bold',
            fontsize=18,
            pos_x=0,
            pos_y=0.17,
            width=1,
            height=0.075,
            foreground=colors[15],
            h_align="center",
            can_focus=False,
            mouse_callbacks={"Button1": lazy.spawn('betterlockscreen -l dim -- --time-str="%H:%M"')}
        ),
        PopupImage(
            filename="~/.config/qtile/assets/logout.svg",
            pos_x=0.0,
            pos_y=0.27,
            width=1.0,
            height=0.15,
            highlight_method='image',
            highlight_filename="~/.config/qtile/assets/logout_blur.svg",
            mouse_callbacks={"Button1": lazy.shutdown()}
        ),
        PopupText(
            text="Logout",
            font='monospace Bold',
            fontsize=18,
            pos_x=0.0,
            pos_y=0.42,
            width=1.0,
            height=0.075,
            foreground=colors[10],
            h_align="center",
            can_focus=False,
            mouse_callbacks={"Button1": lazy.shutdown()}
        ),
        PopupImage(
            filename="~/.config/qtile/assets/restart.svg",
            pos_x=0.0,
            pos_y=0.52,
            width=1.0,
            height=0.15,
            highlight_method='image',
            highlight_filename="~/.config/qtile/assets/restart_blur.svg",
            mouse_callbacks={"Button1": lazy.spawn("systemctl reboot")}
        ),
        PopupText(
            text="Reboot",
            font='monospace Bold',
            fontsize=18,
            pos_x=0,
            pos_y=0.67,
            width=1,
            height=0.075,
            foreground=colors[12],
            h_align="center",
            can_focus=False,
            mouse_callbacks={"Button1": lazy.spawn("systemctl reboot")}
        ),
        PopupImage(
            filename="~/.config/qtile/assets/shutdown.svg",
            pos_x=0,
            pos_y=0.77,
            width=1.0,
            height=0.15,
            highlight_method='image',
            highlight_filename="~/.config/qtile/assets/shutdown_blur.svg",
            mouse_callbacks={"Button1": lazy.spawn("systemctl poweroff")}
        ),
        PopupText(
            text="Shutdown",
            font='monospace Bold',
            fontsize=18,
            pos_x=0,
            pos_y=0.92,
            width=1,
            height=0.075,
            foreground=colors[13],
            h_align="center",
            can_focus=False,
            mouse_callbacks={"Button1": lazy.spawn("systemctl poweroff")}
        ),
    ]

    layout = PopupRelativeLayout(
        qtile,
        width=100,
        height=350,
        border_width=1,
        border=colors[17],
        controls=controls,
        background=colors[7],
        initial_focus=None,
        hide_interval=0.7,
        hide_on_mouse_leave=True
    )
    layout.show(x=-6, y=0.003, warp_pointer=False,relative_to=3,relative_to_bar=True)
