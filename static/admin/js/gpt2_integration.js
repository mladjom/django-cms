if (typeof jQuery === 'undefined') {
    // Load jQuery if not already loaded
    var script = document.createElement('script');
    script.src = 'https://code.jquery.com/jquery-3.6.0.min.js';
    document.head.appendChild(script);
}

// Wait for both Django admin jQuery and regular jQuery
window.addEventListener('load', function() {
    (function($) {
        $(document).ready(function() {
            $('.gpt2-enhanced textarea, .gpt2-enhanced input[type="text"]').each(function() {
                var $field = $(this);
                var $button = $('<button type="button" class="gpt2-generate">Generate with AI</button>');
                var $spinner = $('<span class="gpt2-spinner" style="display:none;">Generating...</span>');
                
                $field.after($spinner);
                $field.after($button);
                
                $button.click(function(e) {
                    e.preventDefault();
                    
                    var $field = $(this).prev();
                    var fieldName = $field.attr('name');
                    var prompt = '';
                    
                    // Show spinner, disable button
                    $spinner.show();
                    $button.prop('disabled', true);
                    
                    // Field-specific settings
                    var maxLengths = {
                        'meta_description': 160,
                        'meta_title': 60,
                        'description': 500
                    };
                    
                    // Get base admin URL
                    var baseUrl = window.location.pathname.replace(/\/change\/?$/, '');
                    var generateUrl = baseUrl + '/generate-text/';
                    
                    // Get CSRF token from cookie
                    function getCookie(name) {
                        let cookieValue = null;
                        if (document.cookie && document.cookie !== '') {
                            const cookies = document.cookie.split(';');
                            for (let i = 0; i < cookies.length; i++) {
                                const cookie = cookies[i].trim();
                                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                    break;
                                }
                            }
                        }
                        return cookieValue;
                    }
                    
                    // Customize prompt based on field
                    if (fieldName === 'meta_description') {
                        prompt = 'Write a meta description for: ' + $('#id_title').val();
                    } else if (fieldName === 'meta_title') {
                        prompt = 'Write an SEO title for: ' + $('#id_title').val();
                    }
                    
                    $.ajax({
                        url: generateUrl,
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        data: {
                            prompt: prompt,
                            field: fieldName
                        },
                        success: function(response) {
                            if (response.text) {
                                var text = response.text.substring(0, maxLengths[fieldName] || 100);
                                $field.val(text);
                            }
                        },
                        error: function(xhr) {
                            if (xhr.status === 403) {
                                alert('Permission denied. Please ensure you are logged in with staff privileges.');
                            } else if (xhr.status === 401) {
                                alert('Your session has expired. Please refresh the page and try again.');
                                window.location.reload();
                            } else {
                                alert('Error generating text: ' + 
                                      (xhr.responseJSON?.error || 'Unknown error occurred'));
                            }
                        },
                        complete: function() {
                            $spinner.hide();
                            $button.prop('disabled', false);
                        }
                    });
                });
            });
        });
    })(window.django ? django.jQuery : jQuery);
    });