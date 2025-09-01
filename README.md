# HSPICE-to-Histogram

This code is designed to extract numerical results (e.g., Monte Carlo simulation results, power traces, ...) from HSPICE simulation output files (`.lis`) and visualize them as **histograms**.
It is especially useful for analyzing parameters such as power, current, and delay.

---

## 🚀 How to Run

1. Open your HSPICE output file (`.lis`) and save it in text format (`.txt`).

2. Copy the `.txt` file to the project folder. (Easiest way)

3. run main.py

---

## 📈 Output

* The script shows the results as a **histogram** using matplotlib.


## 🔍 Notes

* If the data values include different units (e.g., µW, pW, mW), the tool automatically converts them to a common base unit (according to user’s choice) before normalization. This ensures that values are comparable on the same scale.
* Supported prefixes: `f, p, n, u, m, k, M, G`
* You can extend the `common_patterns` list in the code to add more custom patterns.
