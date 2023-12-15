# pdf_renamer

Tries its best to automatically batch-rename PDF files by extracting the student's name from them using OCR.

## Dependencies

- [Python](https://www.python.org/)
- [pdf2image](https://pypi.org/project/pdf2image/) *(Python)*
- [pytesseract](https://pypi.org/project/pytesseract/) *(Python)*
- [wxPython](https://pypi.org/project/wxPython/) *(Python)*
- [Poppler](https://poppler.freedesktop.org/) *(external; must be in `PATH`; required by pdf2image)*
- [Tesseract](https://tesseract-ocr.github.io/) *(external, must be in `PATH`; required by pytesseract)*

## Setting up

### Windows

1\. Clone this repository:

```pwsh
git clone https://github.com/pedromakaveli/pdf-renamer.git
```

2\. Set up a Python virtual environment:

```pwsh
python -m venv env
```

3\. Activate it:

```pwsh
./env/Scripts/activate.ps1
```

4\. Install the project dependencies:

```pwsh
pip install -r requirements.txt
```

5\. Download and set up external dependencies:

```pwsh
./setup-dependencies-win.ps1
```

Next, you can learn [how to run it](#running).

### Linux

TODO

## Running

### Windows

1\. Temporarily modify your `PATH` environment variable so the app finds Poppler and Tesseract:

```pwsh
$env:PATH = (Resolve-Path ./env/deps/poppler).Path + [IO.Path]::PathSeparator + (Resolve-Path ./env/deps/tesseract).Path + [IO.Path]::PathSeparator + $env:PATH
```

2\. Run the app:

```pwsh
python pdf_renamer.py
```

### Linux

TODO

## Packaging

Note: This section assumes you already have a Python virtual environment set up and activated (see [Setting up](#setting-up)).

1\. Install PyInstaller:

```sh
pip install pyinstaller
```

2\. Build the executable:

```sh
pyinstaller build.spec
```

You will find the executable in the `dist/` directory.
