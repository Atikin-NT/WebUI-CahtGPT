const fillDialogues = () => {
    $.ajax({
        type: 'GET',
        url: '/backend-api/conversations?offset=0&limit=20',
        data: null,
        success: function (data) {
            let html_data = '';
            for (let i = 0; i < data.total; i++) {
                title = data.items[i].title;
                let sliced_title = title.slice(0,42);
                if (sliced_title.length != title.length) sliced_title += "..";
                html_data += `
                <li><a href="#" onclick="getpopup(${data.items[i].id}, '${encodeURIComponent(title)}')" class="flex py-3 px-3 items-center gap-3 relative rounded-md cursor-pointer break-all pr-14 bg-gray-800 hover:bg-gray-800 group animate-flash">
                <div class="each-chat flex-grow-1 ms-3"><i class="fa-solid fa-comment"></i><p>${sliced_title}</p></div>
                </a></li>
                `;
            }
            $("#history-list-group").append(html_data);
        }
     });
}

const updateHistory = () => {
    newchathtml = `
    <li><a href="/chat" class="flex py-3 px-3 items-center gap-3 relative rounded-md cursor-pointer break-all pr-14 bg-gray-800 hover:bg-gray-800 group animate-flash">
    <div class="each-chat flex-grow-1 ms-3" style="display: flex; align-items: center;">
        <i class="fa-solid fa-plus"></i>
        <p>New chat</p>
    </div>
    </a></li>`
    $("#history-list-group").empty().append(newchathtml);
    fillDialogues();
}

const create_message = (message, imageSrc) => {
    return `
    <li class="custom-msg list-group-item list-group-item-action d-flex gap-3 py-3">
        <img src=${imageSrc} alt="twbs" width="32" height="32" class="rounded-circle flex-shrink-0">
        <div class="each-msg d-flex gap-2 w-100 justify-content-between markdownx">
        <div class="markdownx-preview">
            <p class="mb-0 opacity-75">${message}</p>
        </div>
        </div>
    </li>
    `;
}

$.ajaxSetup({
    data: {
        conv_id: null
    }
});

$("#gpt-button").click(function() {
    console.log("send mess");
    $(this).attr("disabled", true);
    var question = $("#chat-input").val();
    if (question.trim() === "") return;
    $("#chat-input").val('');

    let userImg = $("#user-img").attr("src");

    let html_data = create_message(question, userImg);
    $("#list-group").append(html_data);

    $.ajax({
        type: "POST",
        url: "/chat",
        data: {'prompt': question },
        success: function (data) {
            let gpt_data = create_message(data.answer, "static/images/gpt.png");
            $("#list-group").append(gpt_data);
            $.ajaxSetup({
                data: {
                    conv_id: data.conv_id
                }
            });
            updateHistory();
        },
        error: function (data) {
            let gpt_data = create_message(data.responseJSON.answer, "static/images/gpt.png");
            $("#list-group").append(gpt_data);
        }
    });
});

$("#chat-input").keyup(function() {
    var textareaVal = $(this).val();
    $("#gpt-button").attr("disabled", textareaVal.trim() === "");
})


function auto_grow(element) {
    element.style.height = "5px";
    element.style.height = (element.scrollHeight)+"px";
}

// from history.js
const getpopup = (id, title) => {
    document.activeElement.blur();
    $.ajax({
        type: "GET",
        url: `/backend-api/conversation/${id}`,
        data: null,
        success: function (data) {
            const decodedTitle = decodeURIComponent(title);
            let sliced_title = decodedTitle.slice(0, 60);
            if (sliced_title.length != decodedTitle.length) sliced_title += "..";
            const messages = data.messages;
            let userImg = $("#user-img").attr("src");
            $("#title").text(`${sliced_title}`);
            $("#list-group").empty();
            for (let message of messages) {
                role = message.role;
                content = message.content;
                if (role == 'user') img = userImg
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

 $(document).ready(function(){ fillDialogues(); });

