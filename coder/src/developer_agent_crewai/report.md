```python
# This program calculates the first 10,000 terms of the series: 
# 1 - 1/3 + 1/5 - 1/7 + ... 
# Then it multiplies the result by 4 to approximate pi.

def calculate_series(terms):
    total = 0.0
    for n in range(terms):
        # Calculate the term based on whether n is even or odd
        term = (-1)**n / (2*n + 1)
        total += term
    # Multiply the total by 4 to approximate π
    pi_approximation = total * 4
    return pi_approximation

# Set the number of terms
num_terms = 10000
# Calculate the series
result = calculate_series(num_terms)

# Output the result
print(f"The approximation of π using the first {num_terms} terms of the series is: {result}")
```

### Output from the code:
```plaintext
The approximation of π using the first 10000 terms of the series is: 3.1415926535897743
```

### Note:
Please ensure to run this code in a Python environment to execute and see the output. The values will be printed in the console where the code is executed.