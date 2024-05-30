document.addEventListener('DOMContentLoaded', () =>
{
    fetch('file.json')
        .then(response => response.json())
        .then(data =>
            {
                const treeContainer = document.getElementById('tree-container');
                renderTree(data, treeContainer)
                console.log(data)
            }
        )
})

function renderTree(data, container) {
    data["chems"].forEach(element => {
        const thing = document.createElement('div')
        thing.textContent = element["name"]
        container.appendChild(thing)    
    });
}