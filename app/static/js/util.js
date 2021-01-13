// This file contains utility functions


/**
 * Show a floating notification on screen.
 *
 * Default timeout is 10 seconds.
 *
 * @param type message type (success, warning, etc.)
 * @param message message to show
 * @param timeout timeout for the message in milliseconds
 */
function showNotification(type, message, timeout) {
  if (typeof timeout === 'undefined') {
    timeout = 10000;
  }

  var params = {
    type: type,
    text: message,
    timeout: timeout
  };

  new Noty(params).show();
}


/**
 * Toggle navbar burger in mobile.
 */
function toggleBurger(e) {
  e.preventDefault();

  var $target = $('#' + $(this).data('target'));

  if ($target.length === 0) {
    return;
  }

  $(this).toggleClass('is-active');
  $target.toggleClass('is-active');
}


/**
 * Toggle navbar dropdown.
 */
function toggleNavbarDropdown(e) {
  e.preventDefault();

  $(this).closest('.has-dropdown').toggleClass('is-active');
}
