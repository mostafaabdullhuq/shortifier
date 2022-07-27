
let SPECIAL_CHARS = "/[!@#$%^&*()_+-=[]{};:\\|,.<>/?]+/",
    EMAILREGEX = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

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


function inputValidation(firstName, lastName, userName, emailAddress, passWord, passWordConfirmation)
{
    // if any input is empty
    if (! firstName || ! lastName || ! userName || ! emailAddress || ! passWord || ! passWordConfirmation || firstName == "" || lastName == "" || userName == ""  || emailAddress == "" || passWord == "" || passWordConfirmation == "")
    {
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
        if (SPECIAL_CHARS.includes(eachChar))
        {
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Invalid username!",
            });
            return false;
        }
    }

    // validate email address

    // if user email input matches the email regex
    if (! emailAddress.match(EMAILREGEX)) {
        Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Invalid email address!",
        });
        return false;
    }

    if (! passWordValidation(passWord, passWordConfirmation))
    {
        Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Password doesn't meet the requirements!",
        });
        return false;
    }
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
            // make ajax request to /register route
            let registerPostData = {
                        "firstName":firstName,
                        "lastName":lastName,
                        "userName":userName,
                        "emailAddress":emailAddress,
                        "passWord":passWord,
                        "passWordConfirmation":passWordConfirmation
                    }

            $.ajax({
                type: "POST",
                url: "/register",
                data: registerPostData,
                success: function (response) {
                    if (response.code === 200) {
                        Swal.fire(
                                "",
                                `Welcome, ${userName}!`, "Your account created successfully, Please check email for activation message.",
                                "success"
                                );
                    } else {
                        Swal.fire({
                            icon: "error",
                            title: "Oops...",
                            text: response.message,
                        });
                    }
                    console.log(response);
                },
            });
        }
    });


    // when login button is clicked
    $("button.login-submit").click(function () {
        let userIdentifier = $("input.login-identifier").val(),
            passWord = $("input.login-password").val();

        if (! userIdentifier || ! passWord || userIdentifier === "" || passWord === "") 
        {
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Please fill all fields.",
            });

        }
        else
        {
            let loginPostData = {
                identifier: userIdentifier,
                passWord: passWord
            };
            $.ajax({
                type: "POST",
                url: "/login",
                data: loginPostData,
                success: function (response) {
                    if (response.code === 200) {
                        window.location.href = '/'
                    } else {
                        Swal.fire({
                            icon: "error",
                            title: "Oops...",
                            text: response.message,
                        });
                    }
                    console.log(response);
                },
            });
        }
    });


    // when settings change api key button is clicked
    $("button.settings-generate-new-key").click(function () {
        $.ajax({
            type: "GET",
            url: "/api/change_key",
            success: function (response) {
                if (response.code === 200) {
                    $("input.settings-api-key").val(response.data.api_key);
                } else {
                    Swal.fire({
                        icon: "error",
                        title: "Oops...",
                        text: response.message,
                    });
                }
                console.log(response);
            },
        });
    });



    // when update profile button is clicked
    $("button.update-profile-submit").click(function () 
    {
        // get inputs values
        let updatePostData = {
            first_name: $("input.settings-first-name").val(),
            last_name: $("input.settings-last-name").val(),
            username: $("input.settings-username").val(),
            email_address: $("input.settings-email-address").val(),
        };

        // if user email input matches the email regex
        if (!emailAddress.match(EMAILREGEX)) {
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Invalid email address!",
            });
        }
        else {
            $.ajax({
                type: "POST",
                url: "/api/update_profile",
                data: updatePostData,
                success: function (response) {
                    if (response.code === 200) {
                        Swal.fire("", `Your profile has been updated successfully.`, "success");
                    } else {
                        Swal.fire({
                            icon: "error",
                            title: "Oops...",
                            text: response.message,
                        });
                    }
                    console.log(response);
                },
            });
        }
    });

    // when change password button is clicked
    $("button.update-password-submit").click(function () {
        let newPassword = $("input.settings-new-password").val(),
            newPassWordConfirmation = $("input.settings-new-password-confirmation").val(),
            updatePasswordData = {
                current_password: $("input.settings-current-password").val(),
                new_password: newPassword,
                new_password_confirmation: newPassWordConfirmation,
            };

        if (! passWordValidation(newPassword, newPassWordConfirmation)) {
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Password doesn't meet the requirements.",
            });
        }
        else {
            $.ajax({
                type: "POST",
                url: "/api/change_password",
                data: updatePasswordData,
                success: function (response) {
                    if (response.code === 200) {
                        Swal.fire("", `Your password has been updated successfully.`, "success");
                    } else {
                        Swal.fire({
                            icon: "error",
                            title: "Oops...",
                            text: response.message,
                        });
                    }
                    console.log(response);
                },
            });
        }

    });
// end document ready
});