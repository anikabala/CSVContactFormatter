import pandas as pd
import os
import re
import glob
import csv

def find_csv_file(directory):
    # Find the first CSV file in the specified directory
    csv_files = glob.glob(os.path.join(directory, "*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in the specified directory.")
    return csv_files[0]  # Return the first CSV file found

def format_csv(input_file, output_file, input_file_name):
    # Custom CSV reader to handle extra fields
    rows = []
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)  # Skip the header row
        for row in reader:
            if len(row) > 14:
                combined_contact = ' '.join(row[12:])  # Combine all fields after the 12th field
                row[12] = combined_contact
                rows.append(row[:14])  # Trim the row back to the first 14 fields
            else:
                rows.append(row)
    
    df = pd.DataFrame(rows, columns=headers[:14])  # Trim the headers to match the processed rows
    # Process the DataFrame as before
    original_file = df.copy()  # Create a copy of the original DataFrame

    def extract_contact_info(contact_str):
        # Extract the first name (everything before the first "Email:")
        name_match = re.match(r"^(.*?)(?=\s*Email:)", contact_str)
        name = name_match.group(0).strip() if name_match else ""

        # Extract the first email (assuming it follows the first "Email:")
        email_match = re.search(r"Email:([^\s,]+)", contact_str)
        email = email_match.group(1).strip() if email_match else ""

        # Extract the first phone number (assuming it follows the first "C:")
        phone_match = re.search(r"C:([^\s,]+)", contact_str)
        phone = phone_match.group(1).strip() if phone_match else ""

        return name, email, phone


    # Rename columns
    df.rename(columns={
        'Course': 'First Name',
        'Room': 'Middle Name',
        'Term(s)': 'Last Name',
        'Last Name': 'Phonetic First Name',
        'First Name': 'Phonetic Middle Name',
        'Middle Name': 'Phonetic Last Name',
        'Suffix': 'Name Prefix',
        'Alias': 'Name Suffix',
        'Gender': 'Nickname',
        'Grade': 'File As',
        'Start Date': 'Organization Name',
        'End Date': 'Organization Title',
        'Guardian Contact(1)': 'Organization Department',
        'Guardian Contact(2)': 'Birthday'
    }, inplace=True)

    # Add new columns or update existing ones based on the original file
    for index, row in df.iterrows():
        notes = ""
        # extract guardian contact info
        # Adjust column name as needed
        guardian_contact = original_file.at[index, 'Guardian Contact(1)']
        name, email, phone = extract_contact_info(guardian_contact)

        # Check if Guardian Contact(2) exists and process it
        if 'Guardian Contact(2)' in original_file.columns:
            guardian_contact2 = original_file.at[index, 'Guardian Contact(2)']
            if pd.notna(guardian_contact2):  # Check if it's not empty or NaN
                name2, email2, phone2 = extract_contact_info(guardian_contact2)
                notes += f"; {name2}"  # Append the second guardian's name to Notes
        # set the 'First Name' to 'First Name' + first initial of 'Last Name' + " Parent"

        # Use either the Alias or First Name depending on the float check
        first_name = original_file.at[index, 'Alias'].strip()
        if not first_name:  # If Alias is empty, use the First Name
            first_name = original_file.at[index, 'First Name'].strip()

        # Get the first initial of 'Last Name'
        last_initial = original_file.at[index, 'Last Name'][0]

        # set columns
        df.at[index, 'First Name'] = f"{first_name} {last_initial}.'s Guardian"
        df.at[index, 'Middle Name'] = None
        df.at[index, 'Last Name'] = None
        df.at[index, 'Phonetic First Name'] = None  # Example logic
        df.at[index, 'Phonetic Middle Name'] = None  # Example logic
        df.at[index, 'Phonetic Last Name'] = None  # Example logic
        df.at[index, 'Name Prefix'] = None
        df.at[index, 'Name Suffix'] = None
        df.at[index, 'Nickname'] = None
        df.at[index, 'File As'] = None
        df.at[index, 'Organization Name'] = None
        df.at[index, 'Organization Title'] = None
        # Example placeholder value
        df.at[index, 'Organization Department'] = None
        df.at[index, 'Birthday'] = None  # Example placeholder value
        df.at[index, 'Notes'] = name
        df.at[index, 'Photo'] = None  # Example placeholder value
        # Example placeholder value'
        df.at[index, 'Labels'] = '[24-25] ' + input_file_name + ' ::: * myContacts'
        df.at[index, 'E-mail 1 - Label'] = '*'   # Example placeholder value
        df.at[index, 'E-mail 1 - Value'] = email
        df.at[index, 'Phone 1 - Label'] = None  # Example placeholder value
        df.at[index, 'Phone 1 - Value'] = phone

    # Write the formatted DataFrame to a new CSV file
    df.to_csv(output_file, index=False)


if __name__ == "__main__":
    directory = ''  # Replace with your directory path
    try:
        # Automatically find the CSV file
        input_file = find_csv_file(directory)
        input_file_name = input_file[:-4]
        output_file = os.path.join(directory, input_file_name + '-Formatted.csv')

        # Call the function to format the CSV file
        format_csv(input_file, output_file, input_file_name)

        print(f"Processing completed. Output saved to {output_file}")
    except FileNotFoundError as e:
        print(e)
