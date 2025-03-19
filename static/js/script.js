document.addEventListener("DOMContentLoaded", function() {
    // Smooth scrolling for navigation
    document.querySelectorAll(".nav-links a").forEach(anchor => {
        anchor.addEventListener("click", function(event) {
            event.preventDefault();
            let targetId = this.getAttribute("href").substring(1);
            let targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: "smooth" });
            }
        });
    });

    // Form validation
    document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", function(event) {
            let inputs = this.querySelectorAll("input[required]");
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.border = "2px solid red";
                } else {
                    input.style.border = "1px solid #ccc";
                }
            });

            if (!isValid) {
                event.preventDefault();
                alert("Please fill in all fields.");
            }
        });
    });

    // Fetch and display search results
    let searchForm = document.getElementById("searchForm");
    if (searchForm) {
        searchForm.addEventListener("submit", async function(event) {
            event.preventDefault(); // Prevent the form from refreshing the page

            const searchType = document.getElementById('search-type').value;
            const searchInput = document.getElementById('searchInput').value;

            if (!searchInput.trim()) {
                alert('Please enter a search term.');
                return;
            }

            try {
                const response = await fetch(`/search?type=${searchType}&query=${encodeURIComponent(searchInput)}`);
                if (!response.ok) {
                    throw new Error('Failed to fetch search results.');
                }

                const results = await response.json();
                displayResults(results);
            } catch (error) {
                console.error(error);
                alert('An error occurred while searching. Please try again.');
            }
        });
    }
});

function displayResults(results) {
    const resultsContainer = document.getElementById('search-results');
    resultsContainer.innerHTML = ''; // Clear previous results

    if (results.length === 0) {
        resultsContainer.innerHTML = '<p>No results found.</p>';
        return;
    }

    const list = document.createElement('ul');
    results.forEach(result => {
        const listItem = document.createElement('li');
        listItem.textContent = result.name; // Adjust based on your API response structure
        list.appendChild(listItem);
    });

    resultsContainer.appendChild(list);
}
