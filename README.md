# pnlcalcgtk

A simple profit and loss calculator.
Best used to calculate potential outcome of trades on futures markets where leverage is used.

Made to get familiar with GKT4 and pygoobject.

## Flatpak

### Build

flatpak-builder --force-clean build-dir com.github.peerchemist.pnlcalc.yaml

### Install

flatpak-builder --user --install --force-clean build-dir com.github.peerchemist.pnlcalc.yaml