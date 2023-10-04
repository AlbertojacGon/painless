These scripts create a graphical user interface (GUI) to make different quantitative sensory testing protocols easier to perform.

The protocols use the TCS temperature stimulator from QSTlab; the eVAS and a cold plate from the same manufacturer; an EEG device from Mentalab to record resting state EEG and contact heat evoked potentials (CHEPS).

The evaluation includes pain5 thresholds for heat and cold; temporal summation of pain and conditioned pain modulation; heat and cold pain thresholds; offset analgesia; resting EEG during cold pressor test and CHEPs.

The scripts store the relevant data for each participant in csv files.

The python code is made to be run with anaconda. 

## Overview and .exe generation
### Freezing python environments

In order to make sure that different systems use the same library versions, the libraries that are installed in a python environment can be exported to a requirements file and reused.

To do this with Anaconda, activate the environment to be exported and call `conda env export --file environment.yml`. The last line of `environment.yml` will list the prefix for the environment, this is ignored when using the file and can safely be deleted.

To install an environment using a requirements file, run `conda env create --file environment.yml`.

### Script overview

The folder `script_overview` contains the code for an overview written using PySide6. To run it, call `python script_overview.py`.

When running `script_overview.py` or `script_overview.exe`, the code checks if there is a folder called `painless` (at the same location as `script_overview.py` or `script_overview.exe`). If so, it will generate a button for every executable found inside. If not, the process will exit.

### Generating executables

To generate executables for the script overview and the painless scripts, `pyinstaller` is used together with the `.spec` files found in the repository. `pyinstaller` needs to be called inside of a python environment that has all necessary libraries for the scripts installed (as well as `pyinstaller`) itself.

The environment should ONLY contain necessary libraries. Pyinstaller may bundle libraries that aren't used by any script, thereby slowing down the generation of the exectubles and increasing the size of the resulting distribution folder. For example, if PySide6 is installed in the environment that `pyinstaller` is called in, it may be bundled with the script executables even if they don't use it, possibly increasing the size of the distribution folder by over 100 MB.

Generating the executable for the overview is done by navigating to the `./script_overview/` folder and executing `pyinstaller script_overview.spec`. The executable for the overview can be found inside of `./dist/painless_script_overview/`.

Generating the executables for the painless scripts is done by executing `pyinstaller painless.spec`. After execution, the folder `./dist/painless/` holds the executables for the scripts. This `painless` folder can then be copied to `./script_overview/dist/painless_script_overview/`.

### Adapting the .spec files if they scripts change

It's not necessary to change the `.spec` files unless the file name of a script has changed (or another script is added).

If the file name of a painless script changes (for example if the numbering changes), the change needs to be made inside `painless.spec` as well. To do this, search for the old file name inside of `painless.spec`, there should be exactly two occurences of the file name in the `.spec` file, one with the `.py` extension and one without an extension. Replace these with the new file name.

For example, if `1_Thresholds5.py` will be renamed to `1_Thresholds5_NEW.py`...
* replace `1_Thresholds5.py` in `painless.spec` with `1_Thresholds5_NEW.py` and
* replace `1_Thresholds5` in `painless.spec` with `1_Thresholds5_NEW`

If nothing changes about a script but its name, it's also possible to simply run pyinstaller with the original `painless.spec` and script names and rename the generated `.exe` files instead.