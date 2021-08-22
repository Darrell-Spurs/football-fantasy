function finalizeLogin(res,db_data){
    // async function add_to_db(){
    //     await db.collection('users').doc(db_data.email).set(db_data)
    //     console.log(db_data)
    // }
    // add_to_db();
    res.user.getIdToken().then(IdToken=>{
        const data =  {
            "id_token": IdToken,
            "db_data": db_data
        };
        axios
            .post("/login",data)
            .then(res=>{
                console.log("Login Succesful",res);
                window.location = "/";
            })
            .catch(err=>{
                console.log("Login Error",err.response)
            });
    });
}



$("#login-form").submit(function(event){
    event.preventDefault();
    const form = {
        email: $("#email").val(),
        password: $("#password").val(),
    };
    console.log("[Log In]",form);
    firebase.auth()
            .signInWithEmailAndPassword(form.email,form.password)
            .then(res=>{
                console.log("Login Request Successful",res);
                finalizeLogin(res,"Login");
            })
            .catch(err=>{
                console.log("Login Request Error",err)
                alert(err.message);
            })
});


$("#signup-form").submit(function(event){
    event.preventDefault();
    const form = {
        email: $("#email").val().toLowerCase(),
        username: $("#username").val(),
        password: $("#password").val(),
    };
    const db_data = {
        email: $("#email").val().toLowerCase(),
        username: $("#username").val(),
        fav_nation: $("#fav_nation").val(),
        fav_club: $("#fav_club").val(),
        leagues: []
    };
    console.log("[Sign Up]",form);
    firebase.auth()
            .createUserWithEmailAndPassword(form.email,form.password)
            .then(res=>{
                console.log("Sign Up Successful",res);
                console.log(db_data);
                finalizeLogin(res,db_data);
            })
            .catch(err=>{
                console.log("Sign Up Error",err)
                alert(err.message);
            })
});
