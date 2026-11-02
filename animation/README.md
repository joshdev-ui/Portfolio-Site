# Tenor wave and automatic portrait loop

Source selected by the user: https://tenor.com/view/anime-anime-wave-bye-wave-bye-gif-21919207

Original GIF URL: https://media1.tenor.com/m/ILT5-vuNzB8AAAAd/anime-anime-wave-bye.gif

`source-wave.gif` preserves the original 640 × 640, 19-frame, 630 ms GIF. The original animation is retained; no replacement character motion is generated. The original room background is removed while preserving the original RGB colors and the moving hand. Source-specific edge cleanup removes room pixels between the fingers and trims the chair outside the sleeve.

## Published assets

Files are in `dist/assets/` (`public/assets/` in the Vercel export):

- `joshua-tenor-portrait-loop.webp`: 928 × 768, optimized animated WebP, 4 seconds, infinite loop. Two seconds of the photograph followed by two seconds of the original GIF repeating at its original cadence. The 0.2-second fades sit inside the GIF phase. First and last frames match.
- `tenor-wave-transparent.webp`: 928 × 768, 19 frames, 630 ms, WebP with alpha transparency. Reusable cutout, not required by the page.

Both phases use one fixed frame. The character’s hairline and chin match the portrait’s head height, the face remains centered, and the lower torso follows a matching rounded crop with room for the waving hand. Side space lets the hand wave without changing the layout.

The page uses an animated image, with no video tag, media controls, or third-party embed. Reduced motion and image errors fall back to Joshua’s photograph. All required runtime assets are local.

## Optional authoring

These tools regenerate the animated assets; they are not required for Vercel:

1. Install Python, `rembg[cpu]`, `opencv-python-headless`, `pillow`, and `numpy`.
2. Run `OMP_NUM_THREADS=4 python animation/prepare-gif.py animation/source-wave.gif --cache /path/to/cutout-cache`. The BiRefNet General Lite model is downloaded automatically on first use.
3. Rasterize `animation/portrait-background.svg` to a 768 × 768 PNG.
4. Run `python animation/render-gif-loop.py --cache /path/to/cutout-cache --background /path/to/background.png --assets public/assets --review /path/to/review`. Use `dist/assets` in the hosted Site source checkout.
5. Add `--stills` for review images only.

The neural model and frame cache are excluded from the source ZIP. Background-removal tooling: https://github.com/danielgatis/rembg
