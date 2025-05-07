// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })

    // Enable Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    })

    // Auto-dismiss alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert-dismissible')
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert)
            bsAlert.close()
        }, 5000)
    })

    // Add active class to current nav link
    var currentPath = window.location.pathname
    var navLinks = document.querySelectorAll('.navbar-nav .nav-link')
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active')
            link.setAttribute('aria-current', 'page')
        }
    })
})

// AJAX add to cart functionality
function addToCart(productId) {
    fetch(`/user/add-to-cart/${productId}`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart count in navbar
            document.querySelectorAll('.cart-count').forEach(el => {
                el.textContent = data.cart_count
            })

            // Show toast notification
            showToast(data.message, 'success')
        }
    })
    .catch(error => console.error('Error:', error))
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer()
    const toastId = 'toast-' + Date.now()

    const toast = document.createElement('div')
    toast.className = `toast align-items-center text-white bg-${type} border-0 show`
    toast.setAttribute('role', 'alert')
    toast.setAttribute('aria-live', 'assertive')
    toast.setAttribute('aria-atomic', 'true')
    toast.id = toastId

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto"
                    data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `

    toastContainer.appendChild(toast)

    // Auto-remove toast after 5 seconds
    setTimeout(() => {
        const bsToast = new bootstrap.Toast(toast)
        bsToast.hide()
        toast.addEventListener('hidden.bs.toast', function() {
            toast.remove()
        })
    }, 5000)
}

function createToastContainer() {
    const container = document.createElement('div')
    container.id = 'toast-container'
    container.className = 'position-fixed bottom-0 end-0 p-3'
    container.style.zIndex = '11'
    document.body.appendChild(container)
    return container
}