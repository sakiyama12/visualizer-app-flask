function formSwitch() {
    condition= document.getElementsByName('condition')
    if (condition[0].checked) {
        // 好きな食べ物が選択されたら下記を実行します
        document.getElementById('hist').style.display = "";
        document.getElementById('series').style.display = "none";
        document.getElementById('scatter').style.display = "none";
    } else if (condition[1].checked) {
        // 好きな場所が選択されたら下記を実行します
        document.getElementById('hist').style.display = "none";
        document.getElementById('series').style.display = "";
        document.getElementById('scatter').style.display = "none";
    } else if (condition[2].checked) {
        // 好きな場所が選択されたら下記を実行します
        document.getElementById('hist').style.display = "none";
        document.getElementById('series').style.display = "none";
        document.getElementById('scatter').style.display = "";
    } else {
        document.getElementById('hist').style.display = "none";
        document.getElementById('series').style.display = "none";
        document.getElementById('scatter').style.display = "none";
    }
}
window.addEventListener('/load', formSwitch());
