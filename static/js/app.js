$(function() {
    $('#submit').click(function() {
        event.preventDefault();
        var form_data = new FormData($('#uploadform')[0]);
        $.ajax({
            type: 'POST',
            url: '/uploadajax',
            data: form_data,
            contentType: false,
            processData: false,
            dataType: 'json'
        }).done(function(data, textStatus, jqXHR){
            console.log(data);
            console.log(textStatus);
            console.log(jqXHR);
            console.log('Success!');
            $("#resultFilename").text(data['name']);
            $("#resultFilesize").text(data['size']);
            $("#resultFilespath").text(data['downloadpath']);
            $("#download_link").attr("href", "download/"+data['name']);
            alert("please click download button")

        }).fail(function(data){
            alert('error!');
        });
    });

});