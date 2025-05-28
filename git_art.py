import argparse
import datetime
import os
import subprocess
import sys
from PIL import Image

# --- Configuration ---
MAX_IMAGE_HEIGHT = 7
MAX_IMAGE_WIDTH = 51
COMMIT_TIME_STR = "12:00:00"  # Arbitrary time for commits
ALPHA_THRESHOLD = 128


# --- Helper Functions ---

def get_existing_commit_dates(repo_path="."):
    """Fetches dates of all existing commits in the repository."""
    try:
        result = subprocess.run(
            ["git", "log", "--pretty=format:%cs"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,  # This will raise CalledProcessError on non-zero exit
        )
        dates = set()
        for line in result.stdout.splitlines():
            if line:
                try:
                    dates.add(datetime.datetime.strptime(line.strip(), "%Y-%m-%d").date())
                except ValueError:
                    print(f"Warning: Could not parse date: {line.strip()}", file=sys.stderr)
        return dates
    except FileNotFoundError:
        print("Error: git command not found. Is Git installed and in your PATH?", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        # Handle common case of an empty repository gracefully
        # stderr for empty repo might contain:
        # "your current branch 'main' does not have any commits yet"
        # "fatal: bad default revision 'HEAD'"
        if "does not have any commits yet" in e.stderr.lower() or \
                "bad default revision 'head'" in e.stderr.lower():
            print("Info: No existing commits found in the repository (repository might be empty).")
            return set()  # No commits means no existing dates
        # Handle case where it's not a git repository at all
        elif "not a git repository" in e.stderr.lower():
            print("Error: This script must be run from within a Git repository.", file=sys.stderr)
            print("Please `cd` into your repository or `git init` a new one.", file=sys.stderr)
            sys.exit(1)
        else:
            # For other unexpected git log errors
            print(f"Error getting git log: {e}", file=sys.stderr)
            print(f"Git stderr: {e.stderr}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        # Catch any other unexpected errors during date fetching
        print(f"An unexpected error occurred while fetching commit dates: {e}", file=sys.stderr)
        sys.exit(1)


def get_first_sunday_of_graph(year):
    """
    Finds the date of the Sunday that starts the first column
    of the GitHub contribution graph for the given year.
    This is the first Sunday on or after January 1st of that year.
    """
    jan_1 = datetime.date(year, 1, 1)
    # weekday(): Monday is 0 and Sunday is 6
    # We want to find days to add to jan_1 to get to a Sunday (6)
    days_to_add = (6 - jan_1.weekday() + 7) % 7
    return jan_1 + datetime.timedelta(days=days_to_add)


def make_git_commit(commit_date, message_prefix, dry_run=True):
    """
    Creates an empty Git commit for the specified date.
    Uses environment variables for GIT_AUTHOR_DATE and GIT_COMMITTER_DATE.
    """
    # Format for --date flag and environment variables (ISO 8601)
    # Example: "2023-05-15T12:00:00"
    datetime_str = f"{commit_date.isoformat()}T{COMMIT_TIME_STR}"
    commit_message = f"{message_prefix}: Pixel on {commit_date.isoformat()}"

    env = os.environ.copy()
    env['GIT_AUTHOR_DATE'] = datetime_str
    env['GIT_COMMITTER_DATE'] = datetime_str

    command = [
        "git", "commit", "--allow-empty",
        "-m", commit_message,
        # The --date flag here is mostly for the author date,
        # env vars are more robust for both author and committer.
        f"--date={datetime_str}"
    ]

    print(f"  {'[DRY RUN] Would commit:' if dry_run else 'Committing:'} {commit_message} (Date: {datetime_str})")

    if not dry_run:
        try:
            subprocess.run(command, env=env, check=True, capture_output=True, text=True)
            print(f"  Successfully committed for {commit_date.isoformat()}")
        except subprocess.CalledProcessError as e:
            print(f"  Error committing for {commit_date.isoformat()}: {e.stderr}", file=sys.stderr)
            return False
    return True


def process_image_and_commit(image_path, year_to_draw_in, commit_message_prefix, dry_run, force_commit):
    """
    Processes the image and creates Git commits.
    """
    try:
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: Image file not found at '{image_path}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error opening image: {e}", file=sys.stderr)
        sys.exit(1)

    if img.height > MAX_IMAGE_HEIGHT:
        print(f"Error: Image height ({img.height}px) exceeds maximum of {MAX_IMAGE_HEIGHT}px.", file=sys.stderr)
        sys.exit(1)
    if img.width > MAX_IMAGE_WIDTH:
        print(f"Error: Image width ({img.width}px) exceeds maximum of {MAX_IMAGE_WIDTH}px.", file=sys.stderr)
        sys.exit(1)

    print(f"Processing image: {image_path} ({img.width}x{img.height}) for year {year_to_draw_in}")

    # Convert image to RGBA to handle transparency and color
    try:
        img = img.convert('RGBA')
    except Exception as e:
        print(
            f"Error converting image to RGBA: {e}. Make sure it's a valid image format (e.g., PNG with transparency).",
            file=sys.stderr)
        sys.exit(1)
    pixels = img.load()

    # Determine the starting date for mapping image pixels
    # This is the Sunday of the *second week* on the GitHub graph for the target year.
    first_sunday_in_graph = get_first_sunday_of_graph(year_to_draw_in)
    print(f"The first Sunday in the graph for {year_to_draw_in} is {first_sunday_in_graph.isoformat()}.")

    if not force_commit:
        print("Fetching existing commit dates...")
        existing_commit_dates = get_existing_commit_dates()
        print(f"Found {len(existing_commit_dates)} dates with existing commits.")
    else:
        existing_commit_dates = set()
        print("Force commit enabled: will not check for existing commits on target dates.")

    commits_to_make = []

    for img_x in range(img.width):  # Image columns (0 to MAX_IMAGE_WIDTH-1)
        for img_y in range(img.height):  # Image rows (0 to MAX_IMAGE_HEIGHT-1)
            r, g, b, a = pixels[img_x, img_y]

            # Check if pixel is black (r=0, g=0, b=0) and sufficiently opaque (alpha > threshold)
            is_target_pixel = (r == 0 and g == 0 and b == 0 and a > ALPHA_THRESHOLD)

            if is_target_pixel:
                commit_date = first_sunday_in_graph + datetime.timedelta(weeks=img_x, days=img_y)

                if commit_date.year > year_to_draw_in and \
                        (commit_date - datetime.date(year_to_draw_in, 12, 25)).days > 10:
                    print(
                        f"  Skipping pixel ({img_x},{img_y}): calculated date {commit_date.isoformat()} is too far into the next year.")
                    continue

                if not force_commit and commit_date in existing_commit_dates:
                    print(f"  Skipping pixel ({img_x},{img_y}): Date {commit_date.isoformat()} already has a commit.")
                    continue

                commits_to_make.append(commit_date)

    if not commits_to_make:
        print("No new commits needed based on the image and existing history.")
        return

    print(f"\nFound {len(commits_to_make)} black pixels requiring commits.")

    if dry_run:
        print("\n--- DRY RUN: The following commits would be made ---")
        for i, date_obj in enumerate(sorted(list(set(commits_to_make)))):  # Sort and unique
            print(f"  {i + 1}. Date: {date_obj.isoformat()}")
        print(f"--- End of DRY RUN ---")
        print(f"\nTo apply these changes, re-run the script with the --execute flag.")
        return

    # Actual commit phase
    print("\n--- Applying Commits ---")
    if not dry_run:
        confirmation = input(f"Proceed with making {len(commits_to_make)} commits? (yes/no): ")
        if confirmation.lower() != 'yes':
            print("Aborted by user.")
            sys.exit(0)

    successful_commits = 0
    for date_obj in sorted(list(set(commits_to_make))):  # Iterate over unique, sorted dates
        if make_git_commit(date_obj, commit_message_prefix, dry_run=False):
            successful_commits += 1
        else:
            print(f"Stopping due to error during commit for {date_obj.isoformat()}. "
                  "Please check your Git repository status.", file=sys.stderr)
            # Optionally, you could try to revert or offer options here
            break  # Stop on first error to avoid cascade

    print(f"\n--- Summary ---")
    print(f"Total pixels to commit: {len(commits_to_make)}")
    print(f"Successfully made {successful_commits} commits.")
    if successful_commits < len(commits_to_make) and not dry_run:
        print("Some commits may have failed. Please review the output.")
    elif successful_commits == len(commits_to_make) and not dry_run:
        print("All scheduled commits processed successfully!")
        print("Don't forget to `git push` if you want to see this on a remote (like GitHub).")


def main():
    parser = argparse.ArgumentParser(
        description="Create Git commits to draw pixel art on your GitHub contribution graph.")
    parser.add_argument("image_path", help="Path to the black-and-white pixel image (max 7px tall, 51px wide).")
    parser.add_argument("year", type=int, help="The year in which to draw the contribution art (e.g., 2023).")
    parser.add_argument("--prefix", default="ArtCommit", help="Prefix for commit messages (default: 'ArtCommit').")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true",
                       help="Simulate and show what would be committed without making changes.")
    group.add_argument("--execute", action="store_true", help="Actually execute the commits (requires confirmation).")
    parser.add_argument("--force", action="store_true",
                        help="Force commits even if a commit already exists on the target date. Use with caution.")

    # Check if inside a git repository before doing anything else
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: This script must be run from within a Git repository.", file=sys.stderr)
        print("Please `cd` into your repository or `git init` a new one.", file=sys.stderr)
        sys.exit(1)

    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        print("Warning: Neither --dry-run nor --execute specified. Defaulting to --dry-run.")
        effective_dry_run = True
    else:
        effective_dry_run = args.dry_run if args.dry_run else not args.execute

    current_year = datetime.date.today().year
    if not (current_year - 10 <= args.year <= current_year + 1):
        print(
            f"Warning: Target year {args.year} is quite far from current year {current_year}. GitHub might not display it as expected on the main profile graph unless it's a recent year or the current year.",
            file=sys.stderr)

    process_image_and_commit(args.image_path, args.year, args.prefix, effective_dry_run, args.force)


if __name__ == "__main__":
    main()
