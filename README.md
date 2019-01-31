mlbz521-recipes
======

Just a few recipes I have created that were not publicly available in other repositories or are unique enough to warrant a second recipe.

## Recipes ##

### Anaconda ###

Parent:  com.github.hansen-m.download.Anaconda

Available recipe types:
  * pkg
    * Variable overrides for version
    * Create a deployable `.pkg` from the `.sh` script installer
    * Default install path is set to:  /Users/Shared/anaconda2 -- adjustable via substitution variable in an override (for use in lab environments)
  * jss


### ARCHICAD ###

Recipes for both the full version download as well as the latest patch.

Available recipe types:
  * download
    * `ARCHICAD.download` will download the latest full installer.
    * `ARCHICAD Patch.download` will download the latest patch.
      * Variable overrides for:  major_version, localization, and release_type
      * Uses custom processor to download
  * pkg
    * `ARCHICAD.pkg`
      * Variable overrides for:  EDUSERIALNUMBER and EDUUSERID
      * Uses multiple custom processor to package
  * jss


### Brother Printer ###

Downloads a Brother Printer Driver, Software Package, Utility, or Firmware specified.  Obviously some packages are compatible with different models, but I haven't been able to think of a way to specify this in the name without it being extremely long.  You will need to specify the model specifically for this to work.  This probably isn't the best way to do it, but it works...

Available recipe types:
  * download
    * Variable overrides for:  MODEL, TYPE_REQUEST, and OS_VERSION
  * pkg
  * jss


### Google Backup and Sync ###

Parent Recipe:  com.github.nstrauss.pkg.BackupandSync

Available recipe types:
  * jss


### Google Drive File Stream ###

Downloads the current release of Google Drive File Stream.

This recipe differs from the recipe available in wardsparadox-recipes as it uses the static URL instead of the DriveFSURLProvider Processor which redirects to mirrored servers and causes the recipe to register false-positive new versions and download them.

Available recipe types:
  * download
  * pkg
  * jss


### Nvivo ###

Parent Recipe:  com.github.joshua-d-miller.download.nvivo
  * Variable overrides for:  MAJOR_VERSION

Available recipe types:
  * pkg
  * jss


### QGIS ###

Downloads the latest specified major_version of QGIS.  Requires python.org Python 3.6 to be pre-installed - other distributions (newer or older) are not supported.  This probably isn't the best way to do it, but it's simple and works for now.

The other publicly available QGIS recipe was no longer functional when the download location moved.  Also added support for different major versions.

Available recipe types:
  * download
    * Variable overrides for:  QGIS_Major_Version
  * pkg
    * Python 3.6+ is a prerequisite before installing QGIS 3 -- the created .pkg will hard fail if Python 3.6+ is not installed.
    * The created .pkg will "uninstall" previous versions of QGIS.
    * The QGIS installer process will also install the necessary Python modules using pip. This requires an internet connection during installation.
  * jss


### Solstice ###

Modified from the original author:  [@joshua-d-miller](https://github.com/autopkg/joshua-d-miller-recipes)
This was removed from his recipe list, but I wanted to use it.  The way Mersive creates the distribution package for Solstice is very wacky.

While this works, it's probably not the best way to do it.  I have plans to revise how this recipe's workflow.

Lately has been causing false positives as well.

Available recipe types:
  * download
  * pkg
  * jss


### Zoom ###

Recipes for both Zoom for IT Admins package and the Zoom Outlook Plugin for macOS.

Available recipe types:
  * download
    * `Zoom-ForIT.download` - Downloads the latest version of Zoom for IT Admins package.  For customizing the package (i.e. SSO, etc)
  * pkg
    * `Zoom-ForIT.pkg` - Variable overrides for: CONFIG_PLIST
      * Configure Zoom for your organization with the CONFIG_PLIST Key
  * jss



## Shared Processors ##

### FileMode ###

This processor essentially runs `chmod` on a file.  Provide the numeric mode for file in octal format.


### TextFileReader ###

This process reads a text file, which can point to a path inside a .dmg which will be mounted, looks for a regex pattern and returns the rest of the line that matched the pattern.


### VersionMajorMinor ###

This processor splits a version string into only the 'Major.Minor' numerals.
  * Expected format is Semantic Versioning
  * Default behavior example: "3.6.5" --> "3.6"


### VersionSubstituter ###

This processor substitutes character(s) in a string by number of occurrences.
  * By default, it splits using a dash only the first item
  * Default behavior example: "3.0.8-2" --> "3.0.8b2"
