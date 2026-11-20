# Gotchas (all hit in real edits)

## Tella timeline
- A Tella recording can carry a screen track showing a teleprompter or notes. Never show it: camera-only base layout, screen only during real demos.
- Motion blur on the video smears a frame at cuts: turn it off.
- `update_layout` that changes `media` or `startTimeMs` can reset `transitionStyle` to `spring` (the card slides over the face). Pass `transitionStyle: "hardCut"` in the same call and check `list_layouts`.
- Adding or moving a card layout can flip the NEXT layout to spring: re-set it.
- A card whose doc ends exactly at its slot end shows one black frame: make the doc a bit longer.
- Word timings drift around long pauses: verify with ffmpeg silencedetect and cut by time.

## Tella Motion
- If `apply_motion_editor_commands` returns `fetch failed`, check `get_motion_document`: empty `nodes` means nothing saved, so resend.
- Delete commands are not echoed in the batch result: verify with a frame.
- `animate` pop writes scale keys. `removeKeyframes` on scale leaves the node stuck small: follow with `setProperty scale 1`.
- Slide presets start at the canvas edge: a card sliding down from the top crosses the title. Slide from the side or bottom.
- `addMedia` fills the canvas: `sheet_cmd.py` sets destination, mask and anchor for you. Keyframing a tile does not move its text or icons: animate them too, or pop the contents in after the tile lands.
- The `repeater` effect can crash the renderer (500 on every frame). Build grids from plain shapes, or a dashed line path with round caps for dot rows.
- Default glow washes small coloured shapes out to white or yellow: screen mode, intensity about 0.35, threshold 0.5, or use dropShadow.
- Wipe keyframes work through the long path `field:common/effects/0/effect/uniforms/completion/values/0`.
- Particles emit from the canvas centre by default: move the emitter onto the element.
- Sound preset "pop" does not exist: use press, tick or toggle.
- White icons vanish against a light wall behind the speaker: stickers use dark or coloured icons on a white disc, or a dark plate.

## Screen demos on 9:16
- Crop the screen to the content column, put the face box below, captions at y 0.88.
- A zoom that enlarges the whole frame can push a number off-canvas. For one number, a per-section crop works better.
- A zoom's focus point is where the zoom grows from, not the centre of the view.

## Sideways footage
Phone or camera footage can arrive sideways on a 16:9 canvas. Tella has no rotate, so:
1. `list_sources` gives the raw's signed `.m3u8` url.
2. `bash scripts/prep_footage.sh "<m3u8 url>" <workdir> ccw|cw|none <cut1> <cut2> ...` (cuts at pauses, pieces under about 22 s). `ccw` when the head points right in the raw frame. Check `check.jpg`.
3. `create_source` (kind video, 1080x1920, duration) per piece, put the uploadUrls in `<workdir>/urls.txt`, `bash scripts/put_pieces.sh <workdir>` (every line 200).
4. `upload_clip` per source in order, `delete_clip` the sideways clip, `update_video` 1080x1920, base layout fullscreen.
Some networks cut long uploads: if a PUT fails, cut smaller pieces.
