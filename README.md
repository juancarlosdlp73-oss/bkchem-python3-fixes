# BKChem (Python 3 Compatible)

BKChem is a free (as in free software) chemical drawing program. This repository contains a modernized version of BKChem, fully ported to **Python 3**.

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Donate-orange.svg)](https://buymeacoffee.com/vijaymasand)

## Overview

The original BKChem was written in Python 2, which has reached its end-of-life. This project aims to keep this powerful chemical drawing tool alive by migrating the entire codebase to Python 3.10+, ensuring compatibility with modern operating systems and libraries.

## Key Features

- **Chemical Drawing**: Full support for drawing molecules, bonds, atoms, and reactions.
- **Modern Python Support**: Completely refactored to run on Python 3.
- **OASA Integration**: Includes a built-in version of the OASA chemistry library for molecule processing.
- **Rich Export Options**:
  - **Vector Graphics**: SVG, PDF, PostScript (via Cairo).
  - **Raster Graphics**: PNG.
  - **Chemical Formats**: CDML (native), Molfile, CML, SMILES, InChI.
  - **Office Formats**: OpenOffice (ODF) support.
- **Interactive Tools**: Template support, structure validation, and bond alignment tools.
- **Multi-platform**: Runs on Windows, macOS, and Linux (anywhere Python 3 and Tkinter are available).

## Setup Instructions

### Prerequisites

1. **Python 3.10+**: Ensure you have a modern version of Python installed.
2. **Tkinter**: Usually bundled with Python, but on some Linux distributions, you might need to install it separately (e.g., `sudo apt-get install python3-tk`).

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vijaymasand/BKChem_python_3.git
   cd BKChem_python_3
   ```

2. **Install dependencies**:
   It is recommended to use a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## How to Use

To start BKChem, run the launcher script:

```bash
python start_bkchem.py
```

This script automatically sets up the environment and launches the main application window.

## Contributing

Contributions are welcome! If you find a bug related to the Python 3 port or want to improve a feature, please open an issue or submit a pull request.

---
Developed and maintained by [Vijay Masand](https://buymeacoffee.com/vijaymasand), Gaurav Masand, and Krish Masand.
