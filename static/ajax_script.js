$(document).ready(function() {
    var data = parseInt($('#UpdateForm').data('entry'))
    $('#AddForm').on('submit', function(event) {
        event.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/add',
            data: $('#AddForm').serialize(),
            success: function(result){
            $('.list-head').prepend(result);
            }
        });
    });
    console.log(data);
    $('#UpdateForm').on('submit', function(event) {
        event.preventDefault();
        $.ajax({
            type: 'POST',
            url: '/entry/edit/'+data,
            data: $('#UpdateForm').serialize(),
            success: function(result){
            $('.entry').html(result);
            }               
        });
    });
});
