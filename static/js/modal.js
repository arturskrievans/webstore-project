document.addEventListener("DOMContentLoaded", function() {

    const modal = document.getElementById("myModal");
    const modalImg = document.getElementById("img01");

    const images = document.querySelectorAll("img");

    images.forEach(image => {
        image.onclick = function() {
            modal.style.display = "block";
            modalImg.src = this.src;
        };
        const span = document.getElementsByClassName("close")[0];
        span.onclick = function() {
            modal.style.display = "none";
        };
    });

});