/* These variables must be defined when linking this script */
// noinspection ES6ConvertVarToLetConst
var requestedUserPK;

$(".tabular.menu .item").tab();

const $userDropdown = $("#user").parent();
$userDropdown.dropdown({
    fullTextSearch: true,
    forceSelection: true,
    onChange: function (userPK, text, $choice) {
        $.ajax(`${LANG_PREFIX}/reservation/quota/user/${userPK}/`, {
            success: function (data, textStatus) {
                $("#user-quotas").html(data);
                setupDeleteModal();
            },
        });
    },
});
if (requestedUserPK)
    $userDropdown.dropdown("set selected", requestedUserPK);
