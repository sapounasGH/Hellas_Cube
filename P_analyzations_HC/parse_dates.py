from datetime import parser

def convert_date(date_str: str, output_format: str = "%d-%m-%Y") -> str:
    return parser.parse(date_str).strftime(output_format)