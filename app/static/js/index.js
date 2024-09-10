$('#btn').click(function () {
        var postId = window.location.pathname.split('/')[2];
        $.ajax({
            url: '/post/' + postId + '/add-comment',
            type: 'POST',
            dataType: 'json',
            data: {
                'content': $('#comment_content').val()
            },
            success: function (data) {
                $('#comments-block').append('<p>' + data.new_comment + '</p>');
                $('#comment_content').val('');
            },
        });
    });

$('#submitPost').click(function() {
    console.log('Button clicked'); // Додаємо цей рядок для перевірки
    var formData = new FormData($('#postForm')[0]);

    $.ajax({
        url: '/add-post',
        type: 'POST',
        data: formData,
        contentType: false,
        processData: false,
        success: function(response) {
            window.location.href = '/';
        },
        error: function(response) {
            alert('Error: ' + response.responseText);
        }
    });
});

$('#btn_back').click(function () {
        window.location.href = '/';
    });