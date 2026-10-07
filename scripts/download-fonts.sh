#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail

caelestia_fonts="$HOME/.local/share/fonts/caelestia"
mkdir -p "$caelestia_fonts"

curl --fail --location --retry 3 \
  'https://raw.githubusercontent.com/google/material-design-icons/master/variablefont/MaterialSymbolsRounded%5BFILL%2CGRAD%2Copsz%2Cwght%5D.ttf' \
  --output "$caelestia_fonts/MaterialSymbolsRounded.ttf"

curl --fail --location --retry 3 \
  'https://raw.githubusercontent.com/google/fonts/main/ofl/rubik/Rubik%5Bwght%5D.ttf' \
  --output "$caelestia_fonts/Rubik.ttf"

fc-cache -f "$caelestia_fonts"
fc-match -f '%{family}\n' 'Material Symbols Rounded'
fc-match -f '%{family}\n' 'Rubik'
