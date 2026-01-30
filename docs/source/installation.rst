Installation
============

Requirements
------------

- Python 3.12 or higher
- pip or uv package manager

Install from PyPI
-----------------

.. code-block:: bash

   pip install mixref

Or using uv:

.. code-block:: bash

   uv pip install mixref

Development Installation
------------------------

Clone the repository:

.. code-block:: bash

   git clone https://github.com/yourusername/mixref.git
   cd mixref

Install with uv:

.. code-block:: bash

   uv sync --all-extras

This installs mixref with all dependencies including development and documentation tools.

Verify Installation
-------------------

Check that mixref is installed correctly:

.. code-block:: bash

   mixref --version

You should see output like::

   mixref version 0.1.0

System Requirements
-------------------

**Audio Libraries**

mixref uses system audio libraries for file I/O:

- **Linux**: libsndfile (usually pre-installed)
- **macOS**: libsndfile via Homebrew: ``brew install libsndfile``
- **Windows**: Included in Python packages

**Optional: FFmpeg**

For MP3 support, install FFmpeg:

- **Linux**: ``apt-get install ffmpeg``
- **macOS**: ``brew install ffmpeg``
- **Windows**: Download from https://ffmpeg.org
