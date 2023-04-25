const getpopup = (id) => {
    $.ajax({
        type: "GET",
        url: `/backend-api/conversation/${id}`,
        success: function (data) {
            title = data.title;
            messages = data.messages;
            $("#title").text(title);
            $("#list-group").empty();
            for (let message of messages) {
                role = message.role;
                content = message.content;
                if (role == 'user') img = "static/images/favicon.png"
                else img = "static/images/gpt.png"
                html_data = create_message(content, img);
                $("#list-group").append(html_data);
            }
        }
    });
    $.ajaxSetup({
        data: {
            conv_id: id
        }
    });
}

$.ajax({
    type: 'GET',
    url: '/backend-api/conversations?offset=0&limit=20',
    success: function (data) {
        console.log(data)
        let html_data = '';
        for (let i = 0; i < data.total; i++) {
            html_data += `
            <a href="#" onclick="getpopup(${data.items[i].id})" class="flex py-3 px-3 items-center gap-3 relative rounded-md cursor-pointer break-all pr-14 bg-gray-800 hover:bg-gray-800 group animate-flash">
            <div class="flex-1 text-ellipsis max-h-5 overflow-hidden break-all relative">${data.items[i].id}</div>
            </a>
            `;
        }
        $("#history-list-group").append(html_data);
    }
 });

