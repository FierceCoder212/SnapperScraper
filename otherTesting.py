import pandas as pd


def process_excel(file_path, sheet_name, column_names, sg_column):
    # Read the Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Check if the columns exist in the dataframe
    for column in column_names:
        if column not in df.columns:
            raise ValueError(
                f"Column '{column}' does not exist in the sheet '{sheet_name}'"
            )

    # Drop duplicate rows based on the specified columns
    df_no_duplicates = df.drop_duplicates(subset=column_names)

    # Reset the index of the dataframe to start from 0
    df_no_duplicates = df_no_duplicates.reset_index(drop=True)

    # Update the SGL codes to be sequential
    sg_prefix = df_no_duplicates[sg_column].iloc[0][:8]
    df_no_duplicates[sg_column] = [
        f"{sg_prefix}{str(i).zfill(7)}" for i in range(1, len(df_no_duplicates) + 1)
    ]

    return df_no_duplicates


# Example usage
file_path = "ModelList.xlsx"  # Path to your Excel file
sheet_name = "Sheet1"  # Name of the sheet
column_names = [
    "Manufacturer",
    "Model",
    "Unique Product Code",
]  # List of column names to check for repeating data
sg_column = "SGL Code"  # Column name for the SGL codes

processed_data = process_excel(file_path, sheet_name, column_names, sg_column)

# Save the processed data to a new Excel file
output_file_path = "processed_data.xlsx"
processed_data.to_excel(output_file_path, index=False)

print(f"Processed data saved to {output_file_path}")


# Data to check to confirm duplicate removal
# 7085921 - LBC6151BV, 6 HP 15" Classic Walk Behind Leaf Blower Series 1
