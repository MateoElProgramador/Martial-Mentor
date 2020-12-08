// Toggle background colour of body upon changing of chroma key checkbox:
$('#chroma_checkbox').change(function() {
      $('body').toggleClass('chromakey');
      $.post('/toggle_chromakey/', function(data) {

      });
});

$('.char_overlay_img').click(function() {
    $(this).toggleClass('grayscale');
});
