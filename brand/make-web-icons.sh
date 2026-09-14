#!/usr/bin/env bash
set -euo pipefail
brand_root="$(cd "$(dirname "$0")" && pwd)"
brand_master="$brand_root/masters/BEACN-front-4K.png"
mkdir -p "$brand_root/web"
convert "$brand_master" -resize 1024x1024 -strip "$brand_root/web/pfp.png"
convert "$brand_master" -resize 1024x1024 -strip -quality 90 "$brand_root/web/beacon-poster.webp"
for brand_size in 16 32 48 64 180 192 256 512; do
  convert "$brand_master" -resize "${brand_size}x${brand_size}" -strip "$brand_root/web/icon-${brand_size}.png"
done
convert "$brand_root/web/icon-16.png" "$brand_root/web/icon-32.png" "$brand_root/web/icon-48.png" "$brand_root/web/favicon.ico"
convert "$brand_master" -resize 600x600 -background '#04070f' -gravity center -extent 1200x630 -strip "$brand_root/web/og.png"
