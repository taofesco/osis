function redirect_after_success(modal, xhr) {
    $(modal).modal('toggle');
    if (xhr.hasOwnProperty('success_url')) {
        window.location.href = xhr["success_url"];
    }
    else {
        window.location.reload();
    }
}

var formAjaxSubmit = function (form, modal) {
    $(form).submit(function (e) {
        // Added preventDefaut so as to not add anchor "href" to address bar
        e.preventDefault();

        $.ajax({
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function (xhr, ajaxOptions, thrownError) {

                //Stay on the form if there are errors.
                if ($(xhr).find('.has-error').length > 0) {
                    $(modal).find('.modal-content').html(xhr);
                    // Add compatibility with ckeditor and related textareas
                    bindTextArea();
                    formAjaxSubmit(form, modal);
                } else {
                    redirect_after_success(modal, xhr);
                }
            },
            error: function (xhr, ajaxOptions, thrownError) {
                // handle response errors here
            }
        });
    });
};


// CKEDITOR needs to dynamically bind the textareas during an XMLHttpRequest requests
function bindTextArea() {
    $("textarea[data-type='ckeditortype']").each( function () {
        CKEDITOR.replace($(this).attr('id'), $(this).data('config'));
    });
}

// Before submitting, we need to update textarea with ckeditor element.
function CKupdate(){
    for (let instance in CKEDITOR.instances )
        CKEDITOR.instances[instance].updateElement();
}

