// This file contains navigation functions

/**
 * Load a page into the given container (usually a '.page-items' div).
 *
 * This is implemented as a standalone function in order to allow both
 * handlePagination() and sortList() functions to call it independently.
 *
 * @param $container - element that will contain the result (.page-items)
 * @param {String} link - link to fetch.
 */
function _loadPage($container, link) {
  if (!$container) {
    console.log('[ERROR] Container not found');
    return;
  }

  if (!link) {
    console.log('[ERROR] Link not specified');
    return;
  }

  $.ajax({
    url: link,
    type: 'GET',
    success: function(data) {
      // Update page
      $container.html(data);

      // Change URL
      window.history.pushState('', '', link);

      // Reattach events
      $container.find('.list-sorting').change(sortList);
      $container.find('.pagination-previous').click(handlePagination);
      $container.find('.pagination-next').click(handlePagination);
      $container.find('.pagination-link').click(handlePagination);

      // Scroll to the top of the container
      $('html, body').animate({
        scrollTop: $container.offset().top
      }, 0);
    },
    error: function(xhr, textStatus, errorThrown) {
      console.log('[ERROR] ' + xhr.responseText);
      showNotification('error', 'ERROR');
    }
  });
}


/**
 * Handle pagination with AJAX.
 *
 * This prevents a full page reload and simply fetches the partial template
 * for the page from the server in order to render it in the appropriate
 * '.page-items' element.
 *
 * Pagination controls are implemented using <a> tags.
 */
function handlePagination(e) {
  // Prevent reload
  e.preventDefault();

  var $container = $(this).closest('.page-items');
  var link = $(this).attr('href');

  _loadPage($container, link);
}
