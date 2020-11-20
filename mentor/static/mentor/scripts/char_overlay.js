// Get csrf token from DOM:
var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();

// --- Ensure csrf token is sent along with any Ajax request: ---
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// Toggle background colour of body upon changing of chroma key checkbox:
$('#chroma_checkbox').change(function() {
      $('body').toggleClass('chromakey');
      $.post('/toggle_chromakey/', function(data) {

      });
});
