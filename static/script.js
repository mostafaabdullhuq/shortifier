

//special characters that allowed in password
let SPECIAL_CHARS = "/[!@#$%^&*()_+-=[]{};:\\|,.<>/?]+/",

    // email validation regex
    EMAILREGEX = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,

    // url validation regex
    URLREGEX = /[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/;

// function to validate password requirements
function passWordValidation(passWord, passWordConfirmation) {

    // if password is not the same as password confirmation
    if (passWord !== passWordConfirmation) 
    {
        return false;
    }

    // if password length is less than 12 characters or bigger than 20 characters
    if (passWord.length < 12 || passWord.length > 20)
    {
        return false;
    }

    // initialize variables to track requirements
    let isSpecialChar = false,
        isUpper = false,
        isDigit = false;

    // check password characters requirements
    for (let eachChar of passWord)
    {

        // if current character is a space
        if (eachChar === " ")
        {
            return false;
        }

        // if current character is uppercase
        if (eachChar === eachChar.toUpperCase())
        {
            isUpper = true;
        }

        // if current character is a special character
        if (SPECIAL_CHARS.includes(eachChar)) {
            isSpecialChar = true;
        }

        // if current character is a digit
        if (eachChar >= '0' && eachChar <= '9')
        {
            isDigit = true;
        }
    }

    // if all requirements are met
    if (isSpecialChar && isUpper && isDigit) {
        return true;
    } 

    // if requirements not met
    else {
        return false;
    }
}

// function to validate registeration inputs
function inputValidation(firstName, lastName, userName, emailAddress, passWord, passWordConfirmation)
{

    // if any input is empty
    if (! firstName || ! lastName || ! userName || ! emailAddress || ! passWord || ! passWordConfirmation || firstName == "" || lastName == "" || userName == ""  || emailAddress == "" || passWord == "" || passWordConfirmation == "")
    {

        // show alert to user
        Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Please fill all fields!",
        });
        return false;
    }

    // validate username

    // check for special characters in username
    for (let eachChar of userName)
    {

        // if the current character is a special character
        if (SPECIAL_CHARS.includes(eachChar))
        {

            // show alert to user
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Invalid username!",
            });
            return false;
        }
    }

    // validate email address

    // if user email input doesn't matche the email regex
    if (! emailAddress.match(EMAILREGEX)) {

        // show alert to user
        Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Invalid email address!",
        });
        return false;
    }

    // validate password and password confirmation

    // if password doesn't meet the requirements
    if (! passWordValidation(passWord, passWordConfirmation))
    {

        // show alert to user
        Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Password doesn't meet the requirements!",
        });
        return false;
    }

    // if all user inputs is valid
    return true;
}


