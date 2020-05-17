$(function() {
    $('#submit').click(function() {
        event.preventDefault();
        var form_data = new FormData($('#uploadform')[0]);
        alert("please wait for some time")
        $("#overlay").show();
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
            $("#download_link").attr("href", "download/"+data['downloadpath']);
            var file_name = data['downloadpath']
            $("#download_button").append("<a id='download_link' href='download/"+file_name+"' >download here</a>");
            $("#overlay").hide();
            alert("please click download button")

        }).fail(function(data){
            alert('error!');
            $("#overlay").hide();

        });
    });

});