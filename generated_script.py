```
import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv('dataset.csv')

# Group by Country and sum Production (Tons) for each country
country_production = df.groupby('Country')['Production (Tons)'].sum().reset_index()

# Sort the countries by production in descending order
country_production.sort_values(by='Production (Tons)', ascending=False, inplace=True)

# Plot a bar chart to show which country produces more
plt.figure(figsize=(10,6))
plt.bar(country_production['Country'], country_production['Production (Tons)'])
plt.xlabel('Country')
plt.ylabel('Production (Tons)')
plt.title('Top Countries by Production')
plt.show()
```