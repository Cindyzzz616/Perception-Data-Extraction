import csv
import sys

import unicodedata
import re

def _clean_text(value: str) -> str:
    """Normalize text while preserving accents/diacritics and handling HTML.

    - Normalizes to NFC form for consistent display.
    - Strips control characters except tab/newline/carriage return.
    - Converts simple HTML tags to markdown equivalents:
        * <b>bold</b> → **bold**
        * <i>italic</i> → *italic*
      and removes other tags entirely.

    This allows bold/italic formatting to survive while removing raw tags
    that would otherwise clutter the CSV cells.
    """
    if not isinstance(value, str):
        return value
    # first, convert known HTML tags to markdown equivalents
    text = value
    # <b> or <strong> => bold
    text = re.sub(r'<\s*(?:b|strong)\s*>(.*?)<\s*/\s*(?:b|strong)\s*>', r'**\1**', text, flags=re.IGNORECASE)
    # <i> or <em> => italic
    text = re.sub(r'<\s*(?:i|em)\s*>(.*?)<\s*/\s*(?:i|em)\s*>', r'*\1*', text, flags=re.IGNORECASE)
    # optionally handle <u> as underline (could convert to markdown _text_?)
    text = re.sub(r'<\s*u\s*>(.*?)<\s*/\s*u\s*>', r'_\1_', text, flags=re.IGNORECASE)
    # remove any other tags
    text = re.sub(r'<[^>]+>', '', text)
    # normalize to composed form (NFC) which is standard for display
    normalized = unicodedata.normalize('NFC', text)
    # remove control characters except for tab/newline/carriage return
    return ''.join(ch for ch in normalized if ch.isprintable() or ch in '\t\n\r')


def filter_csv_columns(input_file, output_file, columns):
    """
    Read a CSV file and write a new CSV with only the specified column indices.
    
    Args:
        input_file: Path to the input CSV file
        output_file: Path to the output CSV file
        columns: List of integer indices of columns to include (0-based)
    
    The first row of the input is treated as a header; the same header values
    for the selected indices will be written to the output file.  All field
    values are cleaned via ``_clean_text`` to strip weird symbols or accented
    characters.
    """
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # read header row if present
            try:
                header = next(reader)
            except StopIteration:
                # empty file
                print(f"Error: '{input_file}' is empty.")
                return
            # select header columns by index, ignoring out-of-range indices
            selected_header = [header[i] for i in columns if 0 <= i < len(header)]
            writer.writerow(selected_header)

            for row in reader:
                filtered_row = [row[i] for i in columns if 0 <= i < len(row)]
                # clean each cell
                cleaned = [_clean_text(cell) for cell in filtered_row]
                writer.writerow(cleaned)
        
        print(f"Successfully wrote filtered CSV to {output_file}")
    
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Example usage (select by index)
    input_csv = "Download_raw_Feb24-2026-NewNewprotocol_10participants/data_exp_258706-v2_questionnaire-6fz5.csv"
    output_csv = "output/questionnaire_output.csv"
    # indices corresponding to requested columns
    # F,I,L,M,O,AC,AD,AE,AF,AG,AH,AI,AM,AO,AP,AQ,AR,AS,AT,AU,AV,AW,AX,AY,AZ,
    # BA,BB,BC,BD,BE,BF,BG,BI,BJ,BL,BM,BN,BP,BS,BT,BU,BV,BW
    columns_to_keep = [5, 8, 11, 12, 14, 28, 29, 30, 31, 32, 33, 34, 38, 40, 41,
                       42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55,
                       56, 57, 58, 60, 61, 63, 64, 65, 67, 70, 71, 72, 73, 74]
    
    filter_csv_columns(input_csv, output_csv, columns_to_keep)