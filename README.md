# albumart-dl

Download HQ album cover art from Apple's iTunes.

Automatically downloads the highest resolution, usually up to 3000 x 3000 px. Actual resolutions vary greatly depending on the source material and can go as low as 600 x 600 px.

## Use

```albumart-dl <search-term>```

Example: Download album art for [Frank Zappa's Apostrophe](https://itunes.apple.com/us/album/apostrophe/549280054)

```albumart-dl "Frank Zappa Apostrophe"```

Download album art files to specific folder

```albumart-dl -o <path-to-folder> <search-term>```

Example: Download album art for all of [Brad Mehldau](https://www.bradmehldau.com/)'s albums to a subfolder

```albumart-dl -o ~/Downloads/"Brad Mehldau"/ "Brad Mehldau"```

## Install

macOS: Install albumart-dl using [Homebrew](https://brew.sh/):

```bash
brew tap paulgalow/tap
brew install albumart-dl
```

## Requirements

albumart-dl requires Python 3.6+. External dependencies are [requests](https://github.com/requests/requests) and [yaspin](https://github.com/pavdmyt/yaspin).