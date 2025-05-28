# Git Art Committer 🎨

This Python script is designed for a very specific purpose: to **"draw" pixel art onto your GitHub contribution graph by
creating Git commits in a DEDICATED "Git Art" repository.** It takes a small image (ideally with black pixels on a
transparent background) and translates its black pixels into commits for specific past dates.

**🔴 VERY IMPORTANT: USAGE GUIDELINES 🔴**

* **DEDICATED REPOSITORY ONLY:** This script is **EXCLUSIVELY** intended for use in a **new, empty, or specially
  designated "Git Art" repository** (e.g., a repository named `yourusername/git-art-profile` or similar). The sole
  purpose of such a repository is to house these art commits for display on your GitHub profile.
* **DO NOT USE ON PROJECT REPOSITORIES:** **NEVER** run this script on repositories containing actual project work,
  shared code, collaborative efforts, or any important historical data. Doing so will clutter the commit history with
  non-functional commits and is highly discouraged.
* **PROFILE AESTHETICS:** The goal is to create a visual pattern on your GitHub profile's contribution graph. It serves
  no other development or project purpose.

Think of this as a novelty tool for personalizing your GitHub profile page.

## Features

* Reads a pixel image (up to 7 pixels tall, 51 pixels wide), preferably PNG with transparency.
* Identifies pixels that are black (RGB: 0,0,0) and sufficiently opaque (Alpha > 128 by default).
* Maps these target pixels to specific dates within a chosen year for your Git Art repository.
* Avoids the first and last columns of the GitHub contribution graph, focusing on the middle 51 weeks.
* Checks for existing commits *in the current (art) repository* on target dates to avoid duplication (can be
  overridden).
* Sets both author and committer dates for accurate GitHub display.
* Includes a `--dry-run` mode to preview changes.

## Prerequisites

1. **Python 3.x:** The script is written for Python 3.
2. **Pillow (PIL Fork):** The Python Imaging Library is used for image processing.
    * Install it using pip: `pip install Pillow`
3. **Git:** Git must be installed and accessible in your system's PATH.
4. **A Dedicated Git Art Repository:**
    * Create a new, empty repository (e.g., on GitHub, name it `git-art` or `profile-art`).
    * Clone this repository to your local machine.
    * The script **must be run from the root directory of this dedicated Git Art repository.**

## Image Preparation

1. **Create your art:**
    * A great online tool for creating pixel art with transparency is [**Pixilart.com**](https://www.pixilart.com/). You
      can draw with black and erase to transparency.
    * Other pixel art editors like Aseprite, Piskel, GIMP, or Photoshop can also be used.
2. **Dimensions:**
    * Maximum Height: **7 pixels**
    * Maximum Width: **51 pixels**
3. **Content:**
    * **Target Pixels:** Draw the parts of your image you want to appear as commits using **black color (RGB: 0,0,0)**.
    * **Background/Empty Space:** Make the rest of your image **transparent**.
    * The script will create commits for pixels that are black (R=0, G=0, B=0) and have an alpha value greater than
      128 (i.e., more than 50% opaque). Other pixels will be ignored.
4. **Format:** Save your image as **PNG** to preserve transparency.

## How to Use (In Your Dedicated Git Art Repo)

1. **Save the Script:** Download `git_art.py` and place it in a convenient location (it doesn't need to be inside your
   Git Art repo, but you'll run it *from* there).
2. **Navigate to Your DEDICATED Git Art Repository:**
   ```bash
   cd /path/to/your/git-art-repository
   ```
3. **Run a Dry Run (Recommended First Step):**
   This will show you which dates the script *would* commit to, without making any actual changes *to this art
   repository*.
   ```bash
   python /path/to/git_art.py <your_image_file.png> <year> --dry-run
   ```
   Example:
   ```bash
   python ../scripts/git_art.py my_art.png 2024 --dry-run
   ```
   Review the output carefully.
4. **Execute the Commits (In Your Dedicated Git Art Repo):**
   If the dry run looks correct, run the script with the `--execute` flag. It will ask for an explicit confirmation
   emphasizing its use for art repos.
   ```bash
   python /path/to/git_art.py <your_image_file.png> <year> --execute
   ```
   The script will now create empty commits with backdated timestamps *in your art repository*.
5. **Push Your Git Art Repository to Remote (e.g., GitHub):**
   For the changes to appear on your GitHub contribution graph:
   ```bash
   git push origin main  # Or your default branch name
   ```
   It might take a few minutes for GitHub's contribution graph to update.

### Command-Line Options

* `image_path`: (Required) Path to your pixel image.
* `year`: (Required) The year in which to "draw" the art.
* `--prefix <PREFIX>`: (Optional) A prefix for the commit messages. Default is "ArtCommit".
* `--dry-run`: (Optional) Simulate and show what commits would be made.
* `--execute`: (Optional) Actually perform the commits (requires confirmation).
* `--force`: (Optional) Create commits even if a commit already exists on the target date *in this art repository*.

If neither `--dry-run` nor `--execute` is specified, the script defaults to a dry run.

## ⚠️ Important Considerations & Warnings (Recap) ⚠️

* **DEDICATED ART REPOSITORY ONLY:** This cannot be stressed enough. Use this script *only* in a repository created
  *specifically* for this artistic purpose.
* **NO IMPACT ON OTHER REPOS:** This script only affects the repository it is run from. Your other project repositories
  remain untouched.
* **GitHub Graph Updates:** The GitHub contribution graph may take a few minutes (or sometimes longer) to reflect new
  commits.
* **`--force` Flag:** Use with caution, even in an art repository, as it can create multiple dots on the same day if not
  intended.
* **Large Number of Commits:** This is expected for an art repository.

## Troubleshooting

* **"git command not found"**: Ensure Git is installed and its executable is in your system's PATH.
* **"Not a git repository"**: Make sure you are running the script from the root directory of your **dedicated Git Art
  repository**.
* **"Info: No existing commits found..."**: This is normal if you're running it in a brand new, empty art repository.
* **Image Errors**: Check image path, dimensions, and format (PNG with black on transparent is best).
* **No Commits Made**: Ensure your image has black (RGB 0,0,0) pixels with sufficient opacity (Alpha > 128).

Have fun personalizing your GitHub profile!
