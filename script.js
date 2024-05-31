document.addEventListener('DOMContentLoaded', () =>
{
    rerender()
})

function round(number)
{
    return Math.round(number * 100) / 100
}

function rerender()
{
    const tree = document.getElementById("tree-container");
    const amount = parseInt(document.getElementById("global-modifier").value);
    tree.innerHTML = '';

    fetch('file.json')
        .then(response => response.json())
        .then(data =>
            {
                const treeContainer = document.getElementById('tree-container');
                renderTree(data, treeContainer, amount)
            }
        )
}

function renderTree(data, container, modifier) {
    data["chems"].forEach(element => {
        const outer = document.createElement('div');
        outer.className = 'outer';

        const thing = document.createElement('div');
        thing.className = 'tree-item';
        thing.textContent = "> " + element["name"] + " " + (element["amount"] * modifier).toFixed(0);
        thing.id = element["name"]
        
        // Create a container for the nested tree
        const nestedContainer = document.createElement('div');
        nestedContainer.className = 'nested-tree';
        nestedContainer.style.display = 'none'; // Initially hidden
        
        // Add click event to toggle visibility
        thing.addEventListener('click', () => {
   
            const isHidden = nestedContainer.style.display === 'none';

            nestedContainer.style.display = isHidden ? 'block' : 'none';
        
            if (isHidden) 
            {
                thing.style.backgroundColor = '#940000'; // Open trees will have red background
            } 
            else 
            {
                thing.style.backgroundColor = ''; // Reset background color when hidden
            }
        });


        outer.appendChild(thing);
        outer.appendChild(nestedContainer);

        container.appendChild(outer);

        // Render the nested tree if there are reactants
        if (element.reactants && element.reactants.length > 0) {
            renderNestedTree(element.reactants, nestedContainer, modifier);
        }
    });
}

function renderNestedTree(reactants, container, modifier) {
    reactants.forEach(reactant => {
        const reactantItem = document.createElement('div');
        reactantItem.className = 'tree-item';
        reactantItem.id = reactant["name"].replace(/\s+/g, '-').toLowerCase(); // Set the ID
        
        // Create a link to this reactant IF it's not a base
        if(reactant["type"] == "base")
        {
            reactantItem.className = reactantItem.className + " base"
            reactantItem.textContent = reactant["name"] + " " + round(reactant["amount"] * modifier).toFixed(1);
        }
        else
            reactantItem.textContent = "> " +  reactant["name"] + " " + round(reactant["amount"] * modifier).toFixed(1);

        // Create a container for the nested reactant tree
        const nestedReactantContainer = document.createElement('div');
        nestedReactantContainer.className = 'nested-tree';
        nestedReactantContainer.style.display = 'none'; // Initially hidden
        
        // Add click event to toggle visibility
        reactantItem.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent event bubbling
            const isHidden = nestedReactantContainer.style.display === 'none';
            nestedReactantContainer.style.display = isHidden ? 'block' : 'none';
            
            if(reactant["type"] == "base") return;
            if (isHidden) 
            {
                reactantItem.style.backgroundColor = '#940000'; // Open trees will have red background
            } 
            else 
            {
                reactantItem.style.backgroundColor = ''; // Reset background color when hidden
            }
        });

        container.appendChild(reactantItem);
        container.appendChild(nestedReactantContainer);

        // Recursively render the nested reactant tree
        if (reactant.reactants && reactant.reactants.length > 0) {
            renderNestedTree(reactant.reactants, nestedReactantContainer, modifier);
        }
    });
}
