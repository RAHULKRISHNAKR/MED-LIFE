document.addEventListener("DOMContentLoaded", function() {
    // Smooth scrolling for navigation
    document.querySelectorAll(".navbar a").forEach(anchor => {
        anchor.addEventListener("click", function(event) {
            // Only apply smooth scrolling for anchors pointing to IDs on the page
            const href = this.getAttribute("href");
            if(href.startsWith('#')) {
                event.preventDefault();
                let targetId = href.substring(1);
                let targetElement = document.getElementById(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({ behavior: "smooth" });
                }
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
                    input.style.border = "2px solid #dc3545";
                    
                    // Create or update error message
                    let errorMsg = input.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('div');
                        errorMsg.classList.add('error-message');
                        errorMsg.style.color = "#dc3545";
                        errorMsg.style.fontSize = "12px";
                        errorMsg.style.marginTop = "5px";
                        input.parentNode.insertBefore(errorMsg, input.nextSibling);
                    }
                    errorMsg.textContent = "This field is required";
                } else {
                    input.style.border = "1px solid #ddd";
                    
                    // Remove error message if it exists
                    let errorMsg = input.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                    
                    // Email validation
                    if (input.type === 'email' && !isValidEmail(input.value)) {
                        isValid = false;
                        input.style.border = "2px solid #dc3545";
                        
                        let errorMsg = document.createElement('div');
                        errorMsg.classList.add('error-message');
                        errorMsg.style.color = "#dc3545";
                        errorMsg.style.fontSize = "12px";
                        errorMsg.style.marginTop = "5px";
                        errorMsg.textContent = "Please enter a valid email address";
                        input.parentNode.insertBefore(errorMsg, input.nextSibling);
                    }
                }
            });

            if (!isValid) {
                event.preventDefault();
            }
        });
    });

    // Fetch and display search results
    let searchForm = document.getElementById("searchForm");
    if (searchForm) {
        searchForm.addEventListener("submit", function(event) {
            const searchInput = document.getElementById('searchInput').value;

            if (!searchInput.trim()) {
                event.preventDefault(); // Prevent form submission
                alert('Please enter a search term.');
            }
            // Form will submit normally if search term is provided
        });
    }

    // Add animation effects to alert messages
    const alertMessages = document.querySelectorAll('.alert');
    alertMessages.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
    
    // Add focus effects to form inputs
    const formInputs = document.querySelectorAll('input, select');
    formInputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.style.borderColor = '#007bff';
            input.style.boxShadow = '0 0 0 2px rgba(0, 123, 255, 0.25)';
        });
        
        input.addEventListener('blur', () => {
            input.style.borderColor = '#ddd';
            input.style.boxShadow = 'none';
        });
    });
});

// Helper function to validate email format
function isValidEmail(email) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email);
}

function displayResults(results) {
    const resultsContainer = document.getElementById('search-results');
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = ''; // Clear previous results

    if (results.length === 0) {
        resultsContainer.innerHTML = '<p>No results found.</p>';
        return;
    }

    const list = document.createElement('ul');
    list.className = 'results-list';
    
    results.forEach(result => {
        const listItem = document.createElement('li');
        listItem.className = 'result-item';
        
        // Adjust based on your API response structure
        if (typeof result === 'string') {
            listItem.textContent = result;
        } else if (result.name) {
            listItem.textContent = result.name;
        } else {
            listItem.textContent = JSON.stringify(result);
        }
        
        list.appendChild(listItem);
    });

    resultsContainer.appendChild(list);
}