#!/bin/bash

python -m PyInstaller \
  --collect-data engine \
  --collect-data cffi \
  --add-data "$PWD/data:data" \
  --name absengine \
  --version-file version_info.txt \
  --specpath build \
  --clean \
  --noconfirm \
  run.pyw
