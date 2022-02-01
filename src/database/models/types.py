from pydantic import condecimal

Money = condecimal(max_digits=10, decimal_places=2)