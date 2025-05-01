# Copyright (C) 2025  Bambi A. Okugawa
# email: msbam@msbam.space
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


import os
import csv


def combine_files_in_directory(directory="."):
    """
    Finds matching *.obj.1 (CSV) and *.txt files in a directory,
    skips the first 17 rows of the *.obj.1 file, combines the remaining
    *.obj.1 columns with space-separated values from the *.txt file line by line,
    and saves to a new *.obj.1.combined CSV file where each value is in its own column.

    Args:
        directory (str): The path to the directory to process.
                         Defaults to the current directory.
    """
    print(f"Processing files in directory: {os.path.abspath(directory)}")

    # Get a list of all files in the directory
    try:
        files = os.listdir(directory)
    except FileNotFoundError:
        print(f"Error: Directory not found: {directory}")
        return
    except PermissionError:
        print(f"Error: Permission denied to access directory: {directory}")
        return

    obj_files = sorted([f for f in files if f.endswith(".obj.1")])
    txt_files_dict = {f[:-4]: f for f in files if f.endswith(".txt")}  # Store txt files by their base name

    if not obj_files:
        print("No '.obj.1' files found in the directory.")
        return

    processed_count = 0
    rows_to_skip = 17  # Define how many rows to skip

    for obj_filename in obj_files:
        base_name = obj_filename[:-6]  # Remove ".obj.1"
        txt_filename_key = base_name

        if txt_filename_key in txt_files_dict:
            txt_filename = txt_files_dict[txt_filename_key]
            output_filename = os.path.join(directory, f"{base_name}.obj.1.combined")
            obj_filepath = os.path.join(directory, obj_filename)
            txt_filepath = os.path.join(directory, txt_filename)

            print(f"\nMatching files found:")
            print(f"  OBJ file: {obj_filename}")  # Changed label slightly
            print(f"  TXT file: {txt_filename}")
            print(f"  Output file: {os.path.basename(output_filename)}")

            try:
                # Note: 'newline=' is crucial for csv reader/writer
                with open(obj_filepath, 'r', newline='') as obj_file, \
                        open(txt_filepath, 'r') as txt_file, \
                        open(output_filename, 'w', newline='') as outfile:

                    # Use csv.reader for the obj.1 file (handles potential commas/quotes within fields)
                    # Assumes obj.1 is comma-separated or simple enough for default reader.
                    # If obj.1 is space-delimited itself, add delimiter=' ' here.
                    csv_reader = csv.reader(obj_file)

                    # Use csv.writer for the output file
                    # Default delimiter is comma. Change if needed (e.g., delimiter='\t' for tab)
                    csv_writer = csv.writer(outfile)

                    txt_lines = txt_file.readlines()  # Read all text lines at once

                    # --- Skip the first N rows ---
                    print(f"  Skipping first {rows_to_skip} rows of {obj_filename}...")
                    skipped_count = 0
                    try:
                        for _ in range(rows_to_skip):
                            next(csv_reader)  # Read and discard a row from the iterator
                            skipped_count += 1
                    except StopIteration:
                        print(
                            f"  Warning: {obj_filename} has fewer than {rows_to_skip} rows ({skipped_count} found). "
                            f"Proceeding with empty or remaining lines.")
                    # --- End Skipping ---

                    # Process the remaining lines
                    line_num_after_skip = 0  # Index for txt_lines
                    obj_lines_processed = 0
                    for obj_columns in csv_reader:  # obj_columns is now a list of fields from obj.1 line
                        obj_lines_processed += 1
                        if line_num_after_skip < len(txt_lines):
                            # Get corresponding text line and split it by spaces
                            txt_content = txt_lines[line_num_after_skip].strip()  # Strip whitespace/newline
                            txt_columns = txt_content.split()  # Split into a list by spaces

                            # Combine columns from obj file and txt file
                            output_row = obj_columns + txt_columns

                            # Write the combined list as a CSV row
                            csv_writer.writerow(output_row)
                            line_num_after_skip += 1
                        else:
                            # If txt file is shorter than the *remaining* obj.1 lines
                            # Write the obj.1 columns directly as a CSV row
                            csv_writer.writerow(obj_columns)
                            # Uncomment the warning if needed
                            # print(f"  Warning: TXT file '{txt_filename}' ended before OBJ file '{obj_filename}' "
                            #       f"(after skipping). Writing remaining OBJ data only.")

                    # Check if txt file had more lines than the remaining obj lines
                    if line_num_after_skip < len(txt_lines) and obj_lines_processed > 0:
                        # This case means obj file ended first after skipping
                        # Decide if you want to write remaining txt lines or ignore
                        print(f"  Warning: TXT file '{txt_filename}' has more lines ({len(txt_lines)}) "
                              f"than processed lines ({obj_lines_processed}) of OBJ file '{obj_filename}' after "
                              f"skipping."
                              f"Extra TXT lines were not used.")
                    elif line_num_after_skip < len(txt_lines) and obj_lines_processed == 0:
                        # This case means obj file was shorter than rows_to_skip OR empty
                        print(f"  Warning: OBJ file '{obj_filename}' had no data after skipping. "
                              f"TXT file '{txt_filename}' ({len(txt_lines)} lines) was not used.")

                    print(
                        f"Successfully combined into CSV '{os.path.basename(output_filename)}' "
                        f"(processed {obj_lines_processed} data rows from OBJ after skipping {skipped_count})")
                    processed_count += 1

            except FileNotFoundError:
                print(f"Error: One of the files not found during processing: {obj_filename} or {txt_filename}")
            except PermissionError:
                print(
                    f"Error: Permission denied while processing files: {obj_filename}, {txt_filename}, "
                    f"or {output_filename}")
            except csv.Error as e:
                print(f"CSV Error processing {obj_filename} or writing {output_filename}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while processing {obj_filename} and {txt_filename}: {e}")
        else:
            print(f"\nNo matching '.txt' file found for '{obj_filename}' (expected '{base_name}.txt'). Skipping.")

    if processed_count == 0 and obj_files:
        print("\nNo matching file pairs were processed.")
    elif processed_count > 0:
        print(f"\nFinished processing. {processed_count} pair(s) combined into CSV format.")


if __name__ == "__main__":
    # To process files in the current directory:
    combine_files_in_directory()

    # To process files in a specific directory:
    # target_directory = "/path/to/your/files"  # Replace with the actual path
    # if os.path.isdir(target_directory):
    #     combine_files_in_directory(target_directory)
    # else:
    #     print(f"The specified directory does not exist: {target_directory}")
