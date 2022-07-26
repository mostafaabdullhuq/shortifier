
let SPECIAL_CHARS = "/[!@#$%^&*()_+\-=\[\]{};:\\|,.<>\/?]+/",
    EMAILREGEX = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/;

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
    if (! firstName || ! lastName || ! userName || ! emailAddress || ! passWord || ! passWordConfirmation || firstName == "" || lastName == "" || userName == ""  || emailAddress == "" || passWord == "" || passWordConfirmation == "" )
    {
        Swal.fire("Please fill all fields!");
        return false;
    }

    // validate username

    // check for special characters in username
    for (let eachChar of userName)
    {
        if (SPECIAL_CHARS.includes(eachChar))
        {
            Swal.fire("Invalid username!");
            return false;
        }
    }

    // validate email address

    // if user email input matches the email regex
    if (! emailAddress.match(EMAILREGEX)) {
        Swal.fire("Invalid email address!");
        return false;
    }

    if (! passWordValidation(passWord, passWordConfirmation))
    {
        Swal.fire("Password doesn't meet the requirements!");
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
            let postData = {
                        "firstName":firstName,
                        "lastName":lastName,
                        "userName":userName,
                        "emailAddress":emailAddress,
                        "passWord":passWord,
                        "passWordConfirmation":passWordConfirmation
                    }

            console.log(postData);
            $.ajax({
                type:"POST",
                url: "/register",
                data: postData
                ,
                success: function (response) {
                    if (response.code === 200) {
                        Swal.fire(
                        `Welcome, ${userName}!`,
                        'Your account created successfully, Please check email for activation message.',
                        'success'
                        )
                    }
                    else
                    {
                        Swal.fire({
                        icon: 'error',
                        title: 'Oops...',
                        text: response.message,
                        })
                    }
                    console.log(response);
                },
            });
        }
    });
});


