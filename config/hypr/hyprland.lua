-- Reference configuration from the working Parrot/Caelestia setup.
-- scripts/export-dotfiles.py captures the actual laptop configuration.

-- Automatically configure connected displays.
hl.monitor({
    output = "",
    mode = "preferred",
    position = "auto",
    scale = 1
})

-- Essential shortcuts. SUPER is the Windows key.
hl.bind("SUPER + Return", hl.dsp.exec_cmd("konsole"))
hl.bind("SUPER + Q", hl.dsp.window.close())
hl.bind("SUPER + SHIFT + E", hl.dsp.exit())
hl.bind("SUPER + F", hl.dsp.window.fullscreen({
    mode = "fullscreen",
    action = "toggle"
}))
hl.bind("SUPER + V", hl.dsp.window.float({ action = "toggle" }))

-- Focus windows using arrow keys.
hl.bind("SUPER + Left", hl.dsp.focus({ direction = "l" }))
hl.bind("SUPER + Right", hl.dsp.focus({ direction = "r" }))
hl.bind("SUPER + Up", hl.dsp.focus({ direction = "u" }))
hl.bind("SUPER + Down", hl.dsp.focus({ direction = "d" }))

-- Switch workspaces or move windows to them.
for i = 1, 5 do
    hl.bind("SUPER + " .. i, hl.dsp.focus({ workspace = i }))
    hl.bind("SUPER + SHIFT + " .. i, hl.dsp.window.move({ workspace = i }))
end

-- Move and resize windows with the mouse.
hl.bind("SUPER + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind("SUPER + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- BEGIN CAELESTIA SETUP
local caelestia_qs = '/usr/local/bin/quickshell -p "$HOME/.config/quickshell/caelestia"'
local caelestia_start = 'env QS_ICON_THEME=Papirus-Dark PATH="$HOME/.local/bin:$PATH" ' .. caelestia_qs .. ' -n -d'

-- Start the shell when the Hyprland session begins.
hl.on("hyprland.start", function()
    hl.dispatch(hl.dsp.exec_cmd(caelestia_start))
end)

hl.bind("SUPER + Space", hl.dsp.global("caelestia:launcher"))
hl.bind("SUPER + C", hl.dsp.global("caelestia:controlCenter"))
hl.bind("SUPER + Escape", hl.dsp.global("caelestia:session"))
hl.bind("SUPER + SHIFT + Space", hl.dsp.global("caelestia:showall"))

hl.bind("SUPER + D", hl.dsp.exec_cmd(
    caelestia_qs .. " ipc call drawers toggle dashboard"
))

-- Launch Brave directly; browser default selection is independent.
hl.bind("SUPER + B", hl.dsp.exec_cmd("brave-browser"))
-- END CAELESTIA SETUP