// when document ready
$(document).ready(function () {

    // when registeration button is clicked
    $("button.register-submit").click(function () {

        // get user inputs
        let firstName = $("input.reg-firstName").val().trim(),
            lastName = $("input.reg-lastName").val().trim(),
            userName = $("input.reg-username").val().trim(),
            emailAddress = $("input.reg-email").val().trim(),
            passWord = $("input.reg-password").val().trim(),
            passWordConfirmation = $("input.reg-passwordConfirmation").val();

        // validate user inputs
        if (inputValidation(firstName, lastName, userName, emailAddress, passWord, passWordConfirmation))
        {
            // initialize registeration post data
            let registerPostData = {
                firstName: firstName,
                lastName: lastName,
                userName: userName,
                emailAddress: emailAddress,
                passWord: passWord,
                passWordConfirmation: passWordConfirmation,
            };

            // make ajax request to /register route
            $.ajax({
                type: "POST",
                url: "/register",
                data: registerPostData,
                success: function (response) {

                    // if registeration successful
                    if (response.code === 200) {

                        // redirect user to the home page
                        window.location.href = "/";
                    
                    // if error happends in registeration process
                    } else {

                        // show alert to user
                        Swal.fire({
                            icon: "error",
                            title: "Oops...",
                            text: response.message,
                        });
                    }
                },
            });
        }
    });


    // when login button is clicked
    $("button.login-submit").click(function () {

        // get user inputs
        let userIdentifier = $("input.login-identifier").val(),
            passWord = $("input.login-password").val();

        // if any input is empty
        if (! userIdentifier || ! passWord || userIdentifier === "" || passWord === "") 
        {

            // show alert to user
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Please fill all fields.",
            });
        }

        // if all inputs is filled
        else
        {

            // initialize login post data
            let loginPostData = {
                identifier: userIdentifier,
                passWord: passWord
            };

            // make ajax request to /login route
            $.ajax({
                type: "POST",
                url: "/login",
                data: loginPostData,
                success: function (response) {

                    // if login process is success
                    if (response.code === 200) {

                        // redirect user to home page
                        window.location.href = '/'

                    // if error happends in login process
                    } else {

                        // show alert to user
                        Swal.fire({
                            icon: "error",
                            title: "Oops...",
                            text: response.message,
                        });
                    }
                },
            });
        }
    });


    // when setting's change api key button is clicked
    $("button.settings-generate-new-key").click(function () {

        // make ajax request to /api/change_key route
        $.ajax({
            type: "GET",
            url: "/api/change_key",
            success: function (response) {

                // if changing api key process is success
                if (response.code === 200) {

                    // change the api input value to the new api key value
                    $("input.settings-api-key").val(response.data.api_key);

                // if error happends in chaning api key process
                } else {

                    // show alert to user
                    Swal.fire({
                        icon: "error",
                        title: "Oops...",
                        text: response.message,
                    });
                }
            },
        });
    });


    // when update profile button is clicked
    $("button.update-profile-submit").click(function () 
    {

        // get all inputs values
        let firstName = $("input.settings-first-name").val(),
            lastName = $("input.settings-last-name").val(),
            userName = $("input.settings-username").val(),
            emailAddress = $("input.settings-email-address").val(),

            // initialize update profile post data
            updatePostData = {
            first_name: firstName,
            last_name: lastName,
            username: userName,
            email_address: emailAddress,
        };

        // if user email doesn't matche the email regex
        if (!emailAddress.match(EMAILREGEX)) {

            // show alert to user
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Invalid email address!",
            });
        } else {

            // send ajax request to /api/update_profile route
            $.ajax({
                type: "POST",
                url: "/api/update_profile",
                data: updatePostData,
                success: function (response) {
                    if (response.code === 200) {

                        // if update profile process is success, show success alert to user
                        Swal.fire("", `Your profile has been updated successfully.`, "success");
                    } else {

                        // if error happends during update profile process, show error alert to user
                        Swal.fire({
                            icon: "error",
                            title: "Oops...",
                            text: response.message,
                        });
                    }
                },
            });
        }
    });


    // when change password button is clicked
    $("button.update-password-submit").click(function () {

        // get the inputs values
        let newPassword = $("input.settings-new-password").val(),
            newPassWordConfirmation = $("input.settings-new-password-confirmation").val(),

            // initialize change password post data
            updatePasswordData = {
                current_password: $("input.settings-current-password").val(),
                new_password: newPassword,
                new_password_confirmation: newPassWordConfirmation,
            };

        // if new password doesn't meet the password requirements
        if (! passWordValidation(newPassword, newPassWordConfirmation)) {
            Swal.fire({

                // show error alert to user
                icon: "error",
                title: "Oops...",
                text: "Password doesn't meet the requirements.",
            });
        }

        // if new password meet the requirements
        else {

            // send ajax request to /api/change_password route
            $.ajax({
                type: "POST",
                url: "/api/change_password",
                data: updatePasswordData,
                success: function (response) {
                    if (response.code === 200) {

                        // if change password process is success, show success alert to user
                        Swal.fire("", `Your password has been updated successfully.`, "success");
                    } else {

                        // if error happends in chaning password process, show error alert to user
                        Swal.fire({
                            icon: "error",
                            title: "Oops...",
                            text: response.message,
                        });
                    }
                },
            });
        }
    });


    // when shorten url button is clicked
    $("button.shorten-submit").click(function() {

        // get the url input value
        let url = $("input.full-url").val(),

            // get the result container section
            resultContainer = $("section.shorten-result-container"),

            // initialize shorten url post data
            shortenPostData = {
                url: url,
            };

        // if url input is empty or url doesn't match the url validation regex
        if (!url || url === "" || !url.match(URLREGEX)) {

            // show error alert to user
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Please enter valid URL.",
            });
        }

        // if url is valid
        else {

            // send ajax request to /api/shorten_url route
            $.ajax({
                type: "POST",
                url: "/api/shorten",
                data: shortenPostData,
                success: function (response) {
                    if (response.code === 200) {

                        // if url shortened successfully

                        // initialize a variable that equal the shortened url full value
                        let shortenURL = window.location.host + "/" + response.data.shortened_url_id;

                        // update the text of the h5 that contains the result shortened url
                        $("h5.result-url-text").text(shortenURL);

                        // update the hidden input that contains the shortened url id
                        $("input.shorten_url_id").val(response.data.url_id);

                        // show the result url container by animation
                        resultContainer.fadeIn();

                    // if error happends in shortening url process
                    } else {

                        // hide the result container container in animation
                        resultContainer.fadeOut();

                        // show error alert to user
                        Swal.fire({
                            icon: "error",
                            title: "Oops...",
                            text: response.message,
                        });
                    }
                },
            });
        }
    });


    // when edit url button is clicked
    $("button.edit-url-submit").click(function() {

        // get the clicked button hidden input sibling that contains the shortened url id
        let urlIDContainerInput = $(this).siblings("input.shorten_url_id"),

            // get the h5 that contains the shortened url that needs to be edited ( if the edit url button is in the home page)
            indexResultContainer = $(urlIDContainerInput).siblings("div.result-url-container").children("h5.result-url-text"),

            // get the paragraph that contains the shortened url that needs to be edited (if the edit url button is in the dashboard page)
            dashboardResultContainer = $(urlIDContainerInput).parent("div.controls-container").siblings("p.dashboard-result-url-text");

            // get the id of the url that needs to be edited
            urlID = urlIDContainerInput.val(),

            // initialize check url post data
            checkURLPostData = {
                url_id: urlID,
            };

            // send ajax request to /api/check_edit_url route
            $.ajax({
                type: "POST",
                url: "/api/check_edit_url",
                data: checkURLPostData,
                success: function (response) {
                    if (response.code === 200) {

                        // if url is valid and exists in database, show alert to user that contains input to enter the new url
                        Swal.fire({
                            title: "Enter New URL",
                            input: "text",
                            inputAttributes: {
                                autocapitalize: "off",
                            },
                            showCancelButton: true,
                            confirmButtonText: "Change",
                        }).then((userResponse) => {
                            
                            // when user enter the new url and click on confirm button

                            // get the new url value
                            let newURL = userResponse.value,

                                // initialize the edit url post data
                                editURLPostData = {
                                    new_url: newURL,
                                    url_id: urlID,
                                };

                            // send ajax request to /api/edit_url route
                            $.ajax({
                                type: "POST",
                                url: "/api/edit_url",
                                data: editURLPostData,
                                success: function (response) {
                                    if (response.code === 200) {

                                        // if the url changed successfully

                                        // get the full new url
                                        let newFullURL = "https://" + window.location.host + "/" + newURL;

                                        // if the edit url process is in the home page
                                        if (indexResultContainer.length > 0) {

                                            // change the result url container h5 value to the new url
                                            indexResultContainer.text(newFullURL);

                                            // show success alert to user
                                            Swal.fire("", `URL has been updated successfully.`, "success");
                                        }

                                        // if the edit url process is in the dashboard page
                                        else {

                                            // change the result url container paragraph value to the new url
                                            dashboardResultContainer.text(newFullURL);

                                            // show success alert to user
                                            Swal.fire("", `URL has been updated successfully.`, "success");
                                        }
                                    } 
                                    else {

                                        // if any error happends while changing url process, show error alert to user
                                        Swal.fire({
                                            icon: "error",
                                            title: "Oops...",
                                            text: response.message,
                                        });
                                    }
                                },
                            });
                        });
                    } else {

                        // if any error happends while checking for url, show error alert to user
                        Swal.fire({
                            icon: "error",
                            title: "Oops...",
                            text: response.message,
                        });
                    }
                },
            });
    });



    // when delete url button is clicked
    $("button.delete-url-submit").click(function () {

        // get the clicked button url id
        let urlID = $(this).siblings("input.shorten_url_id").val(),

            // get the container of the current url
            urlContainer = $(this).parent("div.controls-container").parent("div.card-body").parent("div.shorten-item"),

            // initialize delete url post data
            deletePostData = {
                url_id: urlID
            };

        // send ajax request to /api/delete_url route
        $.ajax({
            type: "POST",
            url: "/api/delete_url",
            data: deletePostData,
            success: function (response) {
                if (response.code === 200) {

                    // if url deleted successfully, remove the url card from the dashboard with animation
                    urlContainer.fadeOut();
                } else {

                    // if any error occurs during deletion process, show error alert to user
                    Swal.fire({
                        icon: "error",
                        title: "Oops...",
                        text: response.message,
                    });
                }
            },
        });
    });
});