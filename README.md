mlbz521-recipes
======

Recipes I have created that were not publicly available in other repositories or are unique enough to warrant a second recipe.

I have a decent number of recipes that use an "offline repository" method.  Basically, these software tiles are not available to be downloaded publicly, normally requiring a login to access the download.  So I have written a custom processor that will allow you to simply drop the vendor provided "package", whatever format it may be, into a specifically named folder structure, whether local to the system running autopkg or a remote host that is mounted before run, and the recipe will be able to determine which version of the application to "download" even if multiple are available.  For more details, review the Shared Processors README linked below.


## Shared Processors ##

A separate README is available for my [shared processors](https://github.com/autopkg/MLBZ521-recipes/blob/master/Shared%20Processors/ReadMe.md).


## Recipes ##

### Amazon Corretto OpenJDK ###

Amazon Corretto is an OpenJDK alternative that is maintained and supported by Amazon.  These recipes allow you to specify which version you'd want; currently 8 and 11 are available from Amazon.

Optionally, this package will pull out the JVM Version which can be used with a Smart Group pointing to an extension attribute to determine latest version.  I have an EA available that can be used in conjunction with this recipe.

Available recipe types:
  * download
    * Variable overrides for:  JDK_MAJOR_VERSION
    * Uses custom processor to download
  * pkg
  * jss
    * Use the EXTENSION_ATTRIBUTE override variable to use your current EA.


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
    * `ARCHICAD.download` will "download" from a offline repository
    * `ARCHICAD Patch.download` will download the latest patch
      * Variable overrides for:  major_version, localization, and release_type
      * Uses custom processor to download
  * pkg
    * `ARCHICAD.pkg`
      * Variable overrides for:  EDUSERIALNUMBER and EDUUSERID
    * Multiple custom processors used to create packages
  * jss


### AutoCAD for Mac ###

Recipes for both base and patch installers are available.  Download recipe for the base full version expects the installer is available in an "offline repository".  Patch download recipe will download the the latest patch from AutoDesk for the supplied major version.

Available recipe types:
  * download
    * `AutoCAD.download` will "download" from a offline repository
    * `AutoCAD Patch.download` will download the latest patch.
      * Variable overrides for:  major_version
      * Uses custom processor to obtain download url
  * pkg
  * jss


### Bomgar ###

Recipes for both the Representative Console and Jump Client are available.  Download recipes expect the installers are available in an "offline repository".

Available recipe types:
  * download
    * recipes will "download" from a offline repository
    * `BomgarConsole.download`
      * Variable overrides for:  CODE_SIGN_IDENTIFIER
  * pkg
  * jss


### Brother Print Drivers ###

Downloads a Brother Printer Driver, Software Package, Utility, or Firmware specified.  Obviously some packages are compatible with different models, but I haven't been able to think of a way to specify this in the name without it being extremely long.  You will need to specify the model specifically for this to work.  This probably isn't the best way to do it, but it works...

Available recipe types:
  * download
    * Variable overrides for:  MODEL, TYPE_REQUEST, and OS_VERSION
  * pkg
  * jss


### Cisco Jabber ###

Download recipe expects the installer is available in an "offline repository".

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg
  * jss


### Cisco Umbrella Roaming Client ###

Downloads the latest release of Cisco Umbrella Roaming Client.

Available recipe types:
  * download
  * pkg
  * jss


### CrowdStrike Falcon ###

Two recipes "types" are available to choice from for CrowdStrike Falcon.
  * The original "offline" recipe requires the installer is available in an "offline repository"
  * A recipe that downloads the agent via CrowdStrike's API

Shortly after creating the offline recipe format that I'm using for other recipes, CrowdStrike completed a feature request we had to make the download available via their API.  I'm leaving the offline recipe format available incase you don't have access to the API or prefer to not use it.

Available recipe types:
  * download
    * `CrowdStrikeFalconOffline.download`
      * will "download" from a offline repository
    * `CrowdStrikeFalcon.download`
      * Variable overrides for:  CLIENT_ID, CLIENT_SECRET, POLICY_ID
  * pkg
    * Variable override for:  LICENSE_ID
  * jss


### CXone Softphone ###

Download recipe expects the installer is available in an "offline repository".

Available recipe types:
  * download
    * will "download" from a offline repository
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


### Jamf Pro Tools ###

Download recipe expects the installer is available in an "offline repository".  This is designed for our "Site Admins" and doesn't include the `Jamf Admin.app` nor `Jamf Imaging.app`.

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg
  * jss


### JMP/JMP Pro ###

Download recipe expects the installer is available in an "offline repository".  The download and pkg recipes can be used for either JMP or JMP Pro and a unique jss recipe is available for each.

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg
  * jss


### Maple ###

Recipes for both base and patch installers are available.  Download recipe for the base full version expects the installer is available in an "offline repository".  Patch download recipe will download the the latest patch from Maple for the supplied major version.

Available recipe types:
  * download
    * `Maple.download` will "download" from a offline repository
    * `Maple Patch.download` will download the latest patch.
      * Variable overrides for:  major_version
      * Uses custom processor to obtain download url
  * pkg
  * jss


### Mathematica ###

Download recipe expects the installer is available in an "offline repository".

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg
  * jss


### Matlab ###

Download recipe expects the installer is available in an "offline repository".

I license most software separately in environment and do not use the built licensePath key.  If you want to use the built-in licensePath Key, you'll want to fork this recipe more than likely.

If you want to customize the products that are installed, a copy of an original, albeit old, installer_input.txt is available in the recipe directory.  I've seen people are unable to locate it as it's not included in newer versions even though the documentation points to it.

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg
    * includes a preinstall script to uninstall previous versions
    * Variable overrides for:  INSTALL_INPUT
  		* As the name suggests, this the "installer.input" that allows you to customize the install of Matlab.  The available parameters are included in the recipe; customize for your environment.
  * jss


### Mendeley ###

Parent Recipe:  com.github.hansen-m.pkg.Mendeley

Available recipe types:
  * jss


### MirrorOp ###

Parent Recipe:  com.github.moofit-recipes.pkg.MirrorOp

Available recipe types:
  * jss


### Nvivo ###

Parent Recipe:  com.github.jazzace.pkg.NVivo

Available recipe types:
  * ~~pkg~~
    * My pkg recipe will be deprecated as I'm using jazzace's pkg recipe now
  * jss


### Pharos Popup Client ###

Parent Recipe:  com.github.asemak.pkg.popup

Available recipe types:
  * jss


### PhET Lab Simulations ###

Downloads the latest version of a specified PhET Lab Simulation and creates a pseudo macOS application wrapper around the .jar Java executable.  Which allows it to be fully inventoried into Jamf Pro like a standard app.  I did my best to create an 'App' that looks half was decent with icons and what not...  Not a graphics person, so that could be improved.

Currently supported:
  * Balloons and Buoyancy

Additional simulation can be added, only what has been requested in my organization, have I added so far.

Available recipe types:
  * download
    * Variable overrides for:  LAB_SIM
    * Uses custom processor to obtain download url and set other environment information used by child recipes
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


### RealVNC ###

Parent Recipe:  com.github.foigus.download.RealVNCViewer

The vendor's CFBundleShortVersionString format is '6.20.113 (r42303)' which isn't accepted by pkgbuild when building the package.  

So I wrote a hacky solution to supply an accept version string to pkgbuild and still retain the "vendor version" that can be used for naming and use within Jamf Pro (Smart Groups, etc).

Available recipe types:
  * pkg
  * jss


### Respondus Lockdown Browser ###

Parent Recipe:  com.github.aysiu.download.LockDownBrowserLab

The download recipe requires you to set your Institution ID and Lab Hash.

Because Respondus does silly things by expecting the licencing information in the file name, the pkg recipe performs "package inception" so that the package name visible in Jamf Pro uses a standard naming convention.

Available recipe types:
  * pkg
  * jss


### Safe Exam Browser ###

Parent Recipe:  com.github.aanklewicz.pkg.SEB

Available recipe types:
  * jss


### Screencast-O-Matic ###

The Screencast-O-Matic application (in my opinion) is poorly designed.  The user has to own .app for them to be able to launch it.  So....that said...That means only one user on any system can actually use this app.  I'm trying to get in contact them to figure this out.  This recipe will account for that (i.e. it changes the permissions on the app to the currently logged in user)...so I highly recommend this is used as a Self Service deployment -- if you require it and their is no user logged it, it will fail, or produce undesirable results.

Available recipe types:
  * download
  * pkg
  * jss


### Solstice ###

Modified from the original author:  [@joshua-d-miller](https://github.com/autopkg/joshua-d-miller-recipes)
This was removed from his recipe list, but I wanted to use it.  The way Mersive creates the distribution package for Solstice is very wacky (a zip, with an .app that creates another .app).

This is v2 of my hack-ish way of being able to deploy this application, but it works. ¯\\_(ツ)_/¯

v1 would do all the work to get the final .app on the client machine, which wasn't exactly desired, while this version will get the final .app on the system running autopkg.
\*\*\*Note this likely requires a user to be logged in when this is ran, as the stupid Solstice bootstrap .app, creates the final .app on the desktop of the user that ran it.
It's dumb, I know.  I've contacted Mersive about it and they claim they're looking at improving macOS deployment in the future, but no ETA.

Hopefully this overhaul will help with the false positives.

Available recipe types:
  * download
  * pkg
  * jss


### SPSS Statistics ###

Recipes for both base and patch installers are available.  Download recipe expects the installer is available in an "offline repository".  The download recipe can be used for either the base or patch installers and unique pkg and jss recipes are needed for additional steps.

In my environment my base package installs to a custom environment (instead of five folders deep), just in case someone has installed SPSS in a different location somehow, in the Patch.pkg recipe, the postinstall script that "handles the upgrade" searches the `/Applications` folder for the version of SPSS being upgraded and will inject the path into the install.properties file so it does not need to be specified in the INSTALL_PROPERTIES override variable below, which is described below.

Available recipe types:
  * download
    * "download" from a offline repository
  * pkg
    * base installer recipe includes a preinstall script to uninstall previous versions
    * Variable overrides for:
      * INSTALL_PROPERTIES
  		  * As the name suggests, this the "installer.properties" that allows you to customize the install of SPSS.  The available parameters are included; customize for your environment.
      * INSTALL_JDK_CLI
        * A JDK is required to install SPSS silently; if one is not installed, you can provide a command line command to acquire one through any method that is support in your environment
  * jss


### Xerox Print Drivers ###

Downloads the latest Xerox package based on the override-able parameters:  model, download type, and OS Version.  Examples are:
  * "macOS Common Driver Installer" (default)
  * "ICA Scan USB Driver"
  * "IMAC CA Scan USB Driver"
  * "TWAIN Scan Driver"

Tested both "macOS Common Driver Installer" and "ICA Scan USB Driver" to download and package successfully.

The "macOS Common Driver Installer" seems to support a large number of printers through my poking.  So the recipes end up labeling the produced package as such and not for a "unique" printer model (this is a change after the last update).

Available recipe types:
  * download
    * Variable overrides for:  model, downloadType, and osVersion
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

