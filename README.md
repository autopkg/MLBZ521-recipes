mlbz521-recipes
======

Recipes I have created that were not publicly available in other repositories or are unique enough to warrant a second recipe (very rare or unintentionally created around the same time or before being merged into the autopkg org).

I have a number of recipes that use an "offline repository" method.  Basically, these software titles are not available to be downloaded publicly, normally requiring a login to access the download.  So I have written a custom processor that will allow you to simply drop the vendor provided "package", in the format they provide, into a specifically named folder structure, whether local to the system running autopkg or a remote host that will be mounted, and the recipe will be able to determine which version of the application to "download" even if multiple are available.  For more details, review the Shared Processors README linked below.


#### **DEPRECATION NOTICE** ####

Please note:  All `.jss` recipes have been deprecated and will no longer receive updates due to the sunset of JSSImporter as it will stop working in a future version of Jamf Pro ([Details](https://grahamrpugh.com/2022/02/16/jssimporter-jamf-pro-api-token-auth.html)).  As most of the community already has, I am moving to JamfUploader.  Currently, I do not plan to create public `.jamf` recipes as my use of JamfUploader very likely will not follow normal community practice due to my use of [PkgBot](https://github.com/MLBZ521/PkgBot).


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
  * EA template is available for use in Jamf Pro
    * Use the EXTENSION_ATTRIBUTE override variable to use your current EA.


### Anaconda ###

Parent:  com.github.hansen-m.download.Anaconda

Available recipe types:
  * pkg
    * Variable overrides for version
    * Create a deployable `.pkg` from the `.sh` script installer
    * Default install path is set to:  /Users/Shared/anaconda3 -- adjustable via substitution variable in an override (for use in lab environments)


### Android Studio SDK CLI Tools ###

This can be used with or separately from Android Studio, but the recipe will assume usage with Android Studio.

To provide additional configuration options, my [Manage-AndroidSDKCMDLineTools.sh script](https://github.com/MLBZ521/MacAdmin/blob/master/Software/Manage-AndroidSDKCMDLineTools.sh) is available.
  * Great for use in multi-user, lab, and non-admin environments
  * It can perform the following actions:
    * Initial setup/configuration
      * Set environment variables via a LaunchAgent that the GUI Android Studio application can utilize
      * Allow an (almost seamless) first run experience
        * The first run Android Studio Setup Wizard will run, but the environment variables will be used to pre-configure all settings (the JDK and Android versions would need to be pre-configured in the jdk.table.xml to completely skip the first run wizard)
        * The required minimum SDK components must be installed before first launch to support this
      * Accept CLI Tool licenses
    * Configure Android Studio (GUI) updates settings
    * Install SDK Components
    * Perform updates to installed components
  
Available recipe types:
  * download
  * pkg
    * Override variable available:
      * SHARED_PATH
        * This is the path to where you want to "install" the sdk (`/path/to/sdk/location/`)
          * e.g. Default install path is set to:  `/Users/Shared/Android`
            * Great for use in multi-user, lab, and non-admin environments


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


### AutoCAD for Mac ###

Recipes for both base and patch installers are available.  Download recipe for the base full version expects the installer is available in an "offline repository".  Patch download recipe will download the the latest patch from AutoDesk for the supplied major version.

There is a **LEGACY** version of the recipes for the 2020 older installer type.

Available recipe types:
  * download
    * `AutoCAD.download` will "download" from a offline repository
    * `AutoCAD Patch.download` will download the latest patch.
      * Variable overrides for:  major_version
      * Uses custom processor to obtain download url
  * pkg


### Bomgar ###

Recipes for both the Representative Console and Jump Client are available.  Download recipes expect the installers are available in an "offline repository".

Available recipe types:
  * download
    * recipes will "download" from a offline repository
    * `BomgarConsole.download`
      * Variable overrides for:  CODE_SIGN_IDENTIFIER
  * pkg


### Brother Print Drivers ###

Downloads a Brother Printer Driver, Software Package, Utility, or Firmware specified.  Obviously some packages are compatible with different models, but I haven't been able to think of a way to specify this in the name without it being extremely long.  You will need to specify the model specifically for this to work.  This probably isn't the best way to do it, but it works...

Available recipe types:
  * download
    * Variable overrides for:  MODEL, TYPE_REQUEST, and OS_VERSION
  * pkg


### Canon Print Driver ###

Downloads a Canon Print Driver package based on the override-able parameters.  The recipe was originally written to download the Recommended driver for Canon's imageRUNNER class, but has been updated to also download drivers for Canon's Multi-Function Printers as well.

The download recipe requires the [Selenium Library](https://www.selenium.dev/documentation/) and requires a browser driver to be supplied.  See the [CanonPrintDriverURLProvider](https://github.com/autopkg/MLBZ521-recipes/blob/master/Shared%20Processors/ReadMe.md#CanonPrintDriverURLProvider) section in my Shared Processors README for more info.

Available recipe types:
  * download
    * Variable overrides for:
      * model:
        * description:  The official model name of the Canon Printer to search for
        * example:  'imageRUNNER ADVANCE C7565i III'
      * download_type:
        * description:  What to download from the available list.  Options:
          * Recommended (Default)
            * Will download _whatever_ option is in the "Recommended Driver(s)" section
              * _Note_:  the "Recommended" driver may not be the *_latest_* driver
          * UFRII
            * will download the latest UFRII optional driver
          * PS
            * will download the latest PS optional driver
          * FAX
            * will download the latest FAX optional driver
          * PPD
            * will download the latest PPD optional driver
            * Note:  The `com.github.mlbz521.pkg.CanonPrintDriver` recipe does not support the PPD file type
      * os_version
        * description:  The OS version to search against
        * required:  False
        * options:  
          * macOS Monterey v12.0:  MACOS_12 (Default)
          * macOS Big Sur v11.0:  MACOS_11_0
          * macOS Catalina v10.15:  MACOS_10_15
          * macOS Mojave v10.14:  MACOS_10_14
          * macOS High Sierra v10.13:  MACOS_10_13
          - (older OS Versions, including Windows and Linux should be supported by the processor as well, see my Shared Processors README)
  * pkg


### Cisco Jabber ###

Download recipe expects the installer is available in an "offline repository".

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg


### Composer ###

Download recipe expects the installer is available in an "offline repository".  This is designed for our "Site Admins".

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg


### CoreShell Helper ###

Downloads the latest release of the CoreShell Helper.

Please note:  if CoreShell Helper has been installed from the vendor’s install .app, this will not update that previous install.  This is due to the fact that the vendor's installation .app installs the bits into the currently logged in users' home directory (so you can’t deploy it without a user logged in).  The autopkg created .pkg will install the bits into non-user space, so it would/could apply to any/all users on a system.

Available recipe types:
  * download
  * pkg


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
      * Input Variable:
        * client_id:
            * required:  True
            * description:  CrowdStrike API Client ID. This API account will need a minimum of Read: Sensor download, and Read: Sensor update policies access
        * client_secret:
            * required:  True
            * description:  CrowdStrike API Client Secret
        * policy_id:
            * required:  True
            * description:  CrowdStrike Policy ID to get the assigned Sensor version. This can be obtained from the end of the URL when viewing the policy details page
        * api_region_url:
            * required:  False
            * default:  `https://api.crowdstrike.com`
            * description:  CrowdStrike Region your instance is associated with
  * pkg
    * Input Variable for:  LICENSE_ID


### CXone Softphone ###

Download recipe expects the installer is available in an "offline repository".

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg


### Cytoscape ###

Downloads the latest release of Cytoscape.

Java 11 is _REQUIRED_ to install Cytoscape.  If Java 11 is not pre-installed, the Cytoscape installer process _should_ download and install Java itself.

Be aware the installation .app is NOT SIGNED.

Available recipe types:
  * download
  * pkg


### iManage Work ###

Download recipe expects the installer is available in an "offline repository".

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg


### JMP/JMP Pro ###

Download recipe expects the installer is available in an "offline repository".  The download and pkg recipes can be used for either JMP or JMP Pro.

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg


### Maple ###

Recipes for both base and patch installers are available.  Download recipe for the base full version expects the installer is available in an "offline repository".  Patch download recipe will download the the latest patch from Maple for the supplied major version.

Available recipe types:
  * download
    * `Maple.download` will "download" from a offline repository
    * `Maple Patch.download` will download the latest patch for the supplied major version
      * Variable overrides for:  major_version
      * Uses custom processor to obtain download url
  * pkg


### Mathematica ###

Download recipe expects the installer is available in an "offline repository".

Available recipe types:
  * download
    * will "download" from a offline repository
  * pkg


### Matlab ###

Recipes for both base and patch installers are available.  Download recipe expects the installer is available in an "offline repository".

For the Patch recipe, I attempted to reverse the built-in update mechanism, however, have not yet determined how the process works.  So offline recipes will have to be used for now.

I now have _two_ different recipes for the base installer, each depend on which source you use.
  * ISO Image (aka Offline Media)
    * This method was the "original" method the recipe used, but it has not worked since 2019b, I'm leaving it here in case MathWorks ever decides to resolve the issue.
    * I've opened two ticket with MathWorks, back in 2020 and again in 2022, both times they've acknowledge and confirmed the issue, but provided no indication that it will be fixed
  * Download Only (download only, but do not install)
    * This recipe version uses the offline media created with the "MathWorks Installer" described in [this guide](https://www.mathworks.com/matlabcentral/answers/259632-how-can-i-get-matlab-installation-files-for-use-on-an-offline-machine).
    * This is the "new" method that the non-specified recipe will be using

I license most software separately in my environment and do not use the installer.input's `licensePath` key.  If you want to use this key, you'll need to fork this recipe and adjust the postinstall script.

If you want to customize the products that are installed, a copy of an original, albeit old, `installer_input.txt` is available in the recipe directory.  I've seen people are unable to locate it as it's not included in newer versions even though the documentation points to it.

Available recipe types:
  * download
    * Will "download" from a offline repository
    * Two versions
      * (non-specified)
      * ISO
  * pkg
    * Variable override for:  INSTALL_INPUT
      * As the name suggests, this the "installer.input" that allows you to customize the install of Matlab.  The available parameters are included in the sample `installer_input.txt` file; customize for your environment.
    * Two versions
      * (non-specified)
      * ISO


### MiKTeX ###

Downloads the latest release of MiKTeX.

Available recipe types:
  * download
  * pkg


### MySQL Community Server ###

Parent Recipe:  com.github.gerardkok.download.MySQLCommunityServer

Available recipe types:
  * pkg


### NoMAD Login AD ###

#### **DEPRECATED** ####

Deprecating this recipe as Jamf has EOL'd NoMAD.

~~Parent Recipe:  com.github.peetinc.download.NoMADLoginAD~~

~~The pkg recipe differs from the recipe available in nstrauss-recipes in that it downloads NoLoAD from source and performs no customizations.~~

~~Available recipe types:~~
  * ~~pkg~~


### NVivo ###

Parent Recipe:  com.github.dataJAR-recipes.download.NVivo 14

Available recipe types:
  * pkg


### Pharos Popup Client ###

Added `download` and `pkg` recipes originally created by @asemak (asemak-recipes) after his repo was deprecated and archived.

Available recipe types:
  * download
  * pkg


### Python ###

Downloads the latest or specified version of Python.  Stable builds are checked first, then pre-release builds.

Options:
  * To download the latest version of Python, use (this is REGEX):  \d+
  * To download a specific minor version, for example, you can use:  "10" or "3.10"
  * You can download a pre-release build if the minor version does not yet have a stable release
  * Technically, you can even download Python2 if you wanted; e.g.:  "2.7"

The recipe will also set the env variable `version_major_minor` that can be used in child recipes.

This recipe defers from the Python3 recipe in scriptingosx-recipes repo by allowing the version to be specified.

Available recipe types:
  * download
    * Variable overrides for:  MATCH_VERSION
      * Default:  `\d+`
  * pkg


### QGIS ###

Downloads the latest specified major_version of QGIS.

The other publicly available QGIS recipe was no longer functional when the download location moved.  Also added support for different major versions.

Available recipe types:
  * download
    * Variable overrides for:  QGIS_Major_Version
  * pkg
    * The created .pkg will "uninstall" previous versions of QGIS.


### RealVNC ###

Parent Recipe:  com.github.foigus.download.RealVNCViewer

The vendor's CFBundleShortVersionString format is '6.20.113 (r42303)' which isn't accepted by pkgbuild when building the package.  

So I wrote a hacky solution to supply an accept version string to pkgbuild and still retain the "vendor version" that can be used for naming and use within Jamf Pro (Smart Groups, etc).

Available recipe types:
  * pkg


### Respondus Lockdown Browser ###

Parent Recipe:  com.github.nstrauss.download.RespondusLockDownBrowser

Downloads and packages the latest version Respondus' LockDown Browser and configures the install package for the Lab Edition.

The download recipe requires you to set your Institution ID and this recipe requires your Lab Hash.

Because Respondus does silly things by expecting the licensing information in the file name, the pkg recipe performs "package inception" so that the package name visible in Jamf Pro uses a standard naming convention and doesn't contain the licensing information.

My pkg recipe differs from nstrauss-recipes's pkg recipe by not installing the LDB on the AutoPkg runner/system and simply performing the above steps to get the desired results (tl/dr:  less steps, similar result).

Available recipe types:
  * pkg


### Ricoh Print Driver ###

Downloads the latest Ricoh Driver package based on the override-able parameters.  See the 

The download recipe requires the [Selenium Library](https://www.selenium.dev/documentation/) and requires a browser driver to be supplied.  See the [RicohPrintDriverProcessor](https://github.com/autopkg/MLBZ521-recipes/blob/master/Shared%20Processors/ReadMe.md#ricohprintdriverprocessor) section in my Shared Processors README for more info.

Available recipe types:
  * download
    * Variable overrides for:
      * model:
        * description:  The official model name of the Ricoh Printer to search for
        * example:  'Aficio SP C830DN'
      * os_version
        * description:  The OS version to search against
        * required:  False
        * options:  
          * Big Sur
          * Catalina
          * Mojave
          * High Sierra
          * Sierra
            - (Windows and Linux could be supported by the processor with some tweaks, see my Shared Processors README)
  * pkg


### Set.A.Light 3D ###

Downloads the latest release of Set.A.Light 3D from Elixxier.  I have not attempted to license this in an programmatic way yet, so the result will need to be licensed manually.

Available recipe types:
  * download
  * pkg


### Solstice ###

Parent Recipe:  com.github.joshua-d-miller.download.solsticeclient

Available recipe types:
  * pkg


### SPSS Statistics ###

Recipes for both base and patch installers are available.  Download recipe expects the installer is available in an "offline repository".  The download recipe can be used for either the base or patch installers and a unique pkg recipe is needed for additional steps.

There is a **LEGACY** version of the recipes for the v26 and older installer type.

(This _only_ applies to the **LEGACY** recipes) In my environment my base package installs to a custom environment (instead of five folders deep), just in case someone has installed SPSS in a different location somehow, in the Patch.pkg recipe, the postinstall script that "handles the upgrade" searches the `/Applications` folder for the version of SPSS being upgraded and will inject the path into the install.properties file so it does not need to be specified in the INSTALL_PROPERTIES override variable below, which is described below.

Available recipe types:
  * download
    * "download" from a offline repository
  * pkg 
    * (**LEGACY**) Variable overrides for:
      * INSTALL_PROPERTIES
        * As the name suggests, this the "installer.properties" that allows you to customize the install of SPSS.  The available parameters are included; customize for your environment.
      * INSTALL_JDK_CLI
        * A JDK is required to install SPSS silently; if one is not installed, you can provide a command line command to acquire one through any method that is support in your environment


### Tableau Public ###

Parent Recipe:  com.github.foigus.download.tableau-public

Available recipe types:
  * pkg


### VOSviewer ###

Downloads the latest release of VOSviewer.

Java is *REQUIRED* to open VOSviewer.  Amazon's Corretto JDK is not compatible in my testing.

Be aware the .app is NOT SIGNED.

Available recipe types:
  * download
  * pkg


### Xcode Command Line Tools ###

Downloads the Xcode Command Line Tools from the Apple dev portal, creates a .pkg, and uploads it to the JPS.  Uses Nick McSpadden's "xcode.downloader" recipe.

The Policy will be named "%NAME% %Major Version%", e.g. "Xcode Command Line Tools 12"

Important Override Variables:
  * You must override APPLE_ID and ( PASSWORD_FILE or PASSWORD )
  * BETA must either be empty for stable releases or set to "Beta" in order to match Xcode betas

See [Nick McSpadden's README](https://github.com/autopkg/nmcspadden-recipes/tree/master/Xcode) for more information.

Parent Recipes:
  * com.github.nmcspadden.download.xcode

Available recipe types:
  * pkg


### Xerox Print Drivers ###

Downloads the latest Xerox package based on the override-able parameters:  model, download type, and OS Version.  Examples are:
  * "macOS Print and Scan Driver Installer" (default)
  * "ICA Scan USB Driver"
  * "IMAC CA Scan USB Driver"
  * "TWAIN Scan Driver"

Tested both "macOS Print and Scan Driver Installer" and "ICA Scan USB Driver" to download and package successfully.

The "macOS Print and Scan Driver Installer" seems to support a large number of printers through my poking.  So the recipes end up labeling the produced package as such and not for a "unique" printer model (this is a change after the last update).  If you end up choosing a different download type, I would recommend changing the NAME input variable to differentiate from other download types, if you use multiple.

Available recipe types:
  * download
    * Variable overrides for:  model, downloadType, and osVersion
  * pkg


### Zoom for IT ###

Downloads the latest version of Zoom for IT Admins package.  This version of the Zoom installer is for customizing the package at install (e.g. SSO, etc.).

Available recipe types:
  * download
  * pkg
    * Variable overrides for: 
      * CONFIG_PLIST
        * Configure Zoom for your organization with the CONFIG_PLIST Key


### Zoom Outlook Plugin ###

Recipes for the Zoom Outlook Plugin for macOS.

Available recipe types:
  * download
  * pkg
