// This file contains initializers defined in other JS files and must
// be imported last.


$(document).ready(function() {
  // Preprocess AJAX
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      // Allow backend to detect AJAX requests
      xhr.setRequestHeader('X-WITH-AJAX', 'true');

      // Add CSRF token (needs to be included in template)
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
        var $csrf = $('meta[name=csrf-token]');

        if ($csrf.length === 0) {
          // Missing CSRF token
          console.log('[ERROR] Missing CSRF meta tag');
          showNotification('error', 'ERROR - CSRF');

        } else {
          xhr.setRequestHeader('X-CSRFToken', $csrf.attr('content'));
        }
      }
    }
  });

  // Navbar
  $('.navbar-burger').click(toggleBurger);
  $('.has-dropdown > .navbar-link').click(toggleNavbarDropdown);

  // Pagination
  $('.pagination-previous').click(handlePagination);
  $('.pagination-next').click(handlePagination);
  $('.pagination-link').click(handlePagination);
});
