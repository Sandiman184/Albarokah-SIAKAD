$(document).ready(function() {
    console.log('Admin JS Loaded');
    
    // Sidebar toggle
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });

    // Initialize Summernote
    function initSummernote() {
        var $editors = $('.wysiwyg-editor');
        if ($editors.length > 0) {
            console.log('Found ' + $editors.length + ' editor(s)');
            
            $editors.each(function() {
                // Check if already initialized
                if ($(this).next('.note-editor').length > 0) {
                    console.log('Editor already initialized');
                    return;
                }

                $(this).summernote({
                    placeholder: 'Tulis konten di sini...',
                    tabsize: 2,
                    height: 400,
                    minHeight: 300,
                    dialogsInBody: true,
                    disableDragAndDrop: true,
                    shortcuts: false,
                    fontNames: ['Open Sans', 'Playfair Display', 'Cinzel', 'Nunito', 'Arial', 'Courier New'],
                    fontNamesIgnoreCheck: ['Open Sans', 'Playfair Display', 'Cinzel', 'Nunito'],
                    toolbar: [
                        ['style', ['style']],
                        ['font', ['bold', 'italic', 'underline', 'clear']],
                        ['fontname', ['fontname']],
                        ['fontsize', ['fontsize']],
                        ['color', ['color']],
                        ['para', ['ul', 'ol', 'paragraph', 'height']],
                        ['table', ['table']],
                        ['insert', ['link', 'picture', 'video', 'hr']],
                        ['view', ['fullscreen', 'codeview', 'help']]
                    ],
                    styleTags: [
                        'p', 
                        { title: 'Blockquote', tag: 'blockquote', className: 'blockquote', value: 'blockquote' },
                        'pre', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
                    ],
                    callbacks: {
                        onInit: function() {
                            console.log('Summernote initialized successfully');
                        }
                    }
                });
            });
        }
    }

    // Call initialization
    initSummernote();

    // Fallback: Try again after a short delay
    setTimeout(initSummernote, 1000);
});
