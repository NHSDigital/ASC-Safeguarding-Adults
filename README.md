# Safeguarding Adults

Safeguarding Adults is a statutory duty for Councils with Adult Social Services Responsibilities in England under the Care Act 2014, in order to safeguard vulnerable adults from abuse or neglect. 

The data is collected directly from these councils in the Safeguarding Adults Collection (SAC) and the outputs produced from the code aim to inform users about aspects of safeguarding activity at national, regional and local level.

## Initial package setup

Run the following command to set up your environment correctly **from the root directory**

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If, while developing this package, you change the installed packages, please update the environment file using

```
pip list --format=freeze > requirements.txt
```

### VSCode specific setup

For Visual Studio Code it is necessary that you change your default interpreter to be the virtual environment you just created `.venv`. To do this use the shortcut `Ctrl-Shift-P`, search for `Python: Select interpreter` and select `.venv` from the list.

## Running the code

Please check that the parameters, including the paths to the input and output files, are correct in `publication_outputs\params.json`.

You can then create the publication (from the publication_outputs directory) using

```
python main.py
```

### Link to the publication

Report: https://digital.nhs.uk/data-and-information/publications/statistical/safeguarding-adults

### Author

Andrew Gallon

Repo Owner Contact Details: andrew.gallon@nhs.net
