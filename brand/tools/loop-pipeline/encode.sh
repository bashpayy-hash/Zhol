#!/bin/bash
# masters (ffv1 gbrp, 30 fps) -> H.264 / VP9 tagged BT.709 matrix + primaries, sRGB transfer, tv range
set -e
cd "$(dirname "$0")"
M=${OUT:-./out}; mkdir -p $M
TAGS="-colorspace bt709 -color_primaries bt709 -color_trc iec61966-2-1 -color_range tv"
vf(){ echo "scale=$1:-2:flags=lanczos+accurate_rnd+full_chroma_int:out_color_matrix=bt709:out_range=tv,format=yuv420p"; }
h264(){ # master out width crf gop
  ffmpeg -v error -y -i $1 -an -vf "$(vf $3)" -c:v libx264 -preset slow -tune film -profile:v high -crf $4 -g $5 -keyint_min $5 -sc_threshold 0 -r 30 $TAGS -movflags +faststart+write_colr $2; }
vp9(){ ffmpeg -v error -y -i $1 -an -vf "$(vf 960)" -c:v libvpx-vp9 -crf 31 -b:v 0 -row-mt 1 -g $3 -r 30 $TAGS $2; }
# Each spec: <ffv1 master from compose.py> <name> <mid width> <large width> <GOP = frames in one loop>. Edit the list for your scenes.
for spec in "bo_m.mkv bologna 1600 2400 240" "be_m.mkv belvedere 1600 2400 240" "pl_m.mkv plan-loggia 1600 2560 240" "tus_m.mkv tuscany-ride 1600 2400 360"; do
  set -- $spec
  h264 $1 $M/$2-$4.mp4 $4 19 $5
  h264 $1 $M/$2-$3.mp4 $3 20 $5
  h264 $1 $M/$2-960.mp4 960 22 $5
  vp9 $1 $M/$2-960.webm $5
  echo "$2 done"
done
ls -l $M
echo ENCODED
