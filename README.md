# Purple Donkey: The Housing Lock-in Paradox

**AI Models Used:** Gemini and Claude

## The Insight
Financial markets operate on established rules: when the cost of borrowing skyrockets, asset prices fall. However, recent data from FRED reveals a complete breakdown of this rule in the U.S. housing market. The Federal Reserve's rate hikes accidentally destroyed housing *supply* faster than they destroyed *demand*, keeping prices at record highs.

Please find the PDF analysis and generated charts in this repository.

## How to Run This Code Locally

This project uses `pyfredapi` to pull live data from the Federal Reserve Economic Data (FRED) API. 

1. **Clone the repository and set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
