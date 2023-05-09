const create_message = (message, imageSrc) => {
    return `
    <a href="#" class="custom-msg list-group-item list-group-item-action d-flex gap-3 py-3">
        <img src=${imageSrc} alt="twbs" width="32" height="32" class="rounded-circle flex-shrink-0">
        <div class="each-msg d-flex gap-2 w-100 justify-content-between">
        <div>
            <p class="mb-0 opacity-75">${message}</p>
        </div>
        </div>
    </a>
    `;
}

$.ajaxSetup({
    data: {
        conv_id: null
    }
});

$("#gpt-button").click(function() {
    var question = $("#chat-input").val();
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
        }
    });
});