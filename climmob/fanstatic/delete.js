function showDelete (url,text, csrf, where = '') {
    swal({
            title: "Are you sure?",
            text: text,
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Yes, delete it!",
            cancelButtonText: "No, cancel!",
            closeOnConfirm: false,
            closeOnCancel: false
        },
        function (isConfirm) {
            if (isConfirm) {

                $.ajax({
                    url: url,
                    datatype: "json",
                    type: "POST",
                    data: {"csrf_token": csrf},
                    success: function(respuesta) {
                        if (where != 'noRedirect') {
                            if (where == '') {
                                location.href = window.location.href;
                            } else {
                                location.href = where;
                            }
                        }else{
                            swal.close()
                        }
                    },
                    error: function(respuesta) {
                        swal("Cancelled", "The information could not be deleted.", "error");
                    }
                });

            } else {
                swal("Cancelled", "We have not deleted the data", "error");
            }
        });
}