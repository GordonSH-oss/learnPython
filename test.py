colors=['red', 'green', 'blue', 'yellow', 'purple', 'orange']
sizes=['S', 'M', 'L', 'XL', 'XXL', 'XXXL']
tshirts=[(color,size) for color in colors for size in sizes]
tshirts_dict={color:size for color,size in tshirts}
print(tshirts_dict)