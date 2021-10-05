const SECRET_SHOW_DURATION_SECONDS = 10;

$(".secret-button").click(function () {
    const secretButton = $(this);
    const secretId = secretButton.data("secret-id");
    const secret = $(`#${secretId}`);
    secret.removeClass("display-none");
    secretButton.addClass("display-none");
    setTimeout(() => {
        secret.addClass("display-none");
        secretButton.removeClass("display-none");
    }, SECRET_SHOW_DURATION_SECONDS * 1000);
});

$(".secret-close-button").click(function () {
    const secretCloseButton = $(this);
    const secretCloseId = secretCloseButton.data("secret-id");
    const secretButton = $(`#${"button-"+secretCloseId}`);
    const secret = $(`#${secretCloseId}`);
    secret.addClass("display-none");
    secretButton.removeClass("display-none");
});
