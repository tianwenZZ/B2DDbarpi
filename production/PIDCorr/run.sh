#!/bin/bash
# firstly, need to set up the environment manually: lb-run -c best Urania/v10r1 bash
python B2DDpi_pidcorr.py > B2DDpi_pidcorr.log 2>&1 &
python B2D0D0pi2b2b_pidcorr.py > B2D0D0pi2b2b_pidcorr.log 2>&1 &
python B2DstDdPi2b_pidcorr.py > B2DstDdPi2b_pidcorr.log 2>&1 &
python B2DstDstpi2b2b_pidcorr.py > B2DstDstpi2b2b_pidcorr.log 2>&1 &
