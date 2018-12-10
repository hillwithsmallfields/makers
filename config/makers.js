function toggle_visibility(id) {
    var e = document.getElementById(id); if(e.style.display == 'block') e.style.display = 'none'; else e.style.display = 'block';
}

// from https://www.w3schools.com/howto/howto_js_tabs.asp with slight modification
function openTab(evt, tabName) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
} 

function openLazyTab(evt, tabName, tabContentsUrl) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Load and show the current tab, and add an "active" class to the button that opened the tab
    $(tabName).load(tabContentsUrl);
    // document.getElementById(tabName).style.display = "block";
    $(tabName).style.display = "block";
    evt.currentTarget.className += " active";
} 


function selectTab(initialTabButton) {
    document.getElementById(initialTabButton).click();
}
