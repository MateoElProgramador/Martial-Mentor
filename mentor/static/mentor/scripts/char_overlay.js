$('body').toggleClass('chromakey')

// Toggle background colour of body upon changing of chroma key checkbox:
$('#chroma_checkbox').change(function() {
      $('body').toggleClass('chromakey');
    });
