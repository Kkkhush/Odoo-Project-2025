// Clothing Swap Platform JavaScript

$(document).ready(function() {
    
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Item request form toggle
    $('input[name="request_type"]').change(function() {
        var requestType = $(this).val();
        if (requestType === 'swap') {
            $('#swap_section').show();
            $('#points_section').hide();
            $('#offered_item_id').prop('required', true);
            $('#points_used').prop('required', false);
        } else if (requestType === 'points') {
            $('#swap_section').hide();
            $('#points_section').show();
            $('#offered_item_id').prop('required', false);
            $('#points_used').prop('required', true);
        }
    });
    
    // Form validation
    $('#requestForm').submit(function(e) {
        var requestType = $('input[name="request_type"]:checked').val();
        
        if (requestType === 'swap') {
            var offeredItemId = $('#offered_item_id').val();
            if (!offeredItemId) {
                e.preventDefault();
                alert('Please select an item to offer for swap.');
                return false;
            }
        } else if (requestType === 'points') {
            var pointsUsed = parseInt($('#points_used').val());
            var userBalance = parseInt($('#points_used').data('balance') || 0);
            
            if (pointsUsed > userBalance) {
                e.preventDefault();
                alert('You don\'t have enough points for this redemption.');
                return false;
            }
        }
    });
    
    // Image preview for add item form
    $('#image').change(function(e) {
        var file = e.target.files[0];
        if (file) {
            var reader = new FileReader();
            reader.onload = function(e) {
                $('#image-preview').remove();
                $('#image').after('<div id="image-preview" class="mt-2"><img src="' + e.target.result + '" class="img-fluid rounded" style="max-width: 200px; max-height: 200px;"></div>');
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Filter form auto-submit with delay
    var filterTimeout;
    $('.filter-input').on('input', function() {
        clearTimeout(filterTimeout);
        filterTimeout = setTimeout(function() {
            $('#filterForm').submit();
        }, 1000);
    });
    
    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(event) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000);
        }
    });
    
    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        var imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    var img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(function(img) {
            imageObserver.observe(img);
        });
    }
    
    // Points balance animation
    $('.points-balance').each(function() {
        var $this = $(this);
        var countTo = parseInt($this.text());
        
        $({ countNum: 0 }).animate({
            countNum: countTo
        }, {
            duration: 2000,
            easing: 'linear',
            step: function() {
                $this.text(Math.floor(this.countNum));
            },
            complete: function() {
                $this.text(countTo);
            }
        });
    });
    
    // Request status updates (for real-time updates)
    function updateRequestStatus() {
        $('.request-status').each(function() {
            var $status = $(this);
            var requestId = $status.data('request-id');
            
            // You could implement real-time status updates here
            // using WebSocket or periodic AJAX calls
        });
    }
    
    // Initialize status updates
    setInterval(updateRequestStatus, 30000); // Update every 30 seconds
    
    // Confirmation dialogs
    $('.btn-danger').click(function(e) {
        if (!confirm('Are you sure you want to perform this action?')) {
            e.preventDefault();
        }
    });
    
    // Auto-hide alerts
    $('.alert').each(function() {
        var $alert = $(this);
        setTimeout(function() {
            $alert.fadeOut();
        }, 5000);
    });
    
    // Search functionality
    $('#searchInput').on('input', function() {
        var searchTerm = $(this).val().toLowerCase();
        $('.searchable-item').each(function() {
            var itemText = $(this).text().toLowerCase();
            if (itemText.includes(searchTerm)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
    
    // Modal handling for item details
    $('.item-modal-trigger').click(function(e) {
        e.preventDefault();
        var itemId = $(this).data('item-id');
        
        // Load item details via AJAX
        $.get('/api/item/' + itemId, function(data) {
            $('#itemModal').html(data).modal('show');
        });
    });
    
    // Infinite scroll for browse page
    if ($('.infinite-scroll').length) {
        var loading = false;
        var page = 2;
        
        $(window).scroll(function() {
            if ($(window).scrollTop() + $(window).height() >= $(document).height() - 1000 && !loading) {
                loading = true;
                $('.loading-spinner').show();
                
                $.get(window.location.pathname + '?page=' + page, function(data) {
                    $('.items-container').append($(data).find('.item-card'));
                    page++;
                    loading = false;
                    $('.loading-spinner').hide();
                });
            }
        });
    }
    
});

// Utility functions
function showNotification(message, type = 'info') {
    var alertClass = 'alert-' + type;
    var notification = $('<div class="alert ' + alertClass + ' alert-dismissible fade show" role="alert">' +
        message +
        '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
        '</div>');
    
    $('#notifications').prepend(notification);
    
    setTimeout(function() {
        notification.fadeOut();
    }, 5000);
}

function formatPoints(points) {
    return points.toLocaleString() + ' pts';
}

function timeAgo(dateString) {
    var date = new Date(dateString);
    var now = new Date();
    var diffInSeconds = (now - date) / 1000;
    
    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return Math.floor(diffInSeconds / 60) + ' minutes ago';
    if (diffInSeconds < 86400) return Math.floor(diffInSeconds / 3600) + ' hours ago';
    return Math.floor(diffInSeconds / 86400) + ' days ago';
}
