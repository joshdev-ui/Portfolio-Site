# Joshua Sarno — Portfolio for Vercel

A complete static website. No Node build, API keys, or server are required.

## Deploy on Vercel

1. Extract this ZIP. The folder containing `vercel.json` is the project root.
2. Upload the folder to your Git repository and import that repository into Vercel.
3. Choose Framework Preset **Other**, leave the build/install commands empty, and set Output Directory to **public**. The included `vercel.json` supplies these settings.
4. Deploy.

For a local preview, run `python -m http.server 8000 --directory public` from this folder.

## Landing animation

A smooth, 1.6-second entrance brings in the navigation, orange circle, text, buttons, and hero animation when the page first opens. It plays once per arrival at the top of the page. Scrolling or interacting completes the entrance immediately, and reduced-motion preferences skip it. Edit the entrance timing in `public/styles.css` and its lifecycle in `public/landing.js`.

## Hero GIF loop

The hero shows only the selected Tenor anime wave, looping continuously at its original speed. The GIF's room background is removed and the character is placed over the same peach/orange developer artwork in a fixed frame. There is no photograph in the hero. Joshua's photograph appears only in the "How I Approach Development" section.

The animation is an optimized WebP image; there is no video element, audio, media control, or third-party embed. Reduced-motion visitors see a still frame of the same artwork.

- `public/assets/joshua-tenor-wave-loop.webp`: 928 x 768 animated WebP, 18 frames, 630 ms, infinite loop.
- `public/assets/joshua-tenor-wave-still.webp`: first frame, shown when reduced motion is requested.
- `public/assets/tenor-wave-transparent.webp`: aligned GIF cutout with alpha transparency, the source for the loop above.
- `public/assets/joshua-tenor-portrait-loop.webp` and `joshua-portfolio-hero.png`: earlier photo-plus-GIF loop and hero photo. No longer used by the page.
- `animation/`: original GIF, source attribution, optional background-removal and rendering scripts. These tools are not required for Vercel.

## Editing

Edit content in `public/index.html`, styling in `public/styles.css`, and general interactions in `public/app.js`. The font and Lenis scrolling library are self-hosted. Projects remain intentionally empty. The contact form opens an email draft for the visitor to review and send; it does not send messages from a server.

Verified responsive framing on desktop, mobile, and tablet; no video controls; reduced-motion and failed-image fallbacks; and offscreen behavior.
