def process_file(file_path):
    unique_lines = set()  # Use a set to store unique lines

    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Strip whitespace and get the substring from index 25 to 55
                processed_line = line[37:106].strip()
                if processed_line:  # Only add non-empty lines
                    unique_lines.add(processed_line)

        # Count of unique lines
        unique_count = len(unique_lines)
        print(f"Number of unique lines (characters 25 to 55): {unique_count}")

    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    file_path = input("Enter the path to the text file: ")
    process_file(file_path)

