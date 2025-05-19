import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

dataset = pd.read_csv('dataset.csv')

if 'Runs' in dataset.columns:
    runs_per_batsman = dataset.groupby('Batsman')['Runs'].sum().reset_index()
    if not runs_per_batsman.empty:
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Batsman', y='Runs', data=runs_per_batsman)
        plt.title('Runs by Batsman')
        plt.xlabel('Batsman')
        plt.ylabel('Runs')
        plt.tight_layout()
        plt.savefig('output.png')
        
        print(runs_per_batsman.nlargest(1, 'Runs'))
else:
    print("Column 'Runs' not found in dataset.")